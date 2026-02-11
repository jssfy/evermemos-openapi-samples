.PHONY: test test-all clean help setup

# Python 运行命令（使用 uv 管理依赖和虚拟环境）
PYTHON := uv run python

# 默认目标：运行所有测试用例（除了 batch_add_async）
test: test-all

# 初始化环境（安装依赖）
setup:
	@echo "==> 初始化 uv 环境..."
	uv sync
	@echo "✅ 环境初始化完成"

# 运行所有测试用例
test-all:
	@echo "=========================================="
	@echo "开始运行所有测试用例..."
	@echo "=========================================="
	@echo ""
	@echo "📝 1/8 - 创建对话元数据 (create_meta_async.py)"
	@cd examples && $(PYTHON) create_meta_async.py
	@echo ""
	@echo "✅ 1/8 完成"
	@echo ""
	@echo "📝 2/8 - 异步添加记忆 (add_async.py)"
	@cd examples && $(PYTHON) add_async.py
	@echo ""
	@echo "✅ 2/8 完成"
	@echo ""
	@echo "📝 3/8 - 同步添加记忆 (add_sync.py)"
	@cd examples && $(PYTHON) add_sync.py
	@echo ""
	@echo "✅ 3/8 完成"
	@echo ""
	@echo "📝 4/8 - 获取记忆 (get_async.py)"
	@cd examples && $(PYTHON) get_async.py
	@echo ""
	@echo "✅ 4/8 完成"
	@echo ""
	@echo "📝 5/8 - 获取元数据 (get_meta_async.py)"
	@cd examples && $(PYTHON) get_meta_async.py
	@echo ""
	@echo "✅ 5/8 完成"
	@echo ""
	@echo "📝 6/8 - 搜索记忆 (search_async.py)"
	@cd examples && $(PYTHON) search_async.py
	@echo ""
	@echo "✅ 6/8 完成"
	@echo ""
	@echo "📝 7/8 - 更新元数据 (update_meta_async.py)"
	@cd examples && $(PYTHON) update_meta_async.py
	@echo ""
	@echo "✅ 7/8 完成"
	@echo ""
	@echo "📝 8/8 - 删除记忆 (delete_async.py)"
	@cd examples && $(PYTHON) delete_async.py
	@echo ""
	@echo "✅ 8/8 完成"
	@echo ""
	@echo "=========================================="
	@echo "🎉 所有测试用例执行成功！"
	@echo "=========================================="

# 运行批量添加测试（需要文件路径参数）
test-batch:
	@echo "📝 批量添加记忆 (batch_add_async.py)"
	@if [ -z "$(FILE)" ]; then \
		echo "❌ 错误: 需要指定文件路径"; \
		echo "用法: make test-batch FILE=path/to/file.txt"; \
		exit 1; \
	fi
	@cd examples && $(PYTHON) batch_add_async.py $(FILE) $(CHUNK_SIZE) $(START) $(MAX)

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
	@echo "  make test          - 运行所有测试用例（默认，除了 batch_add_async）"
	@echo "  make test-all      - 运行所有测试用例（除了 batch_add_async）"
	@echo "  make test-batch    - 运行批量添加测试"
	@echo "                       用法: make test-batch FILE=input.txt [CHUNK_SIZE=1000] [START=1] [MAX=10]"
	@echo "  make test-one      - 运行单个测试用例"
	@echo "                       用法: make test-one SCRIPT=add_async.py"
	@echo "  make clean         - 清理临时文件"
	@echo "  make help          - 显示此帮助信息"
	@echo ""
	@echo "环境变量："
	@echo "  EVERMEMOS_API_KEY              - API密钥（必需）"
	@echo "  EVER_MEM_OS_CLIENT_BASE_URL    - API地址"
	@echo "  EVERMEMOS_GROUP_ID             - 群组ID"
	@echo "  EVERMEMOS_GROUP_NAME           - 群组名称"
	@echo "  EVERMEMOS_SENDER               - 发送者ID"
	@echo "  EVERMEMOS_SENDER_NAME          - 发送者名称"
	@echo ""
	@echo "示例："
	@echo "  make setup                              # 首次使用"
	@echo "  make test"
	@echo "  make test-batch FILE=test.txt CHUNK_SIZE=500"
	@echo "  make test-one SCRIPT=search_async.py"
