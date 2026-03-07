#!/usr/bin/env node
const BASE = "https://api.wise.com";
const token = process.env.WISE_API_TOKEN;
if (!token) throw new Error("Missing WISE_API_TOKEN");

const [,, cmd, ...args] = process.argv;
const rawOutput = args.includes("--raw");

const getArg = (name) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : undefined;
};

const SENSITIVE_KEYS = new Set([
  "firstName",
  "lastName",
  "dateOfBirth",
  "phoneNumber",
  "avatar",
  "email",
  "address",
  "firstNameInKana",
  "lastNameInKana"
]);

const LOCALIZED_SENSITIVE_KEYS = new Set(["firstName", "lastName", "firstNameInKana", "lastNameInKana"]);

function redactValue(value) {
  if (Array.isArray(value)) return value.map(redactValue);
  if (!value || typeof value !== "object") return value;

  const out = {};
  for (const [k, v] of Object.entries(value)) {
    if (SENSITIVE_KEYS.has(k)) {
      out[k] = "[REDACTED]";
      continue;
    }

    if (
      k === "localizedInformation" &&
      Array.isArray(v)
    ) {
      out[k] = v.map((entry) => {
        if (entry && typeof entry === "object" && LOCALIZED_SENSITIVE_KEYS.has(String(entry.key))) {
          return { ...entry, value: "[REDACTED]" };
        }
        return redactValue(entry);
      });
      continue;
    }

    out[k] = redactValue(v);
  }
  return out;
}

function errorSummary(status, text) {
  try {
    const parsed = JSON.parse(text);
    const msg = parsed?.message || parsed?.error || "request failed";
    return `Wise API ${status}: ${msg}`;
  } catch {
    return `Wise API ${status}: request failed`;
  }
}

async function apiGet(path, params = {}) {
  const url = new URL(BASE + path);
  Object.entries(params).forEach(([k, v]) => v != null && url.searchParams.set(k, String(v)));

  const r = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json"
    }
  });

  const text = await r.text();
  if (!r.ok) throw new Error(errorSummary(r.status, text));
  return text ? JSON.parse(text) : null;
}

function printJson(value, { redact = false } = {}) {
  const out = redact && !rawOutput ? redactValue(value) : value;
  console.log(JSON.stringify(out));
}

switch (cmd) {
  case "list_profiles": {
    const data = await apiGet("/v1/profiles");
    printJson(data, { redact: true });
    break;
  }

  case "get_profile": {
    const id = Number(getArg("--profile-id"));
    if (!id) throw new Error("Missing --profile-id");
    const all = await apiGet("/v1/profiles");
    const found = all.find((p) => Number(p?.id) === id);
    if (!found) throw new Error(`Profile not found: ${id}`);
    printJson(found, { redact: true });
    break;
  }

  case "list_balances": {
    const id = Number(getArg("--profile-id"));
    if (!id) throw new Error("Missing --profile-id");
    const data = await apiGet(`/v4/profiles/${id}/balances`, { types: "STANDARD" });
    printJson(data);
    break;
  }

  case "get_exchange_rate": {
    const source = (getArg("--source") || "").toUpperCase();
    const target = (getArg("--target") || "").toUpperCase();
    if (!source || !target) throw new Error("Missing --source/--target");
    const data = await apiGet("/v1/rates", { source, target });
    printJson(data);
    break;
  }

  default:
    throw new Error(
      "Usage: wise_readonly.mjs <list_profiles|get_profile|list_balances|get_exchange_rate> [--raw] ..."
    );
}
