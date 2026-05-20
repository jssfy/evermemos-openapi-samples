# EverOS SDK v1 Samples (0.0.1 - 2026-05-20)
#
# Install SDK:
#   pip install https://pkg.stainless.com/s/everos-trial-python/ea677a49282be2c1723740b1a7fa943cc01e0d5a/everos-0.0.1-py3-none-any.whl
#
# 快速开始：
#   export EVEROS_API_KEY=xxx
#   export EVER_OS_BASE_URL=https://dev-gateway.aws.evermind.ai
#   make all
#
# Key API changes in 0.0.1:
#   - client.v1.memories → client.v1.memory (singular)
#   - user_id → owner_id + owner_type ("user" | "agent")
#   - session_id is now required in memory.add()
#   - NEW: memory.feedback(), client.v1.storage.sign()
#   - NEW memory types: agent_case, agent_skill (owner_type="agent")
#   - search() method "agentic" added

PYTHON := /opt/miniconda3/bin/python3

.DEFAULT_GOAL := help

.PHONY: help all memory cases getting-started cookbook \
        add add-sync add-get-sync \
        get search delete \
        feedback storage-sign task-status \
        gs-save gs-get gs-search \
        qs-sync qs-async qs-complete \
        agent-memory feedback-correction \
        check-env

# ── 环境检查 ──────────────────────────────────────────────
check-env:
	@test -n "$$EVEROS_API_KEY"    || (echo "ERROR: EVEROS_API_KEY not set"; exit 1)
	@test -n "$$EVER_OS_BASE_URL"  || (echo "ERROR: EVER_OS_BASE_URL not set"; exit 1)

# ── 单个样本 ─────────────────────────────────────────────
add: check-env
	$(PYTHON) add_async.py

add-sync: check-env
	$(PYTHON) add_sync.py

add-get-sync: check-env
	$(PYTHON) add_get_sync.py

get: check-env
	$(PYTHON) get_async.py

search: check-env
	$(PYTHON) search_async.py

delete: check-env
	$(PYTHON) delete_async.py

feedback: check-env
	$(PYTHON) feedback_async.py

storage-sign: check-env
	$(PYTHON) storage_sign_async.py

task-status: check-env
	$(PYTHON) get_task_status_async.py

# ── getting-started/ ─────────────────────────────────────
gs-save: check-env
	$(PYTHON) getting-started/03_save.py

gs-get: check-env
	$(PYTHON) getting-started/04.1_get.py

gs-search: check-env
	$(PYTHON) getting-started/04.2_search.py

# ── cookbook/ ────────────────────────────────────────────
qs-sync: check-env
	$(PYTHON) cookbook/quickstart_sdk_sync.py

qs-async: check-env
	$(PYTHON) cookbook/quickstart_sdk_async.py

qs-complete: check-env
	$(PYTHON) cookbook/quickstart_sdk_complete.py

# ── cases/ ───────────────────────────────────────────────
agent-memory: check-env
	$(PYTHON) cases/agent_memory_async.py

feedback-correction: check-env
	$(PYTHON) cases/feedback_correction_async.py

# ── 分组批量执行 ──────────────────────────────────────────
## memory: 写入、查询、搜索、删除、feedback
memory: check-env
	@echo "=== [1/5] add (async) ==="
	$(PYTHON) add_async.py
	@echo "=== [2/5] get (async) ==="
	$(PYTHON) get_async.py
	@echo "=== [3/5] search (async) ==="
	$(PYTHON) search_async.py
	@echo "=== [4/5] delete (async) ==="
	$(PYTHON) delete_async.py
	@echo "=== [5/5] feedback (async) ==="
	$(PYTHON) feedback_async.py

## cases: cases/ 目录下的用例
cases: check-env
	@echo "=== agent-memory ==="
	$(PYTHON) cases/agent_memory_async.py
	@echo "=== feedback-correction ==="
	$(PYTHON) cases/feedback_correction_async.py

