.PHONY: test test-all clean help setup

# 环境选择：make test-all ENV=dev (默认) | test | prod
ENV ?= dev
ENV_FILE := .env.$(ENV)

ifneq ($(wildcard $(ENV_FILE)),)
  include $(ENV_FILE)
  export
else
  $(error 配置文件 $(ENV_FILE) 不存在。请复制 .env.example 并填写: cp .env.example $(ENV_FILE))
endif

# Python 运行命令（使用 uv 管理依赖和虚拟环境）
PYTHON := uv run python

# 默认目标：运行所有测试用例（01–10）
test: test-all

# 初始化环境（安装依赖）
setup:
	@echo "==> 初始化 uv 环境..."
	uv sync
	@echo "✅ 环境初始化完成"

# 运行所有测试用例
test-all:
	@echo "=========================================="
	@echo "环境: $(ENV) | $(EVER_MEM_OS_BASE_URL)"
	@echo "开始运行所有测试用例..."
	@echo "=========================================="
	@echo ""
	@echo "📝 1/10 - 同步写入个人记忆 (01_add_sync.py)"
	@cd examples && $(PYTHON) 01_add_sync.py
	@echo ""
	@echo "✅ 1/10 完成"
	@echo ""
	@echo "📝 2/10 - 异步写入 + 轮询状态 (02_add_async.py)"
	@cd examples && $(PYTHON) 02_add_async.py
	@echo ""
	@echo "✅ 2/10 完成"
	@echo ""
	@echo "📝 3/10 - 查询记忆 (03_get_sync.py)"
	@cd examples && $(PYTHON) 03_get_sync.py
	@echo ""
	@echo "✅ 3/10 完成"
	@echo ""
	@echo "📝 4/10 - 搜索记忆 (04_search_sync.py)"
	@cd examples && $(PYTHON) 04_search_sync.py
	@echo ""
	@echo "✅ 4/10 完成"
	@echo ""
	@echo "📝 5/10 - 删除记忆 (05_delete_sync.py)"
	@cd examples && $(PYTHON) 05_delete_sync.py
	@echo ""
	@echo "✅ 5/10 完成"
	@echo ""
	@echo "📝 6/10 - 触发会话边界 (06_flush_sync.py)"
	@cd examples && $(PYTHON) 06_flush_sync.py
	@echo ""
	@echo "✅ 6/10 完成"
	@echo ""
	@echo "📝 7/10 - Agent 记忆 (07_agent_memories.py)"
	@cd examples && $(PYTHON) 07_agent_memories.py
	@echo ""
	@echo "✅ 7/10 完成"
	@echo ""
	@echo "📝 8/10 - 群组记忆 (08_group_memories.py)"
	@cd examples && $(PYTHON) 08_group_memories.py
	@echo ""
	@echo "✅ 8/10 完成"
	@echo ""
	@echo "📝 9/10 - Groups/Senders/Settings CRUD (09_groups_senders.py)"
	@cd examples && $(PYTHON) 09_groups_senders.py
	@echo ""
	@echo "✅ 9/10 完成"
	@echo ""
	@echo "📝 10/10 - 文件上传预签名 (10_object_sign.py)"
	@cd examples && $(PYTHON) 10_object_sign.py
	@echo ""
	@echo "✅ 10/10 完成"
	@echo ""
	@echo "=========================================="
	@echo "🎉 所有测试用例执行成功！"
	@echo "=========================================="

# 运行单个测试用例
test-one:
	@if [ -z "$(SCRIPT)" ]; then \
		echo "❌ 错误: 需要指定脚本名称"; \
		echo "用法: make test-one SCRIPT=add_async.py"; \
		exit 1; \
	fi
	@echo "📝 运行: $(SCRIPT)"
	@cd examples && $(PYTHON) $(SCRIPT)

# 清理（可以根据需要添加清理逻辑）
clean:
	@echo "🧹 清理临时文件..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ 清理完成"

# 帮助信息
help:
	@echo "EverMemOS 示例代码测试（使用 uv 管理依赖）"
	@echo ""
	@echo "可用的 make 目标："
	@echo "  make setup         - 初始化 uv 环境（首次使用前运行）"
	@echo "  make test          - 运行所有测试用例（默认，01–10）"
	@echo "  make test-all      - 运行所有测试用例（01–10）"
	@echo "  make test-batch    - 运行批量离线导入测试"
	@echo "                       用法: make test-batch FILE=input.txt [CHUNK_SIZE=1000] [START=1] [MAX=10]"
	@echo "  make test-one      - 运行单个测试用例"
	@echo "                       用法: make test-one SCRIPT=add_async.py"
	@echo "  make clean         - 清理临时文件"
	@echo "  make help          - 显示此帮助信息"
	@echo ""
	@echo "环境选择（ENV 参数）："
	@echo "  dev   - 开发环境（默认）"
	@echo "  test  - 测试环境"
	@echo "  prod  - 生产环境"
	@echo ""
	@echo "其他环境变量："
	@echo "  EVERMEMOS_GROUP_ID             - 群组ID"
	@echo "  EVERMEMOS_GROUP_NAME           - 群组名称"
	@echo "  EVERMEMOS_SENDER               - 发送者ID"
	@echo "  EVERMEMOS_SENDER_NAME          - 发送者名称"
	@echo ""
	@echo "配置文件："
	@echo "  .env.dev      - 开发环境配置（默认加载）"
	@echo "  .env.test     - 测试环境配置"
	@echo "  .env.prod     - 生产环境配置"
	@echo "  .env.example  - 配置模板（已提交 git）"
	@echo ""
	@echo "首次使用："
	@echo "  cp .env.example .env.dev   # 复制模板并填写密钥"
	@echo ""
	@echo "示例："
	@echo "  make setup                              # 初始化依赖"
	@echo "  make test                               # dev 环境（默认）"
	@echo "  make test ENV=test                      # 测试环境"
	@echo "  make test ENV=prod                      # 生产环境"
	@echo "  make test-batch FILE=test.txt CHUNK_SIZE=500"
	@echo "  make test-one SCRIPT=04_search_sync.py"
