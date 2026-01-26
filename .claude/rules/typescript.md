---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---
# TypeScript ルール

## 厳格な型チェック
このプロジェクトは `strict: true` で運用。以下を遵守:

1. **`any` 禁止** - 必ず具体的な型を指定
2. **暗黙的なany禁止** - 関数パラメータには必ず型注釈
3. **nullチェック必須** - `strictNullChecks` 有効

```typescript
// Good
function processItem(item: EstimateItem): number {
  return item.quantity * item.unitPrice;
}

// Bad
function processItem(item: any) {
  return item.quantity * item.unitPrice;
}
```

## 未使用パラメータ
未使用のパラメータには `_` プレフィックスを付ける:

```typescript
// Good
export async function searchSimilarCases(
  _query: string,  // 現在モック実装のため未使用
  limit = 10
): Promise<SimilarCase[]> {
  return MOCK_SIMILAR_CASES.slice(0, limit);
}
```

## 型定義の配置
- 複数ファイルで使用する型: `lib/types/` または関連する `lib/*.ts` に定義
- コンポーネント固有の型: 同一ファイル内で定義

## Zodバリデーション
フォーム入力やAPIリクエストには Zod スキーマを使用:

```typescript
import { z } from 'zod';

const EstimateItemSchema = z.object({
  itemName: z.string().min(1, '品目名は必須です'),
  quantity: z.number().positive('数量は正の数で指定'),
  unitPrice: z.number().min(0, '単価は0以上'),
});

type EstimateItemInput = z.infer<typeof EstimateItemSchema>;
```

## Non-null Assertion
`!` の使用は最小限に。代わりに:
- オプショナルチェイニング `?.`
- Nullish coalescing `??`
- 型ガード関数

```typescript
// Avoid
const name = user!.name;

// Prefer
const name = user?.name ?? 'Unknown';
```

## 関数の戻り値型
複雑な関数には明示的な戻り値型を指定:

```typescript
// Good - 明示的な戻り値型
async function generateEstimate(
  projectId: string
): Promise<{ success: true; items: EstimateItem[] } | { success: false; error: string }> {
  // ...
}
```
