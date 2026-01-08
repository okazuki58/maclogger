# macOS Activity Logger

macOSでアクティブウィンドウを自動的にキャプチャし、OCRでテキストを抽出して1分ごとにJSONLログを記録、1時間ごとにLLMで要約するツールです。好きなタイミングで日報を生成できます。

## クイックスタート

```bash
# セットアップ
make setup

# APIキーを設定（.envファイルを作成）
echo "OPENAI_API_KEY=your_key_here" > .env

# 始業時
make start

# 終業時
make stop

# 日報作成
make report
```

## 主な用途

- 日報作成の自動化
- 1日の作業内容を自動的に記録
- 好きなタイミングで日報を生成

## 機能

- アクティブウィンドウのアプリケーション名とタイトルを取得
- アクティブウィンドウのみをキャプチャ(マルチモニター対応)
- Vision FrameworkによるOCR処理(日本語・英語対応)
- 1時間ごとに作業内容をまとめて要約(OpenAI gpt-5-mini)
- JSONL形式での活動ログ記録
- 任意のタイミングで日報を生成(Markdown形式)

## 必要な環境

- macOS (Vision Frameworkを使用)
- Python 3.7以上
- OpenAI APIキー

## インストール

### 1. リポジトリをクローン

```bash
git clone <repository-url> maclogger
cd maclogger
```

### 2. セットアップ

**Makefileを使う場合（推奨）:**

```bash
make setup
```

**手動でセットアップする場合:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate  # インストール完了後は抜けてOK

chmod +x scripts/start_maclogger.sh scripts/stop_maclogger.sh scripts/generate_report.sh
```

### 3. OpenAI APIキーを設定

**方法1: .envファイルを作成（推奨）**

プロジェクトルートに`.env`ファイルを作成して設定します：

```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

または、エディタで`.env`ファイルを作成して以下を記述：

```
OPENAI_API_KEY=your_openai_api_key_here
```

**方法2: 環境変数として設定（一時的）**

シェルセッションごとに設定する場合：

```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

この場合、ターミナルを閉じると設定が消えます。永続化するには`~/.zshrc`や`~/.bashrc`に追記してください。

### 4. macOS権限を設定

このツールは以下の権限が必要です:

#### スクリーンレコーディング権限

1. システム設定 > プライバシーとセキュリティ > 画面収録
2. ターミナル(またはPythonを実行するアプリ)を追加

#### アクセシビリティ権限

1. システム設定 > プライバシーとセキュリティ > アクセシビリティ
2. ターミナル(またはPythonを実行するアプリ)を追加

## 実行方法

### 基本的な使い方

**Makefileを使う場合（推奨）:**

```bash
# 始業時: ロギング開始
make start

# 終業時: ロギング停止
make stop

# 日報作成（DATE指定なし = 当日の日報）
make report

# 特定の日付の日報を作成
make report DATE=2025-12-22

# 状態確認
make status

# ログ確認
make logs

# ヘルプ表示
make help
```

**シェルスクリプトを直接使う場合:**

```bash
# 始業時: ロギング開始
./scripts/start_maclogger.sh

# 終業時: ロギング停止
./scripts/stop_maclogger.sh

# 日報作成（引数なし = 当日の日報）
./scripts/generate_report.sh

# 特定の日付の日報を作成
./scripts/generate_report.sh --date 2025-12-22
```

### 動作内容

実行すると:
- 1分ごとにアクティブウィンドウをキャプチャ
- OCRでテキスト抽出
- `logs/activity_YYYY-MM-DD.jsonl`にログを記録
- 毎正時(13:00、14:00、15:00...)に過去1時間分をLLMで要約
  - 例: 13:45に起動した場合、次の要約は14:00に生成
  - 起動からの経過時間ではなく、時計の時刻に基づきます
- `logs/hourly_summary_YYYY-MM-DD.jsonl`に時間ごとの要約を保存

**日報作成について:**
- `make report`（引数なし）→ 当日の日報を自動生成
- `make report DATE=2025-12-22`（日付指定）→ 指定日の日報を生成
- 生成された日報は`reports/YYYY-MM-DD.md`に保存されます

### 管理コマンド

```bash
# 状態確認
screen -ls | grep maclogger

# 画面に接続（動作確認）
screen -r maclogger
# 接続を解除するには: Ctrl+A, D

# 本日のログを確認
tail -f logs/activity_$(date +%Y-%m-%d).jsonl
```

**注意**: screenセッションはMacを再起動すると終了します。再起動後は`make start`で再度起動してください。

## 日報の自動生成

毎日0時に前日の日報を自動生成するように設定できます。

### セットアップ

```bash
# 日報自動生成を有効化（launchdに登録）
make install-scheduler
```

これで、**毎日0時0分に自動的に前日の日報が生成**されるようになります。

例:
- 12月30日 0:00 → 12月29日の日報を生成
- 12月31日 0:00 → 12月30日の日報を生成

### 確認方法

```bash
# 登録されているか確認
launchctl list | grep maclogger

# ログを確認
cat logs/auto_report.log

