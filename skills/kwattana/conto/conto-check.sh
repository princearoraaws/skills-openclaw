#!/usr/bin/env bash
# conto-check.sh — Conto policy check & management helper for OpenClaw
#
# Payment commands (standard SDK key):
#   conto-check.sh approve <amount> <recipient> <sender> [purpose] [category] [chain_id]
#   conto-check.sh confirm <approval_id> <tx_hash> <approval_token>
#   conto-check.sh x402 <amount> <recipient> <resource_url> [facilitator] [scheme]
#   conto-check.sh budget
#   conto-check.sh services
#
# Policy commands (requires admin SDK key):
#   conto-check.sh policies
#   conto-check.sh policy <id>
#   conto-check.sh create-policy <json_body>
#   conto-check.sh update-policy <id> <json_body>
#   conto-check.sh delete-policy <id>
#   conto-check.sh get-rules <policy_id>
#   conto-check.sh set-rules <policy_id> <json_body>
#   conto-check.sh add-rule <policy_id> <json_body>
#   conto-check.sh delete-rule <policy_id> <rule_id>

set -euo pipefail

# Require bash (script uses bash-specific features)
[[ -n "${BASH_VERSION:-}" ]] || { echo '{"error": true, "message": "This script requires bash"}' >&2; exit 1; }

# Require jq for safe JSON construction
command -v jq >/dev/null 2>&1 || { echo '{"error": true, "message": "jq is required but not installed. Install with: brew install jq (macOS) or apt-get install jq (Linux)"}' >&2; exit 1; }

API_URL="${CONTO_API_URL:-https://conto.finance}"
SDK_KEY="${CONTO_SDK_KEY:?CONTO_SDK_KEY is required}"

