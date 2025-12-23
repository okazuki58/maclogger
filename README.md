# macOS Activity Logger

macOSでアクティブウィンドウを自動的にキャプチャし、OCRでテキストを抽出、LLMで要約して1分ごとにJSONLログを記録し、毎日18:00に日報を自動生成するツールです。

## 主な用途

- 日報作成の自動化
- 1日の作業内容を自動的に記録
- 業務終了時に日報を自動生成

## 機能

- アクティブウィンドウのアプリケーション名とタイトルを取得
- アクティブウィンドウのみをキャプチャ(マルチモニター対応)
- Vision FrameworkによるOCR処理(日本語・英語対応)
- 1時間ごとに作業内容をまとめて要約(OpenAI gpt-5-mini)
- JSONL形式での活動ログ記録
- 毎日18:00に日報を自動生成(Markdown形式)

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

### 2. 依存パッケージをインストール

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# インストール完了後は抜けてOK（起動時に自動でvenvが使われます）
deactivate
```

必要なパッケージ:
- `pyobjc-framework-Vision`: macOS Vision Framework
- `pyobjc-framework-Quartz`: 画像処理
- `openai`: OpenAI API
- `python-dotenv`: 環境変数管理

### 3. 環境変数を設定

```bash
cp .env.example .env
OPENAI_API_KEY=your_openai_api_key_here
```


### 4. macOS権限を設定

このツールは以下の権限が必要です:

#### スクリーンレコーディング権限

1. システム設定 > プライバシーとセキュリティ > 画面収録
2. ターミナル(またはPythonを実行するアプリ)を追加

#### アクセシビリティ権限

1. システム設定 > プライバシーとセキュリティ > アクセシビリティ
2. ターミナル(またはPythonを実行するアプリ)を追加

## 実行方法

### バックグラウンドで実行（推奨）

screenを使ってバックグラウンドで実行します。ターミナルを閉じても動き続けます。

#### 起動

```bash
# 実行権限を付与（初回のみ）
chmod +x start_maclogger.sh stop_maclogger.sh

# バックグラウンドで起動
./start_maclogger.sh
```

#### 管理コマンド(オプション)

```bash
# 状態確認
screen -ls | grep maclogger

# 画面に接続（動作確認）
screen -r maclogger
# 接続を解除するには: Ctrl+A, D

# 停止
./stop_maclogger.sh

# ログ確認
tail -f logs/activity_*.jsonl
```

**注意**: screenセッションはMacを再起動すると終了します。再起動後は`./start_maclogger.sh`で再度起動してください。

実行すると:
- 1分ごとにアクティブウィンドウをキャプチャ
- OCRでテキスト抽出
- `logs/activity_YYYY-MM-DD.jsonl`にログを記録
- 毎正時(13:00、14:00、15:00...)に過去1時間分をLLMで要約
  - 例: 13:45に起動した場合、次の要約は14:00に生成
  - 起動からの経過時間ではなく、時計の時刻に基づきます
- `logs/hourly_summary_YYYY-MM-DD.jsonl`に時間ごとの要約を保存
- 18:00になったら自動で日報を生成(`reports/YYYY-MM-DD.md`)

### 手動実行

```bash
python maclogger.py
```

停止するには`Ctrl+C`を押してください。

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
- `REPORT_TIME`: 日報生成時刻(デフォルト: 18:00)

## ディレクトリ構造

```
maclogger/
├── maclogger.py                    # メインスクリプト
├── requirements.txt                # 依存パッケージ
├── README.md                       # このファイル
├── .env                            # 環境変数(作成してください)
├── .gitignore                      # Gitで無視するファイル
├── com.maclogger.plist             # launchd設定ファイル
├── install_daemon.sh               # デーモンインストールスクリプト
├── uninstall_daemon.sh             # デーモンアンインストールスクリプト
├── venv/                           # Python仮想環境
├── logs/                           # ログディレクトリ(自動作成)
│   ├── activity_YYYY-MM-DD.jsonl   # 1分ごとの活動ログ
│   ├── hourly_summary_YYYY-MM-DD.jsonl # 1時間ごとの要約
│   ├── daemon.log                  # デーモンの標準出力
│   └── daemon.err                  # デーモンのエラー出力
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

## ライセンス

MIT License


