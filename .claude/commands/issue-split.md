# Issue分解（/issue-split）

GitHub Issue を sub-issue に分解して、AI が実装可能な単位に分割するコマンドです。

## 目的

大きな GitHub Issue を分析し、**AI（Claude）が `/issue-run` で実装できる粒度**の sub-issue に自動分解する。

## 引数

* `$ARGUMENTS`: 分解対象の GitHub Issue URL または番号
  * URL形式: `https://github.com/owner/repo/issues/123`
  * 番号のみ: `123`
  * **省略した場合**: AI がユーザーに対象 Issue URL を質問します

## 入力前提

* **分解対象の Issue が既に存在すること**
* Issue に「要件」や「完了条件（DoD）」が記載されていることを推奨

## 振る舞い

### Issue URL が指定されていない場合

1. 「どの Issue を分解しますか？Issue URL または番号を教えてください」とユーザーに質問

### Issue URL が指定されている場合

1. **`gh-sub-issue` 拡張のチェック**
   - `gh extension list` で拡張がインストール済みか確認
   - 未インストールの場合:
     - インストールが必要であることを説明
     - `gh extension install yahsan2/gh-sub-issue` を実行して良いか確認
     - ユーザー承認後にインストール実行
     - ユーザーが拒否した場合はコマンドを終了

2. **Issue 内容の取得**
   - URL から Issue 番号を抽出する（URL形式の場合）
   - `gh issue view {番号} --json title,body,comments` で Issue の最新内容を取得

3. **Issue 内容を分析**
   - 「要件」「完了条件（DoD）」セクションを解析
   - 独立して完了可能な単位に分割
   - 各タスクが 1-3 日で完了できる粒度を目安
   - 依存関係が少ない単位に分割

4. **分解案をユーザーに提示（AskUserQuestion ツール使用）**
   - 各 sub-issue のタイトルと概要を表示
   - 分解の理由や粒度の説明
   - タスク間の依存関係があれば明示
   - **AskUserQuestion で承認を求める**

5. **ユーザー確認**
   - 承認 → sub-issue 作成に進む
   - 修正希望 → 分解案を調整して再提示
   - 追加の質問があれば AskUserQuestion で確認

6. **sub-issue を作成**
   - `gh sub-issue create {親issue番号} --title "..." --body "..."` を実行
   - 各 sub-issue の作成結果を報告
   - 作成された sub-issue の番号とタイトルを一覧表示

## 分解の原則

### AI 分析による自動分解

* Issue 本文の「要件」「完了条件（DoD）」を中心に解析
* 独立して完了可能な単位に分割
* 各 sub-issue が 1-3 日で完了できる粒度を目安
* 親 issue ごとに最大 100 個の sub-issue まで追加可能（GitHub の制限）

### GitHub 公式 sub-issue 機能を活用

* `gh-sub-issue` 拡張を使用して sub-issue を作成
* 親子関係は GitHub がネイティブに管理
* GitHub Projects で sub-issue フィールドが自動的に利用可能
* UI からも確認・編集が容易

### 分解粒度の判断基準

* **AI 実行可能性**: `/issue-run` で AI が実装できる具体性がある
* 1 つの sub-issue が 1-3 日で完了できる
* 依存関係が少ない
* 独立してテスト・デプロイ可能
* 実装範囲が明確
* 完了条件（DoD）が検証可能

## Sub-Issue 本文構造

各 sub-issue は以下の構造で作成されます：

```markdown
## 背景・目的
{親issueから継承または抜粋}

## このタスクの範囲
{このsub-issueで実装する具体的な範囲}

## 要件
- {このsub-issue固有の要件}

## 完了条件（DoD）
- [ ] {独立して検証可能な条件}

## 制約・注意事項
{親issueから継承した制約や、このタスク固有の注意点}
```

## 親 Issue の表示

GitHub UI で sub-issue が自動的に表示されます：

* issue 説明の下部に「sub-issue」セクションが自動生成
* 各 sub-issue へのリンクと進捗状態が表示
* GitHub Projects で sub-issue フィールドが利用可能

## 制約（重要）

* **コードを書かない**
* **技術選定・実装方針を書かない**
* **Issue に書かれていない内容を推測で補完しない**
* **分解案は必ずユーザーに確認してから作成する**

## 使用例

```
# Issue URL を指定して分解
/issue-split https://github.com/owner/repo/issues/123

# Issue 番号のみでも可
/issue-split 123

# 省略（AI が質問する）
/issue-split
```

## 前提条件

* GitHub CLI (`gh`) がインストールされ、認証済みであること
* 現在のディレクトリが Git リポジトリであること
* リポジトリに対して Issue 作成権限があること
* **`gh-sub-issue` 拡張がインストールされていること**
  * 未インストールの場合、コマンド実行時に自動でインストールを提案します
  * インストールコマンド: `gh extension install yahsan2/gh-sub-issue`

## gh-sub-issue 拡張について

`gh-sub-issue` は GitHub の公式 sub-issue 機能を CLI から操作するためのサードパーティ拡張です。

### インストール方法

```bash
gh extension install yahsan2/gh-sub-issue
```

### 基本的な使い方

```bash
# 基本的な使い方
gh sub-issue create <親issue番号> --title "タイトル" --body "本文"

# 複数のsub-issueを一度に作成（カンマ区切り）
gh sub-issue create 10 --title "タスク1,タスク2,タスク3"

# ラベル、担当者、マイルストーンを設定
gh sub-issue create 10 --title "バグ修正" --label "bug,priority" --assignee "@me"
```

## 実装完了後の報告フォーマット

```markdown
## Sub-Issue 作成完了報告

### 親 Issue
- #{親issue番号} {親issueのタイトル}

### 作成した Sub-Issue
1. #{sub-issue番号} {タイトル} - {概要}
2. #{sub-issue番号} {タイトル} - {概要}
3. #{sub-issue番号} {タイトル} - {概要}

### 次のステップ
各 sub-issue に対して `/issue-run {番号}` で実装を開始できます。
必要に応じて各 sub-issue で `/issue-update {番号}` を実行して仕様を確認してください。
```

## 実行フロー図

```
Issue 取得
    ↓
gh-sub-issue 拡張チェック
    ↓（未インストールなら提案）
Issue 内容を分析
    ↓
分解案を作成
    ↓
┌─────────────────────────────────────┐
│ AskUserQuestion で承認を求める        │
│   承認 → sub-issue 作成へ            │
│   修正 → 分解案を調整して再提示       │
└─────────────────────────────────────┘
    ↓
gh sub-issue create で作成
    ↓
作成完了報告
```

## コマンド間のワークフロー

```
/issue-create または手動で Issue 作成
         ↓
   /issue-update で検証（推奨）
         ↓
   /issue-split で分解 ← このコマンド
         ↓
   各 sub-issue に対して /issue-run で実装
```

## 次のステップ

Sub-Issue 作成後は、以下を実行してください：

1. 各 sub-issue の内容を確認
2. 必要に応じて `/issue-update {sub-issue番号}` で仕様を検証
3. `/issue-run {sub-issue番号}` で実装を開始
4. すべての sub-issue が完了したら親 issue をクローズ

## 参考リンク

* [GitHub 公式ドキュメント - sub-issue の追加](https://docs.github.com/ja/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues)
* [gh-sub-issue 拡張](https://github.com/yahsan2/gh-sub-issue)
