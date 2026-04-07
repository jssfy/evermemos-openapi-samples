# EverOS SDK v1 Samples
# 环境变量：EVEROS_API_KEY, EVER_OS_BASE_URL
#
# 快速开始：
#   export EVEROS_API_KEY=xxx
#   export EVER_OS_BASE_URL=https://dev-gateway.aws.evermind.ai
#   make all

PYTHON := python

.DEFAULT_GOAL := help

.PHONY: help all memories cases getting-started cookbook \
        add add-sync add-get-sync \
        get search delete \
        request-status \
        meta-create meta-get meta-update \
        batch-add \
        gs-save gs-get gs-search \
        qs-sync qs-async qs-complete \
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

request-status: check-env
	$(PYTHON) get_request_status_async.py

# ── REMOVED in v1 (kept for documentation) ───────────────
meta-create:
	$(PYTHON) create_meta_async.py

meta-get:
	$(PYTHON) get_meta_async.py

meta-update:
	$(PYTHON) update_meta_async.py

# ── cases/ ───────────────────────────────────────────────
batch-add: check-env
	$(PYTHON) cases/batch_add_async.py

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

# ── 分组批量执行 ──────────────────────────────────────────
## memories: 写入、查询、搜索、删除
memories: check-env
	@echo "=== [1/4] add (async) ==="
	$(PYTHON) add_async.py
	@echo "=== [2/4] get (async) ==="
	$(PYTHON) get_async.py
	@echo "=== [3/4] search (async) ==="
	$(PYTHON) search_async.py
	@echo "=== [4/4] delete (async) ==="
	$(PYTHON) delete_async.py

## cases: cases/ 目录下的批量用例
cases: check-env
	@echo "=== batch-add ==="
	$(PYTHON) cases/batch_add_async.py

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

## all: 顺序执行全部样本（跳过 removed conversation_meta 示例）
all: check-env
	@echo "========================================"
	@echo " EverOS SDK v1 - Running all samples"
	@echo "========================================"
	@for f in add_sync.py add_async.py add_get_sync.py \
	           get_async.py search_async.py delete_async.py \
	           get_request_status_async.py \
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
	@echo "EverOS SDK v1 Samples"
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
	@echo "    make request-status   get_request_status_async.py"
	@echo "    make batch-add        cases/batch_add_async.py"
	@echo "    make gs-save          getting-started/03_save.py"
	@echo "    make gs-get           getting-started/04.1_get.py"
	@echo "    make gs-search        getting-started/04.2_search.py"
	@echo "    make qs-sync          cookbook/quickstart_sdk_sync.py"
	@echo "    make qs-async         cookbook/quickstart_sdk_async.py"
	@echo "    make qs-complete      cookbook/quickstart_sdk_complete.py"
	@echo ""
	@echo "  REMOVED in v1 (will raise NotImplementedError):"
	@echo "    make meta-create      create_meta_async.py (conversation_meta removed)"
	@echo "    make meta-get         get_meta_async.py    (conversation_meta removed)"
	@echo "    make meta-update      update_meta_async.py (conversation_meta removed)"
	@echo ""
	@echo "  Batch:"
	@echo "    make memories         写入、查询、搜索、删除"
	@echo "    make cases            cases/ 批量用例"
	@echo "    make getting-started  getting-started/ 入门示例"
	@echo "    make cookbook         cookbook/ Quickstart 示例"
	@echo "    make all              全部样本（跳过 conversation_meta 示例）"
	@echo ""
