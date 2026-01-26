---
paths:
  - "**/*"
---
# Dandori プロジェクト基本ルール

## プロジェクト概要
- 見積もり作成支援システム (atoyoro-mitsumori)
- Next.js 16 + TypeScript + Prisma + PostgreSQL

## 技術スタック
- **フレームワーク**: Next.js 16 (App Router)
- **UI**: Radix UI + Tailwind CSS + shadcn/ui
- **DB**: PostgreSQL + Prisma ORM
- **認証**: Clerk
- **AI**: OpenAI API
- **テスト**: Playwright (E2E)

## ディレクトリ構造
```
app/           # ページ、API、Server Actions
├── actions/   # Server Actions
├── api/       # REST API ルート
├── services/  # 外部サービス連携
components/    # UIコンポーネント
├── ui/        # shadcn/ui ベースコンポーネント
lib/           # ビジネスロジック、ユーティリティ
├── data/      # CSVデータ、マスター
├── estimate/  # 見積生成ロジック
├── mocks/     # モックデータ
prisma/        # DBスキーマ
tests/e2e/     # E2Eテスト
```

## インポート規則
1. パスエイリアス `@/` を必ず使用
2. 相対パス (`../`) は禁止

```typescript
// Good
import { db } from '@/lib/db';
import { Button } from '@/components/ui/button';

// Bad
import { db } from '../../../lib/db';
```

## 命名規則
| 対象 | 規則 | 例 |
|------|------|-----|
| ファイル名 | kebab-case | `estimate-item-row.tsx` |
| コンポーネント | PascalCase | `EstimateItemRow` |
| 関数 | camelCase | `generateEstimate` |
| 定数 | UPPER_SNAKE_CASE | `MOCK_ESTIMATE_ITEMS` |
| 型/インターフェース | PascalCase | `EstimateItemData` |

## 言語
- コード内のコメント: 日本語OK
- ユーザー向けメッセージ: 日本語
- 変数名・関数名: 英語

## 開発コマンド
```bash
npm run dev          # 開発サーバー
npm run check        # 型チェック + lint
npm run test:e2e     # E2Eテスト
npm run db:migrate:local  # DBマイグレーション
```
