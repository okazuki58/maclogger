---
paths:
  - "tests/**/*.ts"
  - "**/*.spec.ts"
---
# テストルール (Playwright E2E)

## テストファイル配置
```
tests/
├── e2e/
│   ├── mock-flow-verification.spec.ts
│   └── outsource-flow.spec.ts
└── fixtures/
    └── sample-memo.ts
```

## 基本構造

```typescript
import { test, expect } from '@playwright/test';

test.describe('見積作成フロー', () => {
  test.beforeEach(async ({ page }) => {
    // 共通セットアップ
    await page.goto('/projects/new');
  });

  test('新規プロジェクトを作成できる', async ({ page }) => {
    // Arrange
    const projectName = 'テストプロジェクト';

    // Act
    await page.fill('[data-testid="project-name"]', projectName);
    await page.click('[data-testid="submit-button"]');

    // Assert
    await expect(page).toHaveURL(/\/projects\/[\w-]+/);
    await expect(page.getByText(projectName)).toBeVisible();
  });
});
```

## ロケータ戦略
優先順位:
1. `data-testid` 属性
2. ロール + アクセシブル名
3. テキストコンテンツ
4. CSSセレクタ (最後の手段)

```typescript
// Good
await page.getByTestId('submit-button').click();
await page.getByRole('button', { name: '保存' }).click();
await page.getByText('見積を作成').click();

// Avoid
await page.click('.btn-primary');
await page.click('#submit');
```

## 待機処理
明示的な待機を使用:

```typescript
// ナビゲーション待機
await page.waitForURL(/\/projects\/[\w-]+/);

// 要素の表示待機
await expect(page.getByTestId('loading')).toBeHidden();
await expect(page.getByText('完了')).toBeVisible();

// API応答待機
await page.waitForResponse(resp =>
  resp.url().includes('/api/projects') && resp.status() === 200
);
```

## タイムアウト設定
このプロジェクトは AI 処理があるため長めのタイムアウト:

```typescript
// 個別テストでタイムアウト延長
test('AI見積生成', async ({ page }) => {
  test.setTimeout(120000); // 2分

  await page.click('[data-testid="generate-estimate"]');
  await expect(page.getByTestId('estimate-table')).toBeVisible({
    timeout: 60000,
  });
});
```

## テストデータ
`tests/fixtures/` にテストデータを配置:

```typescript
// tests/fixtures/sample-memo.ts
export const SAMPLE_MEMO = `
プロジェクト概要:
- Webアプリケーション開発
- ユーザー管理機能
- レポート出力機能
`;

// テストで使用
import { SAMPLE_MEMO } from '../fixtures/sample-memo';

test('議事録入力', async ({ page }) => {
  await page.fill('[data-testid="memo-input"]', SAMPLE_MEMO);
});
```

## 認証
E2E テストユーザーで認証:

```typescript
test.beforeEach(async ({ page }) => {
  // 環境変数から認証情報を取得
  await page.goto('/sign-in');
  await page.fill('[name="email"]', process.env.E2E_TEST_USER_EMAIL!);
  await page.fill('[name="password"]', process.env.E2E_TEST_USER_PASSWORD!);
  await page.click('[type="submit"]');
  await page.waitForURL('/');
});
```

## 実行コマンド
```bash
npm run test:e2e          # 通常実行
npm run test:e2e:ui       # UIモード (デバッグに便利)
npm run test:e2e:headed   # ブラウザ表示
npm run test:e2e:debug    # Playwrightデバッガ
```

## CI での注意
- リトライ: 2回 (不安定性対策)
- スクリーンショット: 失敗時のみ
- ビデオ: 失敗時のみ
