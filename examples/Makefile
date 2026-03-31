# EverMemOS SDK v1 Samples
# 环境变量：EVERMEMOS_API_KEY, EVER_MEM_OS_BASE_URL
#
# 快速开始：
#   export EVERMEMOS_API_KEY=xxx
#   export EVER_MEM_OS_BASE_URL=https://dev-gateway.aws.evermind.ai
#   make all

PYTHON := python

.DEFAULT_GOAL := help

.PHONY: help all memories agent group management \
        add add-async get search delete flush \
        agent-mem group-mem mgmt sign \
        check-env

# ── 环境检查 ──────────────────────────────────────────────
check-env:
	@test -n "$$EVERMEMOS_API_KEY"      || (echo "ERROR: EVERMEMOS_API_KEY not set"; exit 1)
	@test -n "$$EVER_MEM_OS_BASE_URL"   || (echo "ERROR: EVER_MEM_OS_BASE_URL not set"; exit 1)

# ── 单个样本 ─────────────────────────────────────────────
add: check-env
	$(PYTHON) 01_add_sync.py

add-async: check-env
	$(PYTHON) 02_add_async.py

get: check-env
	$(PYTHON) 03_get_sync.py

search: check-env
	$(PYTHON) 04_search_sync.py

delete: check-env
	$(PYTHON) 05_delete_sync.py

flush: check-env
	$(PYTHON) 06_flush_sync.py

agent-mem: check-env
	$(PYTHON) 07_agent_memories.py

group-mem: check-env
	$(PYTHON) 08_group_memories.py

mgmt: check-env
	$(PYTHON) 09_groups_senders.py

sign: check-env
	$(PYTHON) 10_object_sign.py

# ── 分组批量执行 ──────────────────────────────────────────
## memories: 个人记忆（写入、查询、搜索、删除、flush）
memories: check-env
	@echo "=== [1/5] add ==="
	$(PYTHON) 01_add_sync.py
	@echo "=== [2/5] get ==="
	$(PYTHON) 03_get_sync.py
	@echo "=== [3/5] search ==="
	$(PYTHON) 04_search_sync.py
	@echo "=== [4/5] delete ==="
	$(PYTHON) 05_delete_sync.py
	@echo "=== [5/5] flush ==="
	$(PYTHON) 06_flush_sync.py

## agent: Agent 轨迹记忆（写入 + flush）
agent: check-env
	@echo "=== agent memories ==="
	$(PYTHON) 07_agent_memories.py

## group: 群组记忆（写入 + flush）
group: check-env
	@echo "=== group memories ==="
	$(PYTHON) 08_group_memories.py

## management: Groups / Senders / Settings / Object Sign CRUD
management: check-env
	@echo "=== [1/2] groups + senders + settings ==="
	$(PYTHON) 09_groups_senders.py
	@echo "=== [2/2] object sign ==="
	$(PYTHON) 10_object_sign.py

## all: 顺序执行全部 10 个样本
all: check-env
	@echo "========================================"
	@echo " EverMemOS SDK v1 - Running all samples"
	@echo "========================================"
	@for f in 01_add_sync.py 02_add_async.py 03_get_sync.py \
	           04_search_sync.py 05_delete_sync.py 06_flush_sync.py \
	           07_agent_memories.py 08_group_memories.py \
	           09_groups_senders.py 10_object_sign.py; do \
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
	@echo "EverMemOS SDK v1 Samples"
	@echo ""
	@echo "  Prerequisites:"
	@echo "    export EVERMEMOS_API_KEY=<your_key>"
	@echo "    export EVER_MEM_OS_BASE_URL=https://dev-gateway.aws.evermind.ai"
	@echo ""
	@echo "  Single sample:"
	@echo "    make add          01_add_sync.py"
	@echo "    make add-async    02_add_async.py"
	@echo "    make get          03_get_sync.py"
	@echo "    make search       04_search_sync.py"
	@echo "    make delete       05_delete_sync.py"
	@echo "    make flush        06_flush_sync.py"
	@echo "    make agent-mem    07_agent_memories.py"
	@echo "    make group-mem    08_group_memories.py"
	@echo "    make mgmt         09_groups_senders.py"
	@echo "    make sign         10_object_sign.py"
	@echo ""
	@echo "  Batch:"
	@echo "    make memories     个人记忆（01,03,04,05,06）"
	@echo "    make agent        Agent 记忆（07）"
	@echo "    make group        群组记忆（08）"
	@echo "    make management   管理 + 签名（09,10）"
	@echo "    make all          全部 10 个样本"
	@echo ""
