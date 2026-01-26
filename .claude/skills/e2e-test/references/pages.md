# Page Navigation Reference

## 画面一覧

| パス | 画面名 | 説明 |
|------|--------|------|
| `/projects` | プロジェクト一覧 | 案件リスト表示 |
| `/projects/new` | 新規案件作成 | 議事録入力から開始 |
| `/projects/[id]/parameters` | パラメータ入力 | イベント要件確認 |
| `/projects/[id]/estimate` | 見積編集 | 見積項目の編集 |
| `/outsource` | 外注一覧 | 外注品目リスト |
| `/outsource/new` | 新規外注作成 | 3ステップウィザード |
| `/outsource/[id]` | 外注詳細 | 外注品目詳細 |

## 共通セットアップパターン

### 見積編集画面へのアクセス

```typescript
test.beforeEach(async ({ page }) => {
  await page.goto('/projects');
  await expect(page).toHaveURL('/projects');

  const projectRow = page.locator('a[href*="/estimate"]').first();
  await expect(projectRow).toBeVisible({ timeout: 10000 });
  await projectRow.click();

  await page.waitForURL(/\/projects\/[^/]+\/estimate/, { timeout: 30000 });
  await page.waitForLoadState('networkidle');
});
```

### 外注一覧画面へのアクセス

```typescript
test.beforeEach(async ({ page }) => {
  await page.goto('/outsource');
  await expect(page).toHaveURL('/outsource');
});
```

### 新規案件作成フロー

```typescript
test.beforeEach(async ({ page }) => {
  await page.goto('/projects');
  const newButton = page.getByRole('link', { name: /新規案件作成/i }).first();
  await newButton.click();
  await expect(page).toHaveURL('/projects/new');
});
```

## 見積編集画面の要素

### テーブル構造

| 要素 | セレクタ |
|------|----------|
| 項目行 | `tbody tr` (with `svg.lucide-grip-vertical`) |
| カテゴリ行 | `tbody tr` (with chevron icon) |
| ドラッグハンドル | `svg.lucide-grip-vertical` |
| 展開ボタン | `button` with `svg.lucide-chevron-right` |
| 折りたたみボタン | `button` with `svg.lucide-chevron-down` |
| +ボタン（挿入） | `button[aria-label="項目を挿入"]` |
| 項目を追加行 | `tr` with text `項目を追加` |

### 編集フィールド

| フィールド | セレクタ |
|------------|----------|
| 項目名 | インライン編集（クリックで`input`表示） |
| 単価 | インライン編集 |
| 数量 | インライン編集 |
| 重要度 | `Select` コンポーネント |
| 詳細説明 | 展開後に `textarea` |

### モーダル

| モーダル | トリガー | セレクタ |
|----------|----------|----------|
| 項目追加 | +ボタン or 「項目を追加」行 | `[role="dialog"]` |

## 外注画面の要素

### 一覧画面

| 要素 | セレクタ |
|------|----------|
| 新規作成ボタン | `button` with `/新規作成/i` |
| ソートボタン | `columnheader` 内の `button` |
| 発注済非表示 | `button` with `/発注済を非表示/i` |
| 行クリック | `tr` の nth(1) 以降 |

### 新規作成ウィザード

| ステップ | 主要要素 |
|----------|----------|
| Step 1 | `#description` (textarea) |
| Step 2 | `#itemName`, `[id^="supplier-"]` (checkboxes) |
| Step 3 | 確認画面、送信ボタン |

## フィクスチャ

テストデータは `tests/fixtures/` に配置:

```typescript
// tests/fixtures/sample-memo.ts
import { SAMPLE_MEMO, SHORT_SAMPLE_MEMO } from '../fixtures/sample-memo';
```
