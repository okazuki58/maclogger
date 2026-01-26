---
name: weekly-reconcile
description: 週次目標ファイルとmaclogger週報を突合し、計画vs実績のレポートを生成するスキル。「突合して」「今週の振り返りして」「計画と実績を比較して」などのリクエストで発動。評価シートの振り返り作成を支援する。
---

# 週次突合スキル

週次目標ファイル（plan）とmaclogger週報（report）を突合し、計画vs実績のレポートを生成する。

## 発動トリガー

- 「突合して」「計画と実績を比較して」
- 「今週の振り返りして」「週次レビューして」
- 「達成率出して」「何ができた？」
- 週報と計画ファイルを両方アップロードされたとき

## ファイル構成

```
maclogger/
├── weekly-plans/
│   └── 2026-W04-plan.md    # 入力: 週次目標
├── reports/
│   └── 2026-W04.md         # 入力: maclogger週報
└── reconcile/
    └── 2026-W04-reconcile.md  # 出力: 突合結果
```

## 突合レポートのフォーマット

**ファイル名**: `YYYY-WXX-reconcile.md`

```markdown
---
week: "2026-W04"
plan_file: "weekly-plans/2026-W04-plan.md"
report_file: "reports/2026-W04.md"
generated_at: "2026-01-26T10:00:00+09:00"
---

# 週次突合レポート 2026-W04

## サマリ

| 指標 | 値 |
|-----|-----|
| 計画タスク数 | 6 |
| 完了 | 4 |
| 未完了 | 2 |
| 計画外実施 | 3 |
| **達成率** | **67%** |

## 計画タスクの結果

### 本業
- [x] [本業] atoyoro A社フィードバック対応 | 想定: 10h | G2
- [x] [本業] dandori展示会対応 | 想定: 8h | G2

### 改善
- [x] [改善] git-worktree-runner導入 | 想定: 2h | G3, Be sustainable

### アウトプット
- [x] [アウトプット] 評価シート作成 | 想定: 4h | Be sustainable
- [ ] [アウトプット] Claude Code記事公開 | 想定: 5h | Be hungry
  - → 下書きまで完了、W05に公開予定

### 学習
- [ ] [学習] AWS CLF模試2回 | 想定: 3h | Be hungry
  - → 時間確保できず、W05に繰り越し

### ➕ 計画外で実施

- [x] [本業] SIG案件の追加稼働調整 | Be an owner
- [x] [改善] claude-shared リポジトリ整備 | G3, Be sustainable
- [x] [学習] Python/LLM並列実行の技術調査 | Be hungry

## 評価項目別の進捗

### 能力評価

| 項目 | 今週の成果 | 累計進捗 |
|-----|----------|---------|
| G2 | Dandori展示会対応完了 | 100% ✅ |
| G3 | git-worktree-runner, claude-shared | 85% |

### バリュー評価

| 項目 | 今週の成果 | 累計進捗 |
|-----|----------|---------|
| Be hungry | 技術調査実施、記事下書き | 記事2/6, CLF未取得 |
| Be an owner | SIG案件調整、展示会対応 | マイルストーン達成 ✅ |
| Be sustainable | 評価シート支援ツール共有 | Confluence展開開始 |

## 来週への申し送り

### 繰り越しタスク
- [ ] [学習] AWS CLF模試2回 | Be hungry
- [ ] [アウトプット] Claude Code記事公開 | Be hungry

### 今週の学び
- 展示会対応など突発タスクが入ると学習時間が取れない
- 評価シート作成をツール化したのは良かった

### 来週の注意点
- AWS CLFは2月上旬受験目標 → 学習時間を死守
- 記事は「完璧」を目指さず公開優先

## 評価シート振り返り用メモ

以下をコピペして評価シートの振り返りに使える：

```
⚫︎ W04の成果
- Dandori AI展示会対応を完了（進捗9.5割達成）
- git-worktree-runnerによる並行開発フロー確立
- claude-sharedリポジトリを整備し社内共有
- 評価シート作成支援ツールを開発しConfluenceに展開

⚫︎ 証跡
- Dandoriリポジトリ: [URL]
- claude-sharedリポジトリ: [URL]
- Confluenceドキュメント: [URL]
```
```

