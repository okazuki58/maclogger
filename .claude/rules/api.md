---
paths:
  - "app/api/**/*.ts"
  - "app/actions/**/*.ts"
---
# API / Server Actions ルール

## Server Actions 優先
新規機能では API ルート (`app/api/`) より Server Actions (`app/actions/`) を優先:

```typescript
// app/actions/projects/estimate.ts
'use server';

import { db } from '@/lib/db';

export async function generateEstimate(projectId: string) {
  // 見積生成ロジック
  const result = await db.estimateItem.findMany({
    where: { projectId },
  });

  return { success: true, items: result };
}
```

## 戻り値パターン
成功/失敗を明示的に返す:

```typescript
type ActionResult<T> =
  | { success: true; data: T }
  | { success: false; error: string };

export async function updateProject(
  projectId: string,
  data: ProjectUpdateInput
): Promise<ActionResult<Project>> {
  try {
    const project = await db.project.update({
      where: { id: projectId },
      data,
    });
    return { success: true, data: project };
  } catch (error) {
    console.error('Project update failed:', error);
    return { success: false, error: 'プロジェクトの更新に失敗しました' };
  }
}
```

## API ルート (必要な場合のみ)
外部からのWebhookや、Server Actionsが使えない場合:

```typescript
// app/api/projects/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const project = await db.project.findUnique({
    where: { id: params.id },
  });

  if (!project) {
    return NextResponse.json(
      { error: 'プロジェクトが見つかりません' },
      { status: 404 }
    );
  }

  return NextResponse.json(project);
}
```

## Prisma クライアント
`@/lib/db` からインポート:

```typescript
import { db } from '@/lib/db';

// トランザクション例
const result = await db.$transaction(async (tx) => {
  const project = await tx.project.create({ data: projectData });
  await tx.estimateItem.createMany({
    data: items.map(item => ({ ...item, projectId: project.id })),
  });
  return project;
});
```

## エラーハンドリング
`lib/errors/` のユーティリティを活用:

```typescript
import { handleError } from '@/lib/errors/error-handler';
import { AppError, ValidationError } from '@/lib/errors/error-types';

export async function riskyAction(input: unknown) {
  try {
    // バリデーション
    if (!isValidInput(input)) {
      throw new ValidationError('入力が不正です');
    }

    // 処理
    return { success: true, data: result };
  } catch (error) {
    return handleError(error);
  }
}
```

## モック実装
開発中は `lib/mocks/` のモックデータを使用:

```typescript
import { MOCK_ESTIMATE_ITEMS } from '@/lib/mocks/mock-estimate-items';
import { MOCK_SIMILAR_CASES } from '@/lib/mocks/mock-project-params';

// 本番実装前のモック
export async function searchSimilarCases(_query: string, limit = 10) {
  // TODO: Weaviate連携実装後に置き換え
  return MOCK_SIMILAR_CASES.slice(0, limit);
}
```
