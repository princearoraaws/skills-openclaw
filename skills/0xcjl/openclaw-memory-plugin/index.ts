/**
 * index.ts — OpenClaw Memory System Plugin
 *
 * Registers memory management tools that wrap the Python/bash memory scripts.
 * This plugin provides:
 *   - memory_recall    : Recall relevant memories before a task
 *   - memory_save      : Save task output to memory after completion
 *   - memory_search    : Search memories by keyword
 *   - memory_build     : Rebuild all memory indexes
 *   - memory_dag_link  : Link two memory entries in the DAG
 *
 * Zero external Python dependencies — uses only stdlib.
 */

import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { execFileSync, spawnSync } from "child_process";
import { resolve } from "path";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk/types";

const __dirname = import.meta.dirname!;
const SCRIPTS_DIR = resolve(__dirname, "scripts");

// ─── Config helpers ───────────────────────────────────────────────────────────

function getWorkspaceRoot(api: OpenClawPluginApi): string {
  const cfg = api.getConfig?.() ?? {};
  return (
    cfg.workspaceRoot ??
    `${process.env.HOME}/.openclaw/workspace-dev`
  );
}

function getAgentId(api: OpenClawPluginApi): string {
  const cfg = api.getConfig?.() ?? {};
  return cfg.agentId ?? "dev";
}

function getTopN(api: OpenClawPluginApi): number {
  const cfg = api.getConfig?.() ?? {};
  return cfg.topN ?? 3;
}

// ─── Script runners ───────────────────────────────────────────────────────────

function runPython(script: string, args: string[]): string {
  const result = spawnSync("python3", [script, ...args], {
    encoding: "utf-8",
    timeout: 10_000,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(`Script exited ${result.status}: ${result.stderr}`);
  }
  return result.stdout;
}

function runBash(script: string, args: string[]): string {
  const result = spawnSync("bash", [script, ...args], {
    encoding: "utf-8",
    timeout: 10_000,
  });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(`Script exited ${result.status}: ${result.stderr}`);
  }
  return result.stdout;
}

// ─── Tool definitions ─────────────────────────────────────────────────────────