## 突合ロジック

### Step 1: 計画ファイルのパース

```python
import re

def parse_plan(plan_content):
    """週次目標ファイルからタスクを抽出"""
    tasks = []
    pattern = r'- \[ \] \[(\w+)\] (.+?) \| 想定: (\d+)h \| (.+)'
    
    for match in re.finditer(pattern, plan_content):
        tasks.append({
            'category': match.group(1),
            'description': match.group(2),
            'estimated_hours': int(match.group(3)),
            'evaluation_items': match.group(4).split(', '),
            'status': 'planned'
        })
    
    return tasks
```

### Step 2: 週報のパース

```python
def parse_report(report_content):
    """maclogger週報から作業内容を抽出"""
    # 「今週の成果」セクションを抽出
    # 「各日の作業内容」セクションを抽出
    # キーワードを抽出してマッチング用に保持
    pass
```

### Step 3: マッチング

計画タスクと週報の作業内容をマッチング：

1. **キーワードマッチ**
   - タスク名に含まれるキーワードが週報に出現するか
   - 例: 「Dandori」「AWS」「Claude Code」

2. **カテゴリマッチ**
   - 計画の `[本業]` と週報の開発関連作業
   - 計画の `[学習]` と週報の学習・調査関連

3. **手動確認フラグ**
   - 自動マッチングの確信度が低い場合はフラグを立てる

### Step 4: 結果の集計

```python
def reconcile(plan_tasks, report_activities):
    completed = []      # 計画にあり、週報にもある
    incomplete = []     # 計画にあり、週報にない
    unplanned = []      # 計画になく、週報にある
    
    # マッチング処理...
    
    achievement_rate = len(completed) / len(plan_tasks) * 100
    
    return {
        'completed': completed,
        'incomplete': incomplete,
        'unplanned': unplanned,
        'achievement_rate': achievement_rate
    }
```

## 対話的な突合モード

完全自動マッチングが難しい場合、対話的に確認：

```
以下のタスクは完了しましたか？

1. [学習] AWS CLF模試2回
   → 週報に「AWS」の記載なし
   → [完了 / 未完了 / 一部完了]？

2. [アウトプット] Claude Code記事公開
   → 週報に「評価シート作成支援AI」の記載あり、関連？
   → [完了 / 未完了 / 別タスク]？
```

## 月次・期末の集計

### 月次サマリ

```bash
# W01〜W04の突合結果を集計
reconcile/
├── 2026-W01-reconcile.md
├── 2026-W02-reconcile.md
├── 2026-W03-reconcile.md
├── 2026-W04-reconcile.md
└── 2026-01-monthly-summary.md  # 月次サマリ
```

### 期末サマリ

評価期間終了時に全週の突合結果を集計し、評価シートの振り返りに使えるレポートを生成：

```markdown
# FY2025下半期 評価期間サマリ

## 全体達成率
- 計画タスク総数: 156
- 完了: 128
- **達成率: 82%**

## 評価項目別の累計

| 項目 | 計画 | 完了 | 達成率 |
|-----|-----|-----|-------|
| G2 | 24 | 24 | 100% |
| G3 | 18 | 15 | 83% |
| Be hungry | 36 | 28 | 78% |
| Be an owner | 12 | 12 | 100% |
| Be sustainable | 24 | 20 | 83% |

## 主な成果（評価シート用）
1. atoyoroプロトタイプ開発・stgデプロイ完了
2. 開発プロセス自動化（Claude Code, git-worktree-runner）
3. 技術記事6本公開、社内Qiita賞受賞
4. ...
```

## Tips

### 週報のフォーマット改善提案

突合精度を上げるために、maclogger週報に以下を追加すると良い：

1. **カテゴリタグ**
   ```markdown
   - [本業] Dandori外注作成ウィザードの実装
   - [改善] git-worktree-runner導入
   ```

2. **評価項目タグ**（任意）
   ```markdown
   - [本業][G2] Dandori外注作成ウィザードの実装
   ```

### 振り返りのコツ

- 未完了タスクは「なぜ」を1行で書く
- 計画外タスクも評価項目に紐付ける（アピールポイントになる）
- 「学び」は具体的に、次に活かせる形で