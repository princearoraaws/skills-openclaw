#!/usr/bin/env bash
# =====================================================
# Bailian Skill Extraction Script
# Usage: ./extract_skill.sh <messages_json> [existing_skills_json]
# =====================================================

set -euo pipefail

ENDPOINT="https://poc-dashscope.aliyuncs.com/api/v2/apps/poc-memory/skills/extract"

# Check API key
if [ -z "${DASHSCOPE_API_KEY:-}" ]; then
    echo "Error: DASHSCOPE_API_KEY environment variable is not set" >&2
    exit 1
fi

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <messages_json> [existing_skills_json]" >&2
    echo "  messages_json: JSON array of conversation messages" >&2
    echo "  existing_skills_json: Optional JSON array of existing skills" >&2
    exit 1
fi

MESSAGES="$1"
EXISTING_SKILLS="${2:-}"

# Build request body
if [ -n "$EXISTING_SKILLS" ]; then
    REQUEST_BODY=$(cat <<EOF
{
  "messages": $MESSAGES,
  "existing_skills": $EXISTING_SKILLS
}
EOF
)
else
    REQUEST_BODY=$(cat <<EOF
{
  "messages": $MESSAGES
}
EOF
)
fi

# Call API
RESPONSE=$(curl -s -w "\n%{http_code}" \
    --max-time 30 \
    -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
    -d "$REQUEST_BODY" 2>&1)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
    echo "Error: API returned HTTP $HTTP_CODE" >&2
    echo "$BODY" >&2
    exit 1
fi

# Output result
echo "$BODY"