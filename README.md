# macOS Activity Logger

macOSでアクティブウィンドウを自動キャプチャ→OCR→1時間ごとにLLMで要約→好きなタイミングで日報生成。

## 何ができるの？

- 1分ごとに自動でアクティブウィンドウをキャプチャ→OCR
- 1時間ごとにLLMで作業内容を要約
- 好きなタイミングで日報・週報を生成（Markdown形式）

**必要なもの:** macOS、Python 3.7以上、Google Gemini APIキー

## セットアップ（初回のみ）

```bash
# 1. セットアップ（自動で環境構築）
make setup

# 2. APIキーを設定
cp .env.example .env
# .envファイルを開いて GEMINI_API_KEY=your_key を設定

# 3. macOSの権限を許可（初回のみ）
# システム設定 > プライバシーとセキュリティ
# - 画面収録: ターミナルを追加
# - アクセシビリティ: ターミナルを追加
```

## 使い方

```bash
# 始業時: ロギング開始
make start

# 終業時: ロギング停止
make stop

# 日報作成
make report

# 週報作成
make weekly-report
```

これだけです。`make start`すれば、1分ごとにキャプチャ→OCR→1時間ごとに要約が自動で回ります。

## よく使うコマンド

```bash
# 状態確認
make status

# ログ確認
make logs

# 特定の日付の日報を作成
make report DATE=2025-01-05

# 全コマンド確認
make help
```

## 日報の自動生成（オプション）

毎日0時に自動で前日の日報を生成したい場合：

```bash
# 自動生成を有効化
make install-scheduler

# 無効化する場合
make uninstall-scheduler
```

## 技術的な詳細（興味がある人向け）

<details>
<summary>ログフォーマットとディレクトリ構造</summary>

### ログの保存場所

- `logs/activity_YYYY-MM-DD.jsonl`: 1分ごとのアクティビティログ
- `logs/hourly_summary_YYYY-MM-DD.jsonl`: 1時間ごとの要約
- `reports/daily/YYYY-MM-DD.md`: 日報
- `reports/weekly/YYYY-WNN.md`: 週報

### 動作の仕組み

- 1分ごとにアクティブウィンドウをキャプチャ→OCR
- 毎正時(13:00、14:00...)に過去1時間分をLLMで要約
- screenセッションでバックグラウンド実行
- Mac再起動後は手動で`make start`が必要

### API利用料金

- 1時間ごとに要約を生成(gemini-3-pro-preview使用)
- コスト: 非常に低コスト（1日8時間稼働でも数円程度）

</details>

## トラブルシューティング

<details>
<summary>権限エラーが出る</summary>

システム設定 > プライバシーとセキュリティで以下を確認：
- 画面収録: ターミナルを追加
- アクセシビリティ: ターミナルを追加

</details>

<details>
<summary>日報が生成されない</summary>

- `.env`ファイルに`GEMINI_API_KEY`が設定されているか確認
- `make logs`でログを確認してhourly_summaryが生成されているか確認
- `make status`でプロセスが動いているか確認

</details>

<details>
<summary>自動日報生成が動かない</summary>

```bash
# スケジューラが登録されているか確認
launchctl list | grep maclogger

# ログを確認
cat logs/auto_report.log

# 再登録
make uninstall-scheduler
make install-scheduler
```

</details>

## ライセンス

MIT License