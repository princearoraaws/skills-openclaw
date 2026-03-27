import * as fs from "node:fs";
import * as path from "node:path";

const handler = async (event: any) => {
  // Only handle agent:bootstrap events
  if (event.type !== "agent" || event.action !== "bootstrap") {
    return;
  }

  const sessionKey = event.sessionKey;
  const workspaceDir = event.context?.workspaceDir;
  if (!sessionKey || !workspaceDir) return;

  const previewPath = path.join(workspaceDir, "previews", `${sessionKey}.md`);

  if (!fs.existsSync(previewPath)) {
    return;
  }

  try {
    const content = fs.readFileSync(previewPath, "utf-8");

    const statusMatch = content.match(/##\s*状态[\r\n]+(\S+)/i);
    if (!statusMatch || statusMatch[1].toLowerCase() !== "pending") {
      return;
    }

    const summaryMatch = content.match(/##\s*本次 session 摘要[\r\n]+([\s\S]*?)(?=##|$)/i);
    const itemsMatch = content.match(/##\s*未完成事项[\r\n]+([\s\S]*?)(?=##|$)/i);
    const nextStepMatch = content.match(/##\s*醒来后第一步[\r\n]+([\s\S]*?)(?=##|$)/i);
    const contextMatch = content.match(/##\s*关键上下文[\r\n]+([\s\S]*?)(?=##|$)/i);

    const summary = summaryMatch ? summaryMatch[1].trim() : "（无）";
    const items = itemsMatch ? itemsMatch[1].trim() : "（无）";
    const nextStep = nextStepMatch ? nextStepMatch[1].trim() : "（无）";
    const context = contextMatch ? contextMatch[1].trim() : "（无）";

    const message = [
      "🌙 检测到上次 session 有未完成事项，恢复上下文：",
      "",
      `**上次 session 摘要**：${summary}`,
      "",
      `**未完成事项**：${items}`,
      "",
      `**醒来后第一步**：${nextStep}`,
      "",
      `**关键上下文**：${context}`,
      "",
      "请根据上述信息，继续处理未完成的事项。",
    ].join("\n");

    event.messages.push(message);
  } catch (err) {
    console.error("[session-sleep-wake] Error reading preview:", err);
  }
};

export default handler;
