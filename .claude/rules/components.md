---
paths:
  - "**/*.tsx"
  - "components/**/*"
---
# React コンポーネントルール

## Server Component vs Client Component

### Server Component (デフォルト)
- データフェッチ、DB操作を行うコンポーネント
- `'use client'` ディレクティブなし

```typescript
// app/projects/[id]/page.tsx (Server Component)
import { db } from '@/lib/db';

export default async function ProjectPage({ params }: { params: { id: string } }) {
  const project = await db.project.findUnique({
    where: { id: params.id },
  });

  return <ProjectDetailClient project={project} />;
}
```

### Client Component
- useState, useEffect, イベントハンドラを使用するコンポーネント
- ファイル先頭に `'use client'` を記述

```typescript
// components/project-steps.tsx (Client Component)
'use client';

import { useState } from 'react';

export function ProjectSteps({ projectId }: { projectId: string }) {
  const [activeStep, setActiveStep] = useState(0);
  // ...
}
```

## UIコンポーネント
`components/ui/` には shadcn/ui ベースのコンポーネントを配置:

```typescript
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
```

## スタイリング
Tailwind CSS + `cn` ユーティリティを使用:

```typescript
import { cn } from '@/lib/utils';

<div className={cn(
  'flex items-center gap-2',
  isActive && 'bg-primary text-white',
  className
)}>
```

## Props型定義
コンポーネントのProps型は同一ファイル内で定義:

```typescript
interface EstimateTableProps {
  items: EstimateItem[];
  onItemUpdate?: (id: string, data: Partial<EstimateItem>) => void;
  readonly?: boolean;
}

export function EstimateTable({ items, onItemUpdate, readonly = false }: EstimateTableProps) {
  // ...
}
```

## レイアウトパターン
`app/projects/[id]/` では Server/Client 分離パターンを採用:

```
layout.tsx        # Server Component - データ取得
layout-client.tsx # Client Component - インタラクション
```

## アイコン
lucide-react または @heroicons/react を使用:

```typescript
import { Plus, Trash2, Edit } from 'lucide-react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';
```

## フォーム
Zodスキーマでバリデーション:

```typescript
'use client';

import { z } from 'zod';
import { useState } from 'react';

const formSchema = z.object({
  name: z.string().min(1, '名前は必須です'),
});

export function MyForm() {
  const [errors, setErrors] = useState<z.ZodError | null>(null);

  const handleSubmit = (data: FormData) => {
    const result = formSchema.safeParse(Object.fromEntries(data));
    if (!result.success) {
      setErrors(result.error);
      return;
    }
    // 処理続行
  };
}
```