export default definePluginEntry({
  id: "openclaw-memory-system",
  name: "OpenClaw Memory System",
  description:
    "Persistent memory for OpenClaw agents — BM25 recall, keyword indexing, DAG linking, and session hooks.",

  register(api: OpenClawPluginApi) {
    const scripts = SCRIPTS_DIR;

    // ── memory_recall ─────────────────────────────────────────────────────────
    api.registerTool(
      {
        name: "memory_recall",
        description:
          "Recall relevant memories before starting a task. " +
          "Uses hybrid BM25 + keyword search over the local memory index. " +
          "Performance target: < 500ms. " +
          "Returns top-N relevant memory entries sorted by combined score.",
        parameters: {
          type: "object",
          properties: {
            task: {
              type: "string",
              description:
                "Natural language description of the current task. " +
                "Used as the search query for memory recall.",
            },
            top: {
              type: "number",
              description:
                "Number of memories to return (default: 3, max: 10).",
            },
          },
          required: ["task"],
        },
      },
      { optional: false },
    );

    // Register the implementation after both declarations above
    api.registerToolHandler(
      "memory_recall",
      async (_id, params: { task: string; top?: number }) => {
        const topN = params.top ?? getTopN(api);
        const agentId = getAgentId(api);
        const indexer = `${scripts}/memory-indexer.py`;
        const bm25 = `${scripts}/bm25_search.py`;

        let output = "";

        // Try BM25 first (more semantic)
        try {
          output = runPython(bm25, [
            "--search", params.task,
            "--agent-id", agentId,
            "--top", String(topN),
            "--json",
          ]);
          if (output.trim()) {
            const parsed = JSON.parse(output);
            if (Array.isArray(parsed) && parsed.length > 0) {
              return {
                content: [
                  {
                    type: "text",
                    text: formatRecallOutput(parsed, params.task),
                  },
                ],
              };
            }
          }
        } catch {
          // fall through to keyword search
        }

        // Fall back to keyword indexer
        try {
          output = runPython(indexer, [
            "search", params.task,
            "--agent-id", agentId,
            "--top", String(topN),
            "--json",
          ]);
          if (output.trim()) {
            const parsed = JSON.parse(output);
            return {
              content: [
                {
                  type: "text",
                  text: formatRecallOutput(parsed, params.task),
                },
              ],
            };
          }
        } catch (e) {
          return {
            content: [{ type: "text", text: `(No memories found for: ${params.task})` }],
          };
        }

        return {
          content: [{ type: "text", text: `(No memories found for: ${params.task})` }],
        };
      },
    );

    // ── memory_save ───────────────────────────────────────────────────────────
    api.registerTool(
      {
        name: "memory_save",
        description:
          "Save a completed task output to the memory store. " +
          "Writes a dated markdown file under memory/YYYY-MM-DD/ and " +
          "triggers async index rebuild (WAL snapshot).",
        parameters: {
          type: "object",
          properties: {
            task: {
              type: "string",
              description: "Brief description of the task that was completed.",
            },
            result: {
              type: "string",
              description:
                "Task result or key output to store. " +
                "Can be a summary or full result text.",
            },
          },
          required: ["task"],
        },
      },
      { optional: false },
    );

    api.registerToolHandler("memory_save", async (_id, params: { task: string; result?: string }) => {
      const agentId = getAgentId(api);
      const hook = `${scripts}/memory-hook.sh`;

      const args = ["after-task", params.task];
      if (params.result) {
        // Write result to temp file and pass path
        const tmp = `/tmp/openclaw-memory-result-${Date.now()}.txt`;
        await Bun.write(tmp, params.result);
        args.push(tmp);
      }

      const output = runBash(hook, args);
      return {
        content: [{ type: "text", text: output || "Memory saved successfully." }],
      };
    });

    // ── memory_search ────────────────────────────────────────────────────────
    api.registerTool(
      {
        name: "memory_search",
        description:
          "Full-text search over the memory store using BM25 ranking. " +
          "Returns ranked entries with scores, summaries, and shared flags.",
        parameters: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Search query string.",
            },
            top: {
              type: "number",
              description: "Number of results to return (default: 3).",
            },
            includeShared: {
              type: "boolean",
              description: "Include memories from other agents (default: true).",
            },
          },
          required: ["query"],
        },
      },
      { optional: false },
    );

    api.registerToolHandler(
      "memory_search",
      async (_id, params: { query: string; top?: number; includeShared?: boolean }) => {
        const topN = params.top ?? getTopN(api);
        const agentId = getAgentId(api);
        const includeShared = params.includeShared ?? true;
        const bm25 = `${scripts}/bm25_search.py`;

        const args = [
          "--search", params.query,
          "--agent-id", agentId,
          "--top", String(topN),
          "--json",
        ];
        if (!includeShared) args.push("--no-shared");

        const output = runPython(bm25, args);
        try {
          const parsed = JSON.parse(output);
          return {
            content: [
              {
                type: "text",
                text: formatSearchOutput(parsed),
              },
            ],
          };
        } catch {
          return { content: [{ type: "text", text: output || "No results." }] };
        }
      },
    );

    // ── memory_build ─────────────────────────────────────────────────────────
    api.registerTool(
      {
        name: "memory_build",
        description:
          "Rebuild all memory indexes: keyword index (memory-indexer.py) " +
          "and BM25 index (bm25_search.py). Also updates the WAL state file. " +
          "Call this after bulk memory writes.",
        parameters: {
          type: "object",
          properties: {
            agentId: {
              type: "string",
              description: "Agent ID to build index for (default: current agent).",
            },
          },
        },
      },
      { optional: false },
    );

    api.registerToolHandler(
      "memory_build",
      async (_id, params: { agentId?: string }) => {
        const agent = params.agentId ?? getAgentId(api);
        const wal = `${scripts}/wal-snapshot.sh`;
        const output = runBash(wal, ["rebuild"]);
        return {
          content: [{ type: "text", text: output || "Indexes rebuilt." }],
        };
      },
    );

    // ── memory_dag_link ──────────────────────────────────────────────────────
    api.registerTool(
      {
        name: "memory_dag_link",
        description:
          "Record a directed link between two memory entries in the DAG. " +
          "Used to build associative memory graphs for later traversal.",
        parameters: {
          type: "object",
          properties: {
            fromId: {
              type: "string",
              description: "Source memory entry ID.",
            },
            toId: {
              type: "string",
              description: "Target memory entry ID (the linked memory).",
            },
            reason: {
              type: "string",
              description: "Reason or context for the link.",
            },
          },
          required: ["fromId", "toId"],
        },
      },
      { optional: false },
    );

    api.registerToolHandler(
      "memory_dag_link",
      async (_id, params: { fromId: string; toId: string; reason?: string }) => {
        const agentId = getAgentId(api);
        const hook = `${scripts}/memory-hook.sh`;
        const args = ["dag-link", params.fromId, params.toId];
        if (params.reason) args.push(params.reason);
        const output = runBash(hook, args);
        return {
          content: [{ type: "text", text: output || "DAG link recorded." }],
        };
      },
    );
  },
});

// ─── Output formatters ─────────────────────────────────────────────────────────

function formatRecallOutput(entries: any[], query: string): string {
  if (!entries.length) return `No memories found for: ${query}`;
  const lines = [`## Memory Recall: "${query}"\n`];
  entries.forEach((e, i) => {
    const shared = e.shared ? " **[shared]**" : "";
    lines.push(`${i + 1}. **${e.file}**${shared} (weight: ${e.weight ?? "?"})`);
    lines.push(`   ${(e.summary || "").slice(0, 150)}`);
    lines.push("");
  });
  return lines.join("\n");
}

function formatSearchOutput(entries: any[]): string {
  if (!entries.length) return "No results.";
  const lines: string[] = [];
  entries.forEach((e, i) => {
    lines.push(
      `${i + 1}. **${e.file}** — bm25=${e.bm25?.toFixed(3)} combined=${e.combined?.toFixed(3)}`,
    );
    lines.push(`   ${(e.summary || "").slice(0, 120)}`);
    lines.push("");
  });
  return lines.join("\n");
}