# Enforce HTTPS to prevent credential leakage over plaintext
if [[ "$API_URL" != https://* ]] && [[ "$API_URL" != http://localhost* ]] && [[ "$API_URL" != http://127.0.0.1* ]]; then
  echo '{"error": true, "message": "CONTO_API_URL must use https:// (or http://localhost for development)"}' >&2
  exit 1
fi

# ── Input validation helpers ──

# Validate that a value looks like a safe path segment (alphanumeric, hyphens, underscores)
_validate_id() {
  local value="$1" label="$2"
  if [[ ! "$value" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "{\"error\": true, \"message\": \"Invalid $label: must contain only alphanumeric characters, hyphens, and underscores\"}" >&2
    exit 1
  fi
}

# Validate that a value looks like a blockchain address (0x hex for EVM or base58 for Solana)
_validate_address() {
  local value="$1" label="$2"
  # EVM: 0x followed by 40 hex chars; Solana: 32-44 base58 chars
  if [[ "$value" =~ ^0x[a-fA-F0-9]{40}$ ]] || [[ "$value" =~ ^[1-9A-HJ-NP-Za-km-z]{32,44}$ ]]; then
    return 0
  fi
  echo "{\"error\": true, \"message\": \"Invalid $label: must be an EVM address (0x + 40 hex) or Solana address (32-44 base58)\"}" >&2
  exit 1
}

# Validate that a value is a positive number
_validate_number() {
  local value="$1" label="$2"
  if [[ ! "$value" =~ ^[0-9]+\.?[0-9]*$ ]]; then
    echo "{\"error\": true, \"message\": \"Invalid $label: must be a positive number\"}" >&2
    exit 1
  fi
}

# Validate that a value looks like a hex transaction hash (0x + 64 hex chars)
_validate_tx_hash() {
  local value="$1" label="$2"
  if [[ ! "$value" =~ ^0x[a-fA-F0-9]{64}$ ]]; then
    echo "{\"error\": true, \"message\": \"Invalid $label: must be 0x-prefixed 64-char hex string\"}" >&2
    exit 1
  fi
}

# Validate approval token (64-char hex string)
_validate_token() {
  local value="$1" label="$2"
  if [[ ! "$value" =~ ^[a-fA-F0-9]{64}$ ]]; then
    echo "{\"error\": true, \"message\": \"Invalid $label: must be a 64-char hex string\"}" >&2
    exit 1
  fi
}

# Validate chain ID (numeric)
_validate_chain_id() {
  local value="$1"
  if [[ ! "$value" =~ ^[0-9]+$ ]]; then
    echo '{"error": true, "message": "Invalid chainId: must be a positive integer"}' >&2
    exit 1
  fi
}

# ── HTTP request helper ──

# Make authenticated request with safe header passing and timeouts
_conto_request() {
  local method="$1" endpoint="$2" body="${3:-}"
  local url="${API_URL}${endpoint}"
  local max_retries=1
  local attempt=0
  local response http_code body_out

  while [[ $attempt -le $max_retries ]]; do
    # Pass auth header via stdin to avoid leaking SDK key in process listing
    local args=(-sS -w "\n%{http_code}" -X "$method" -H @- -H "Content-Type: application/json" --connect-timeout 10 --max-time 30 --proto '=https')

    # Allow http for localhost development
    if [[ "$API_URL" == http://localhost* ]] || [[ "$API_URL" == http://127.0.0.1* ]]; then
      args=(-sS -w "\n%{http_code}" -X "$method" -H @- -H "Content-Type: application/json" --connect-timeout 10 --max-time 30)
    fi

    if [[ -n "$body" ]]; then
      args+=(-d "$body")
    fi

    response=$(printf 'Authorization: Bearer %s' "$SDK_KEY" | curl "${args[@]}" "$url")
    http_code=$(echo "$response" | tail -1)
    body_out=$(echo "$response" | sed '$d')

    # Retry on 500/502/503 with a short delay
    if [[ "$http_code" -ge 500 ]] && [[ "$http_code" -le 503 ]] && [[ $attempt -lt $max_retries ]]; then
      attempt=$((attempt + 1))
      sleep 2
      continue
    fi

    if [[ "$http_code" -ge 400 ]]; then
      # Sanitize error output: extract only error/message fields from response
      local safe_error
      safe_error=$(echo "$body_out" | jq -c '{error: true, httpStatus: '"$http_code"', message: (.message // .error // "Request failed")}' 2>/dev/null) \
        || safe_error="{\"error\": true, \"httpStatus\": $http_code, \"message\": \"Request failed\"}"
      echo "$safe_error"
      exit 1
    fi

    echo "$body_out"
    return 0
  done
}

case "${1:-help}" in

  # ── Payment commands ──

  approve)
    amount="${2:?amount required}"
    recipient="${3:?recipientAddress required}"
    sender="${4:?senderAddress required}"
    purpose="${5:-}"
    category="${6:-}"
    chain_id="${7:-42431}"

    _validate_number "$amount" "amount"
    _validate_address "$recipient" "recipientAddress"
    _validate_address "$sender" "senderAddress"
    _validate_chain_id "$chain_id"

    # Build JSON safely with jq
    payload=$(jq -n \
      --argjson amount "$amount" \
      --arg recipient "$recipient" \
      --arg sender "$sender" \
      --arg purpose "$purpose" \
      --arg category "$category" \
      --argjson chain_id "$chain_id" \
      '{
        amount: $amount,
        recipientAddress: $recipient,
        senderAddress: $sender,
        purpose: (if $purpose == "" then null else $purpose end),
        category: (if $category == "" then null else $category end),
        chainId: $chain_id
      }')
    _conto_request POST /api/sdk/payments/approve "$payload"
    ;;

  confirm)
    approval_id="${2:?approvalId required}"
    tx_hash="${3:?txHash required}"
    approval_token="${4:?approvalToken required}"

    _validate_id "$approval_id" "approvalId"
    _validate_tx_hash "$tx_hash" "txHash"
    _validate_token "$approval_token" "approvalToken"

    payload=$(jq -n \
      --arg tx_hash "$tx_hash" \
      --arg approval_token "$approval_token" \
      '{txHash: $tx_hash, approvalToken: $approval_token}')
    _conto_request POST "/api/sdk/payments/${approval_id}/confirm" "$payload"
    ;;

  x402)
    amount="${2:?amount required}"
    recipient="${3:?recipientAddress required}"
    resource_url="${4:?resourceUrl required}"
    facilitator="${5:-}"
    scheme="${6:-}"

    _validate_number "$amount" "amount"
    _validate_address "$recipient" "recipientAddress"

    payload=$(jq -n \
      --argjson amount "$amount" \
      --arg recipient "$recipient" \
      --arg resource_url "$resource_url" \
      --arg facilitator "$facilitator" \
      --arg scheme "$scheme" \
      '{
        amount: $amount,
        recipientAddress: $recipient,
        resourceUrl: $resource_url,
        facilitator: (if $facilitator == "" then null else $facilitator end),
        scheme: (if $scheme == "" then null else $scheme end),
        category: "API_PROVIDER"
      }')
    _conto_request POST /api/sdk/x402/pre-authorize "$payload"
    ;;

  budget)
    _conto_request GET /api/sdk/x402/budget
    ;;

  services)
    _conto_request GET /api/sdk/x402/services
    ;;

  # ── Policy management commands (requires admin SDK key) ──

  policies)
    _conto_request GET /api/policies
    ;;

  policy)
    policy_id="${2:?policy_id required}"
    _validate_id "$policy_id" "policy_id"
    _conto_request GET "/api/policies/${policy_id}"
    ;;

  create-policy)
    body="${2:?JSON body required}"
    # Validate that the input is valid JSON
    echo "$body" | jq . >/dev/null 2>&1 || { echo '{"error": true, "message": "Invalid JSON body"}' >&2; exit 1; }
    _conto_request POST /api/policies "$body"
    ;;

  update-policy)
    policy_id="${2:?policy_id required}"
    body="${3:?JSON body required}"
    _validate_id "$policy_id" "policy_id"
    echo "$body" | jq . >/dev/null 2>&1 || { echo '{"error": true, "message": "Invalid JSON body"}' >&2; exit 1; }
    _conto_request PATCH "/api/policies/${policy_id}" "$body"
    ;;

  delete-policy)
    policy_id="${2:?policy_id required}"
    _validate_id "$policy_id" "policy_id"
    _conto_request DELETE "/api/policies/${policy_id}"
    ;;

  get-rules)
    policy_id="${2:?policy_id required}"
    _validate_id "$policy_id" "policy_id"
    _conto_request GET "/api/policies/${policy_id}/rules"
    ;;

  set-rules)
    policy_id="${2:?policy_id required}"
    body="${3:?JSON body required}"
    _validate_id "$policy_id" "policy_id"
    echo "$body" | jq . >/dev/null 2>&1 || { echo '{"error": true, "message": "Invalid JSON body"}' >&2; exit 1; }
    _conto_request PUT "/api/policies/${policy_id}/rules" "$body"
    ;;

  add-rule)
    policy_id="${2:?policy_id required}"
    body="${3:?JSON body required}"
    _validate_id "$policy_id" "policy_id"
    echo "$body" | jq . >/dev/null 2>&1 || { echo '{"error": true, "message": "Invalid JSON body"}' >&2; exit 1; }
    _conto_request POST "/api/policies/${policy_id}/rules" "$body"
    ;;

  delete-rule)
    policy_id="${2:?policy_id required}"
    rule_id="${3:?rule_id required}"
    _validate_id "$policy_id" "policy_id"
    _validate_id "$rule_id" "rule_id"
    _conto_request DELETE "/api/policies/${policy_id}/rules/${rule_id}"
    ;;

  help|*)
    cat <<USAGE
