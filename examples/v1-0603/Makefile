# examples/v1-0603 — everos_cloud SDK 示例运行 Makefile
#
# 用法：
#   make help            查看所有 target
#   make install         安装 everos_cloud wheel 到 $(PYTHON)
#   make smoke           跑综合冒烟测试 test_dev.py
#   make basic           跑 01–12 基础示例
#   make cookbook        跑 cookbook 三个完整流程
#   make multimodal      跑多模态 add/search/get/audio
#   make all             以上全部
#
# 可覆盖变量：
#   PYTHON=python3                       指定解释器
#   EVEROS_API_KEY=xxx                   覆盖 API Key（默认用示例内置 dev key）
#   EVER_OS_BASE_URL=https://...         覆盖网关地址
#   WHEEL=https://.../everos_cloud-*.whl  install 用的 wheel 地址

PYTHON ?= /opt/miniconda3/bin/python3
WHEEL  ?= https://pkg.stainless.com/s/everos-python/e6ddf185ee0fcbc1dbb34bdcc91f28e4691100fb/everos_cloud-0.4.0-py3-none-any.whl

BASIC := 01_add_sync 02_search_sync 03_get_sync 04_delete_flush 05_agent_memories \
         06_add_async 07_search_async 08_get_async 09_delete_async 10_task_status \
         11_object_sign 12_groups_senders
COOKBOOK := quickstart_sdk_sync quickstart_sdk_async quickstart_sdk_complete
MULTIMODAL := 01_add_multimodal 02_search_multimodal 03_get_multimodal 04_add_audio_multimodal

.DEFAULT_GOAL := help
.PHONY: help install version smoke basic cookbook multimodal all clean

help: ## 显示本帮助
	@echo "everos_cloud 示例 (examples/v1-0603)"
	@echo ""
	@grep -E '^[a-zA-Z0-9_%-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "解释器: PYTHON=$(PYTHON)"

install: ## 安装 everos_cloud wheel（WHEEL=... 可覆盖）
	$(PYTHON) -m pip install --force-reinstall "$(WHEEL)"

version: ## 打印已安装的 everos_cloud 版本
	@$(PYTHON) -c "import everos_cloud; print('everos_cloud', getattr(everos_cloud,'__version__','?'))"

smoke: ## 综合冒烟测试（add→flush→search→get→agent→delete）
	$(PYTHON) test_dev.py

basic: ## 跑 01–12 基础示例
	@for f in $(BASIC); do \
	  echo "──── $$f ────"; \
	  $(PYTHON) $$f.py || echo "❌ $$f FAILED"; \
	done

cookbook: ## 跑 cookbook 三个完整流程
	@for f in $(COOKBOOK); do \
	  echo "──── cookbook/$$f ────"; \
	  $(PYTHON) cookbook/$$f.py || echo "❌ $$f FAILED"; \
	done

multimodal: ## 跑多模态示例（add/search/get/audio，含上传，较慢）
	@for f in $(MULTIMODAL); do \
	  echo "──── multimodal/$$f ────"; \
	  (cd multimodal && $(PYTHON) $$f.py) || echo "❌ $$f FAILED"; \
	done

all: smoke basic cookbook multimodal ## 跑全部示例

# ── 单个 target（make basic-01_add_sync / mm-01_add_multimodal 等）────────────
basic-%: ## 跑单个基础示例，如 make basic-01_add_sync
	$(PYTHON) $*.py

cookbook-%: ## 跑单个 cookbook，如 make cookbook-quickstart_sdk_sync
	$(PYTHON) cookbook/$*.py

mm-%: ## 跑单个多模态示例，如 make mm-01_add_multimodal
	cd multimodal && $(PYTHON) $*.py

clean: ## 清理 __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