# 手動でテスト実行
make test-auto-report
```

### 通知

日報生成が完了すると、macOSの通知センターで結果を確認できます:
- 成功時: "Daily report generated for YYYY-MM-DD"
- 失敗時: "Failed to generate daily report"

### 無効化する場合

```bash
# 日報自動生成を無効化
make uninstall-scheduler
```

### 注意事項

- **Macの電源が入っている必要があります**（スリープ中でもOK）
- 0:00時点でスリープ中の場合、起動時に実行されます
- OpenAI APIキーが設定されている必要があります
- hourly_summaryが存在しない日は日報が生成されません

## ログフォーマット

### アクティビティログ (`logs/activity_YYYY-MM-DD.jsonl`)

```json
{
  "timestamp": "2025-12-23T10:30:45.123456+09:00",
  "application": "Google Chrome",
  "window_title": "GitHub - Project Overview",
  "ocr_text": "GitHub logo... pull requests... issues..."
}
```

### 時間ごとの要約 (`logs/hourly_summary_YYYY-MM-DD.jsonl`)

```json
{
  "timestamp": "2025-12-23T11:00:00.123456+09:00",
  "hour": "11:00",
  "activities_count": 60,
  "summary": "Cursorでmacloggerプロジェクトを開発。OCR機能の実装とデバッグを行い、動作確認。Slackでチームとコミュニケーション。"
}
```

## 日報サンプル

日報は`reports/YYYY-MM-DD.md`に保存されます。

```markdown
# 業務日報 - 2025年12月23日

## 本日の主な作業

### プロジェクトA - 機能開発
- 新機能のコーディング(VS Code、3時間)
- GitHubでコードレビュー対応(30分)

### 資料作成
- プレゼン資料をKeynoteで作成(1時間)

### コミュニケーション
- Slackでチーム連絡、メール対応(30分)

## 使用ツール
- VS Code、Google Chrome、Slack、Keynote

## 所感
新機能の実装が順調に進んだ。明日はテストを実施予定。
```

## 設定のカスタマイズ

環境変数で設定を変更できます:

- `OPENAI_API_KEY`: OpenAI APIキー(必須)

## ディレクトリ構造

```
maclogger/
├── src/                            # Pythonスクリプト
│   ├── maclogger.py                # メインスクリプト
│   └── generate_report.py          # 日報生成スクリプト
├── scripts/                        # シェルスクリプト
│   ├── start_maclogger.sh          # 起動スクリプト
│   ├── stop_maclogger.sh           # 停止スクリプト
│   └── generate_report.sh          # 日報生成実行スクリプト
├── Makefile                        # コマンド短縮用
├── requirements.txt                # 依存パッケージ
├── README.md                       # このファイル
├── .env                            # 環境変数(作成してください)
├── .gitignore                      # Gitで無視するファイル
├── venv/                           # Python仮想環境
├── logs/                           # ログディレクトリ(自動作成)
│   ├── activity_YYYY-MM-DD.jsonl   # 1分ごとの活動ログ
│   └── hourly_summary_YYYY-MM-DD.jsonl # 1時間ごとの要約
└── reports/                        # 日報ディレクトリ(自動作成)
    └── YYYY-MM-DD.md               # 日報
```

## 注意事項

- OCRの精度は完璧ではありません。ローカル処理のため、コストを抑えています。
- スクリーンショットは一時ファイルとして作成され、処理後に自動削除されます。
- **OpenAI APIの利用料金**:
  - 1時間ごとに要約を生成(gpt-5-mini使用)
  - コスト: 約$0.002/時間、1日8時間稼働で約$0.016(約2円)
  - 1分ごとの要約と比べて約1/60のコストに削減
- 日報は1日1回、指定時刻に自動生成されます。既に生成済みの場合は上書きしません。
- マルチモニター環境でも、アクティブなウィンドウのみをキャプチャします。
- **バックグラウンド実行**:
  - screenを使用してバックグラウンドで実行できます
  - ターミナルを閉じても動作し続けます
  - スリープから復帰しても継続します
  - 注意: Mac再起動後は手動で再起動が必要です
- **macOSの制約**:
  - launchdでのデーモン化はスクリーンキャプチャの権限制約により動作しません
  - GUI環境で実行する必要があります

## トラブルシューティング

### "Error: pyobjc-framework-Vision and pyobjc-framework-Quartz are required."

```bash
pip install pyobjc-framework-Vision pyobjc-framework-Quartz
```

### "Warning: OPENAI_API_KEY not set."

環境変数にOpenAI APIキーを設定してください:

```bash
export OPENAI_API_KEY=your_key
```

### スクリーンショットが撮れない

システム設定でスクリーンレコーディング権限を確認してください。

### アクティブウィンドウ情報が取得できない

システム設定でアクセシビリティ権限を確認してください。

### 日報自動生成が動作しない

#### スケジューラが登録されているか確認

```bash
launchctl list | grep maclogger
```

`com.maclogger.daily-report`が表示されれば正常に登録されています。

#### ログを確認

```bash
# 自動実行のログ
cat logs/auto_report.log

# launchdの標準出力
cat logs/launchd_stdout.log

# launchdのエラー出力
cat logs/launchd_stderr.log
```

#### 手動でテスト実行

```bash
make test-auto-report
```

これで正常に動作すれば、launchdの設定に問題があります。

#### よくある問題

- **OPENAI_API_KEYが設定されていない**: `.env`ファイルを確認
- **hourly_summaryがない**: 日報生成にはhourly_summaryが必要です
- **パスが間違っている**: plistファイル内のパスを確認
- **権限の問題**: `chmod +x scripts/auto_generate_daily_report.sh`を実行

#### スケジューラの再登録

```bash
# 一度削除
make uninstall-scheduler

# 再登録
make install-scheduler
```

## ライセンス

MIT License


