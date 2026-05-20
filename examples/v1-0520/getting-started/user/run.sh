#!/usr/bin/env bash
# Getting Started — User memory (curl版)
# Endpoints: POST /api/v1/memory/{add|get|search}
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
  echo "=== [save] POST /api/v1/memory/add (owner_type=user) ==="
  curl -s -X POST "$BASE/api/v1/memory/add" \
    -H "$AUTH" \
    -H "$CT" \
    -d '{
      "owner_id":   "user_demo_001",
      "owner_type": "user",
      "session_id": "session_getting_started",
      "messages": [
        {
          "role":      "user",
          "timestamp": 1736935200000,
          "content":   "I like black Americano, no sugar, the stronger the better!"
        },
        {
          "role":      "user",
          "timestamp": 1737021660000,
          "content":   "Today I want to discuss the project progress."
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
      "owner_id":    "user_demo_001",
      "owner_type":  "user",
      "memory_type": "episodic_memory",
      "page_size":   5,
      "sort_by":     "timestamp",
      "sort_order":  "desc"
    }' | python3 -m json.tool

  echo ""
  echo "=== [get] POST /api/v1/memory/get (memory_type=profile) ==="
  curl -s -X POST "$BASE/api/v1/memory/get" \
    -H "$AUTH" \
    -H "$CT" \
    -d '{
      "owner_id":    "user_demo_001",
      "owner_type":  "user",
      "memory_type": "profile",
      "page_size":   5
    }' | python3 -m json.tool
}

# ── 04.2: search ─────────────────────────────────────────────────────────────
run_search() {
  echo ""
  echo "=== [search] POST /api/v1/memory/search (method=hybrid, include_profile=true) ==="
  curl -s -X POST "$BASE/api/v1/memory/search" \
    -H "$AUTH" \
    -H "$CT" \
    -d '{
      "owner_id":       "user_demo_001",
      "owner_type":     "user",
      "query":          "coffee preference",
      "method":         "hybrid",
      "include_profile": true,
      "top_k":          5
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
