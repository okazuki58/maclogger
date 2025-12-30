.PHONY: setup start stop report status logs clean help

# デフォルトターゲット
.DEFAULT_GOAL := help

# 環境変数
VENV = venv
PYTHON = $(VENV)/bin/python
DATE ?= $(shell date +%Y-%m-%d)

help: ## ヘルプを表示
	@echo "macOS Activity Logger - 利用可能なコマンド:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## 初期セットアップ（venv作成、パッケージインストール、実行権限付与）
	@echo "Setting up maclogger..."
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt
	chmod +x scripts/start_maclogger.sh scripts/stop_maclogger.sh scripts/generate_report.sh scripts/generate_weekly_report.sh
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Set your OpenAI API key: export OPENAI_API_KEY=your_key"
	@echo "  2. Start logging: make start"

start: ## 始業時: ロギングを開始
	@./scripts/start_maclogger.sh

stop: ## 終業時: ロギングを停止
	@./scripts/stop_maclogger.sh

report: ## 日報を作成 (使用例: make report DATE=2025-12-22)
	@./scripts/generate_report.sh --date $(DATE)

weekly-report: ## 週報を作成(今週月曜日〜日曜日)
	@./scripts/generate_weekly_report.sh

status: ## 実行状態を確認
	@echo "maclogger status:"
	@screen -ls | grep maclogger || echo "Not running"

logs: ## 本日のアクティビティログを表示
	@tail -f logs/activity_$(shell date +%Y-%m-%d).jsonl

clean: ## ログファイルを削除（注意: 全てのログが削除されます）
	@read -p "Delete all logs? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -rf logs/*.jsonl reports/daily/*.md reports/weekly/*.md; \
		echo "✓ Logs deleted"; \
	else \
		echo "Cancelled"; \
	fi

