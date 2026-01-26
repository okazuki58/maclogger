---
name: e2e-test
description: |
  Playwright E2Eテスト作成ガイド。ユーザーが「E2Eテストを書いて」「Playwrightテストを追加して」「この機能のテストを作成して」と言った時に使用。テストファイルの構造、セレクタパターン、アサーション方法、プロジェクト固有の画面遷移パターンを提供。
---

# E2E Test Guide

## Quick Start

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.setTimeout(120 * 1000);

  test.beforeEach(async ({ page }) => {
    // Setup: navigate to target page
  });

  test('should do something', async ({ page }) => {
    // Test implementation
  });
});
```

## File Location

- テストファイル: `tests/e2e/*.spec.ts`
- フィクスチャ: `tests/fixtures/*.ts`

## Run Tests

```bash
npm run test:e2e                              # 全テスト実行
npm run test:e2e -- tests/e2e/xxx.spec.ts     # 特定ファイル
npm run test:e2e -- --headed                  # ブラウザ表示
```

## Selector Patterns (優先順)

1. **Role-based** (推奨): `page.getByRole('button', { name: '保存' })`
2. **Label/Text**: `page.getByText('項目を追加')`
3. **aria-label**: `page.locator('button[aria-label="項目を挿入"]')`
4. **ID/Class**: `page.locator('#itemName')`, `page.locator('.text-destructive')`
5. **SVG icon**: `page.locator('svg.lucide-plus')`

## Common Patterns

### Wait for navigation
```typescript
await page.waitForURL(/\/projects\/[^/]+\/estimate/, { timeout: 30000 });
await page.waitForLoadState('networkidle');
```

### Hover interaction
```typescript
await element.hover();
await page.waitForTimeout(300);  // transition待ち
```

### Modal handling
```typescript
const modal = page.locator('[role="dialog"]');
await expect(modal).toBeVisible();
await page.keyboard.press('Escape');
await expect(modal).not.toBeVisible();
```

### Dropdown menu
```typescript
await trigger.click();
const menu = page.locator('[role="menu"]');
await expect(menu).toBeVisible();
await page.getByRole('menuitem', { name: 'メニュー項目' }).click();
```

### CSS property assertion
```typescript
await expect(element).toHaveCSS('opacity', '1');
await expect(element).toHaveCSS('background-color', 'rgb(243, 244, 246)');
```

### Element size assertion
```typescript
const box = await element.boundingBox();
expect(box?.width).toBe(24);
expect(box?.height).toBe(24);
```

## Best Practices

- **console.log禁止**: テストは自己文書化されるべき
- **タイムアウト**: `test.setTimeout(120 * 1000)` を設定
- **待機**: `waitForTimeout` は最小限に。`waitForURL`, `expect().toBeVisible()` を優先
- **コメント**: 日本語コメントOK、ただし最小限に
- **アサーション**: 1テスト1目的。複数の検証は分割

## Page Navigation

詳細は [references/pages.md](references/pages.md) を参照。

主要な画面:
- `/projects` - プロジェクト一覧
- `/projects/[id]/estimate` - 見積編集
- `/outsource` - 外注一覧
- `/outsource/new` - 新規外注作成
