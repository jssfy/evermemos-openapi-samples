#!/usr/bin/env bash
# Getting Started — Agent memory (curl版)
# Endpoints: POST /api/v1/memory/{add|get|search}
# owner_type="agent" — stores episodic traces; server may distill agent_case / agent_skill
#
# Usage:
#   export EVEROS_API_KEY=<your_key>
#   export EVER_OS_BASE_URL=https://dev-gateway.aws.evermind.ai
#   bash run.sh [save|get|search|all]

set -euo pipefail

: "${EVEROS_API_KEY:?EVEROS_API_KEY is not set}"
: "${EVER_OS_BASE_URL:?EVER_OS_BASE_URL is not set}"

BASE="$EVER_OS_BASE_URL"
AUTH="Authorization: Bearer $EVEROS_API_KEY"
CT="Content-Type: application/json"

CMD="${1:-all}"

# ── 03: save ────────────────────────────────────────────────────────────────
run_save() {
  echo "=== [save] POST /api/v1/memory/add (owner_type=agent, with tool_calls) ==="
  curl -s -X POST "$BASE/api/v1/memory/add" \
    -H "$AUTH" \
    -H "$CT" \
    -d '{
      "owner_id":   "agent_demo_001",
      "owner_type": "agent",
      "agent_id":   "agent_demo_001",
      "session_id": "session_agent_getting_started",
      "messages": [
        {
          "role":      "user",
          "timestamp": 1736935200000,
          "content":   "Analyze sales.csv and generate a monthly revenue summary."
        },
        {
          "role":      "assistant",
          "timestamp": 1736935210000,
          "tool_calls": [
            {
              "id":   "call_001",
              "type": "function",
              "function": {
                "name":      "read_file",
                "arguments": "{\"path\": \"sales.csv\"}"
              }
            }
          ]
        },
        {
          "role":         "tool",
          "timestamp":    1736935220000,
          "tool_call_id": "call_001",
          "content":      "date,product,revenue\n2025-01,Widget A,50000\n2025-02,Widget A,62000"
        },
        {
          "role":      "assistant",
          "timestamp": 1736935230000,
          "content":   "Analysis complete. Widget A: Jan $50k, Feb $62k. Total Q1: $112k (+24% MoM)."
        }
      ]
    }' | python3 -m json.tool
}

# ── 04.1: get ────────────────────────────────────────────────────────────────
run_get() {
  echo ""
  echo "=== [get] POST /api/v1/memory/get (memory_type=episodic_memory) ==="
  curl -s -X POST "$BASE/api/v1/memory/get" \
    -H "$AUTH" \
    -H "$CT" \
    -d '{
      "owner_id":    "agent_demo_001",
      "owner_type":  "agent",
      "memory_type": "episodic_memory",
      "page_size":   5,
      "sort_by":     "timestamp",
      "sort_order":  "desc"
    }' | python3 -m json.tool

  echo ""
  echo "=== [get] POST /api/v1/memory/get (memory_type=agent_case) ==="
  curl -s -X POST "$BASE/api/v1/memory/get" \
    -H "$AUTH" \
    -H "$CT" \
    -d '{
      "owner_id":    "agent_demo_001",
      "owner_type":  "agent",
      "memory_type": "agent_case",
      "page_size":   5
    }' | python3 -m json.tool

  echo ""
  echo "=== [get] POST /api/v1/memory/get (memory_type=agent_skill) ==="
  curl -s -X POST "$BASE/api/v1/memory/get" \
    -H "$AUTH" \
    -H "$CT" \
    -d '{
      "owner_id":    "agent_demo_001",
      "owner_type":  "agent",
      "memory_type": "agent_skill",
      "page_size":   5
    }' | python3 -m json.tool
}

# ── 04.2: search ─────────────────────────────────────────────────────────────
run_search() {
  echo ""
  echo "=== [search] POST /api/v1/memory/search (method=hybrid) ==="
  curl -s -X POST "$BASE/api/v1/memory/search" \
    -H "$AUTH" \
    -H "$CT" \
    -d '{
      "owner_id":   "agent_demo_001",
      "owner_type": "agent",
      "query":      "data analysis and CSV processing",
      "method":     "hybrid",
      "top_k":      5
    }' | python3 -m json.tool

  echo ""
  echo "=== [search] POST /api/v1/memory/search (method=agentic) ==="
  curl -s -X POST "$BASE/api/v1/memory/search" \
    -H "$AUTH" \
    -H "$CT" \
    -d '{
      "owner_id":   "agent_demo_001",
      "owner_type": "agent",
      "query":      "what tasks has this agent successfully completed?",
      "method":     "agentic",
      "top_k":      5
    }' | python3 -m json.tool
}

case "$CMD" in
  save)   run_save ;;
  get)    run_get ;;
  search) run_search ;;
  all)
    run_save
    echo ""
    echo "Waiting 8s for memory extraction..."
    sleep 8
    run_get
    run_search
    ;;
  *)
    echo "Usage: $0 [save|get|search|all]"
    exit 1
    ;;
esac
