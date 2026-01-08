.PHONY: setup start stop report status logs clean help install-scheduler uninstall-scheduler test-auto-report

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

weekly-report: ## 週報を作成(今週月曜日〜日曜日、または DATE=YYYY-MM-DD で指定週)
	@./scripts/generate_weekly_report.sh --date $(DATE)

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

install-scheduler: ## 日報自動生成をlaunchdに登録（毎日0時に自動実行）
	@echo "Installing daily report scheduler..."
	@mkdir -p ~/Library/LaunchAgents
	@cp launchd/com.maclogger.daily-report.plist ~/Library/LaunchAgents/
	@launchctl load ~/Library/LaunchAgents/com.maclogger.daily-report.plist
	@echo "✓ Scheduler installed!"
	@echo ""
	@echo "Daily reports will be automatically generated at midnight (0:00)"
	@echo "Check logs at: logs/auto_report.log"
	@echo ""
	@echo "To verify: launchctl list | grep maclogger"
	@echo "To test now: make test-auto-report"uninstall-scheduler: ## 日報自動生成をlaunchdから削除
	@echo "Uninstalling daily report scheduler..."
	@launchctl unload ~/Library/LaunchAgents/com.maclogger.daily-report.plist 2>/dev/null || true
	@rm -f ~/Library/LaunchAgents/com.maclogger.daily-report.plist
	@echo "✓ Scheduler uninstalled"

test-auto-report: ## 自動日報生成スクリプトを手動テスト
	@echo "Running auto report generation test..."
	@./scripts/auto_generate_daily_report.sh