## getting-started: getting-started/ 目录下的入门示例
getting-started: check-env
	@echo "=== [1/3] save ==="
	$(PYTHON) getting-started/03_save.py
	@echo "=== [2/3] get ==="
	$(PYTHON) getting-started/04.1_get.py
	@echo "=== [3/3] search ==="
	$(PYTHON) getting-started/04.2_search.py

## cookbook: cookbook/ 目录下的 Quickstart 示例
cookbook: check-env
	@echo "=== [1/3] quickstart-sync ==="
	$(PYTHON) cookbook/quickstart_sdk_sync.py
	@echo "=== [2/3] quickstart-async ==="
	$(PYTHON) cookbook/quickstart_sdk_async.py
	@echo "=== [3/3] quickstart-complete ==="
	$(PYTHON) cookbook/quickstart_sdk_complete.py

## all: 顺序执行全部样本
all: check-env
	@echo "========================================"
	@echo " EverOS SDK v1 (0.0.1) - Running all samples"
	@echo "========================================"
	@for f in add_sync.py add_async.py add_get_sync.py \
	           get_async.py search_async.py delete_async.py \
	           feedback_async.py storage_sign_async.py \
	           get_task_status_async.py \
	           cookbook/quickstart_sdk_sync.py \
	           cookbook/quickstart_sdk_async.py \
	           cookbook/quickstart_sdk_complete.py; do \
	  echo ""; \
	  echo ">>> $$f"; \
	  $(PYTHON) $$f || echo "!!! $$f FAILED (continuing)"; \
	done
	@echo ""
	@echo "========================================"
	@echo " Done"
	@echo "========================================"

# ── 帮助 ─────────────────────────────────────────────────
help:
	@echo ""
	@echo "EverOS SDK v1 (0.0.1) Samples"
	@echo ""
	@echo "  Prerequisites:"
	@echo "    export EVEROS_API_KEY=<your_key>"
	@echo "    export EVER_OS_BASE_URL=https://dev-gateway.aws.evermind.ai"
	@echo ""
	@echo "  Single sample:"
	@echo "    make add              add_async.py"
	@echo "    make add-sync         add_sync.py"
	@echo "    make add-get-sync     add_get_sync.py"
	@echo "    make get              get_async.py"
	@echo "    make search           search_async.py"
	@echo "    make delete           delete_async.py"
	@echo "    make feedback         feedback_async.py         [NEW]"
	@echo "    make storage-sign     storage_sign_async.py     [NEW]"
	@echo "    make task-status      get_task_status_async.py"
	@echo "    make gs-save          getting-started/03_save.py"
	@echo "    make gs-get           getting-started/04.1_get.py"
	@echo "    make gs-search        getting-started/04.2_search.py"
	@echo "    make qs-sync          cookbook/quickstart_sdk_sync.py"
	@echo "    make qs-async         cookbook/quickstart_sdk_async.py"
	@echo "    make qs-complete      cookbook/quickstart_sdk_complete.py"
	@echo "    make agent-memory     cases/agent_memory_async.py  [NEW]"
	@echo "    make feedback-correction  cases/feedback_correction_async.py  [NEW]"
	@echo ""
	@echo "  Batch:"
	@echo "    make memory           写入、查询、搜索、删除、feedback"
	@echo "    make cases            cases/ 用例"
	@echo "    make getting-started  getting-started/ 入门示例"
	@echo "    make cookbook         cookbook/ Quickstart 示例"
	@echo "    make all              全部样本"
	@echo ""
	@echo "  API Changes in 0.0.1:"
	@echo "    client.v1.memories → client.v1.memory (singular)"
	@echo "    user_id → owner_id + owner_type ('user'|'agent')"
	@echo "    session_id now required in memory.add()"
	@echo "    NEW: memory.feedback(memory_id, memory_type, content)"
	@echo "    NEW: client.v1.storage.sign(object_list)"
	@echo "    NEW memory types: agent_case, agent_skill"
	@echo "    NEW search method: agentic"
	@echo ""