Conto Policy Check & Management — OpenClaw Helper

Payment Commands (standard SDK key):
  approve       <amount> <recipient> <sender> [purpose] [category] [chain_id]
  confirm       <approval_id> <tx_hash> <approval_token>
  x402          <amount> <recipient> <resource_url> [facilitator] [scheme]
  budget        Check remaining x402 budget and burn rate
  services      List x402 services this agent has used

Policy Commands (requires admin SDK key):
  policies                          List all policies
  policy        <id>                Get a single policy with rules
  create-policy <json>              Create a new policy
  update-policy <id> <json>         Update policy name/priority/active
  delete-policy <id>                Delete a policy
  get-rules     <policy_id>         List rules for a policy
  set-rules     <policy_id> <json>  Replace all rules on a policy
  add-rule      <policy_id> <json>  Add a rule to a policy
  delete-rule   <policy_id> <rule_id>  Delete a single rule

Environment:
  CONTO_SDK_KEY   (required) Your Conto SDK API key
  CONTO_API_URL   (optional) API base URL, default: https://conto.finance

Requires: bash, curl, jq

Examples:
  # Check policy before payment
  conto-check.sh approve 50 0xabc... 0x123... "Pay for API" API_PROVIDER

  # List policies
  conto-check.sh policies

  # Create a \$200 per-tx limit policy
  conto-check.sh create-policy '{"name":"Max \$200","policyType":"SPEND_LIMIT","priority":10,"isActive":true,"rules":[{"ruleType":"MAX_AMOUNT","operator":"LTE","value":"200","action":"ALLOW"}]}'

  # Block an address
  conto-check.sh create-policy '{"name":"Blocklist","policyType":"COUNTERPARTY","priority":50,"isActive":true,"rules":[{"ruleType":"BLOCKED_COUNTERPARTIES","operator":"IN_LIST","value":"[\"0xbad...\"]","action":"DENY"}]}'

  # Add a rule to existing policy
  conto-check.sh add-rule cmm59z... '{"ruleType":"DAILY_LIMIT","operator":"LTE","value":"1000","action":"ALLOW"}'
USAGE
    ;;
esac
