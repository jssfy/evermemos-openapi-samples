# EverOS SDK v0 Samples
# 环境变量：EVEROS_API_KEY, EVER_OS_BASE_URL
#
# 快速开始：
#   export EVEROS_API_KEY=xxx
#   export EVER_OS_BASE_URL=https://dev-gateway.aws.evermind.ai
#   make all

PYTHON := python

.DEFAULT_GOAL := help

.PHONY: help all memories meta cases getting-started \
        add add-sync add-get-sync \
        get search delete \
        create-meta get-meta update-meta \
        request-status reproduce-bugs \
        batch-add \
        gs-save gs-get gs-search \
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

create-meta: check-env
	$(PYTHON) create_meta_async.py

get-meta: check-env
	$(PYTHON) get_meta_async.py

update-meta: check-env
	$(PYTHON) update_meta_async.py

request-status: check-env
	$(PYTHON) get_request_status_async.py

reproduce-bugs: check-env
	$(PYTHON) reproduce_bugs.py

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

## meta: Metadata CRUD
meta: check-env
	@echo "=== [1/3] create-meta ==="
	$(PYTHON) create_meta_async.py
	@echo "=== [2/3] get-meta ==="
	$(PYTHON) get_meta_async.py
	@echo "=== [3/3] update-meta ==="
	$(PYTHON) update_meta_async.py

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

## all: 顺序执行全部样本（跳过 reproduce-bugs & getting-started 教学示例）
all: check-env
	@echo "========================================"
	@echo " EverOS SDK v0 - Running all samples"
	@echo "========================================"
	@for f in add_sync.py add_async.py add_get_sync.py \
	           get_async.py search_async.py delete_async.py \
	           create_meta_async.py get_meta_async.py update_meta_async.py \
	           get_request_status_async.py; do \
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
	@echo "EverOS SDK v0 Samples"
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
	@echo "    make create-meta      create_meta_async.py"
	@echo "    make get-meta         get_meta_async.py"
	@echo "    make update-meta      update_meta_async.py"
	@echo "    make request-status   get_request_status_async.py"
	@echo "    make reproduce-bugs   reproduce_bugs.py"
	@echo "    make batch-add        cases/batch_add_async.py"
	@echo "    make gs-save          getting-started/03_save.py"
	@echo "    make gs-get           getting-started/04.1_get.py"
	@echo "    make gs-search        getting-started/04.2_search.py"
	@echo ""
	@echo "  Batch:"
	@echo "    make memories         写入、查询、搜索、删除"
	@echo "    make meta             Metadata CRUD"
	@echo "    make cases            cases/ 批量用例"
	@echo "    make getting-started  getting-started/ 入门示例"
	@echo "    make all              全部样本（跳过 reproduce-bugs & getting-started 教学示例）"
	@echo ""
