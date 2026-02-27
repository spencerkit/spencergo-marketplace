---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---
# JavaScript/TypeScript Coding Style

> This file extends [common/coding-style.md](../common/coding-style.md) with JavaScript/TypeScript specific content.

## Immutability

Use spread operator for immutable updates:

```typescript
// WRONG: Mutation
function updateUser(user, name) {
  user.name = name  // MUTATION!
  return user
}

// CORRECT: Immutability
function updateUser(user, name) {
  return {
    ...user,
    name
  }
}
```

For arrays:
```typescript
// WRONG
items.push(newItem)

// CORRECT
const newItems = [...items, newItem]

// WRONG
items.splice(index, 1)

// CORRECT
const newItems = items.filter((_, i) => i !== index)
```

## Error Handling

Use async/await with try-catch:

```typescript
try {
  const result = await riskyOperation()
  return result
} catch (error) {
  console.error('Operation failed:', error)
  throw new Error('Detailed user-friendly message')
}
```

## Input Validation

Use Zod for schema-based validation:

```typescript
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150)
})

const validated = schema.parse(input)
```

## TypeScript Specific

### Interface vs Type

- Use `interface` for object shapes that may be extended
- Use `type` for unions, intersections, and primitives

```typescript
// Interface for extendable objects
interface User {
  id: string
  name: string
}

// Type for unions
type Status = 'pending' | 'active' | 'deleted'
```

### Strict Type Safety

- Enable `strict: true` in tsconfig
- Avoid `any`, use `unknown` when type is truly unknown
- Use type guards for runtime type checking

## Console.log

- No `console.log` statements in production code
- Use proper logging libraries (pino, winston) instead
- Use debug/log levels appropriately

## Naming Conventions

- Variables and functions: camelCase
- Classes and interfaces: PascalCase
- Constants: SCREAMING_SNAKE_CASE
- Files: kebab-case.ts

## Function Declaration

Prefer `const` with arrow functions over `function` declaration:

```typescript
// PREFERRED
const fetchUser = async (id: string) => {
  const response = await api.get(`/users/${id}`)
  return response.data
}

// ACCEPTABLE for functions that need hoisting
function handleClick() {
  // ...
}
```

## File Naming

Use kebab-case for all files:

```
src/
├── user-profile.tsx          # Utility/helper files
├── api-client.ts             # API client files
└── components/
    ├── button/
    │   ├── index.tsx         # Main component
    │   └── button.module.css # Styles
    └── modal/
        ├── index.tsx
        └── modal.module.css
```

## Component Organization

### Directory Structure

All components (parent and sub-components) use `index.tsx`:

```
src/components/
├── button/
│   ├── index.tsx
│   └── index.module.scss
└── modal/
    ├── index.tsx
    ├── index.module.scss
    ├── modal-header/
    │   ├── index.tsx
    │   └── index.module.scss
    ├── modal-body/
    │   ├── index.tsx
    │   └── index.module.scss
    └── modal-footer/
        ├── index.tsx
        └── index.module.scss
```

### Component Sizing

- Split components when they exceed 200 lines
- Extract logical parts into sub-components at the same level as the parent
- Sub-components follow the same organization rules

```typescript
// Example: Modal/index.tsx (parent, ~150 lines)
import { ModalHeader } from './modal-header'
import { ModalBody } from './modal-body'
import { ModalFooter } from './modal-footer'

export const Modal = ({ ... }) => {
  // Core modal logic
  return (
    <div className="modal">
      <ModalHeader title={title} onClose={onClose} />
      <ModalBody>{children}</ModalBody>
      <ModalFooter onConfirm={onConfirm} onCancel={onCancel} />
    </div>
  )
}
```

### Component Location

- **Public components**: `src/components/`
- **Feature-specific components**: co-located with the feature
- **Shared UI components**: `src/components/ui/` or `src/components/`

## Export Style

Prefer named exports over default exports:

```typescript
// PREFERRED: Named exports
export const Button = ({ ... }) => { ... }
export const Modal = ({ ... }) => { ... }
export type { ButtonProps } from './types'

// AVOID: Default exports
export default function Button() { ... }
```

**Exceptions**: When re-exporting third-party components or for barrel files:
```typescript
// Barrel file - acceptable
export { Button } from './button'
export { Modal } from './modal'
```

## Project Structure

Recommended directory structure for TypeScript projects:

```
src/
├── api/                  # API 请求封装
├── assets/               # 静态资源 (图片, 字体等)
├── components/           # 公共组件
│   ├── button/
│   ├── modal/
│   └── ui/               # 基础 UI 组件
├── config/               # 配置文件
├── constants/            # 常量定义
├── hooks/                # 自定义 hooks
├── layouts/              # 布局组件
├── pages/                # 页面组件
├── routes/               # 路由配置
├── services/             # 业务服务层
├── stores/               # 状态管理 (Zustand, Redux, etc.)
├── types/                # 全局类型定义
├── utils/               # 工具函数
├── app.tsx               # 根组件
└── main.tsx              # 入口文件
```

### Directory Principles

- `components/` - 可复用的 UI 组件
- `pages/` - 页面级组件，与路由对应
- `hooks/` - 可复用的业务逻辑
- `utils/` - 纯函数工具
- `services/` - 业务逻辑封装
- `types/` - 跨模块共享的类型

## Import Order

Maintain consistent import order:

```typescript
// 1. React/Third-party libraries (alphabetical)
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from 'antd'
import { z } from 'zod'

// 2. Project-wide components/hooks/utils (alphabetical)
import { useAuth } from '@/hooks'
import { formatDate } from '@/utils'
import { ApiClient } from '@/services'

// 3. Relative imports - components/utils in same feature
import { ModalHeader } from './modal-header'
import { ModalBody } from './modal-body'
import { myHelper } from './utils'

// 4. Types
import type { User, Order } from '@/types'
import type { ModalProps } from './types'

// 5. Styles
import styles from './index.module.scss'
```

## Constants Management

### Why Constants Matter

Avoid magic numbers and strings throughout the codebase:

```typescript
// WRONG: Magic values scattered
if (user.age < 18) { ... }
const timeout = 3000
const API_URL = 'https://api.example.com'

// CORRECT: Centralized constants
// src/constants/index.ts
export const AGE_LIMIT = 18
export const REQUEST_TIMEOUT = 3000
export const API_ENDPOINTS = {
  BASE_URL: 'https://api.example.com',
  USERS: '/users',
  ORDERS: '/orders',
} as const
```

### Constants Organization

```
src/
├── constants/
│   ├── index.ts              # Barrel export
│   ├── api.ts                # API 相关常量
│   ├── config.ts             # 应用配置
│   ├── regex.ts              # 正则表达式
│   └── routes.ts             # 路由常量
```

### Constants Best Practices

- Use `const` with `as const` for object constants
- Group by domain (api, config, routes, etc.)
- Export from `constants/index.ts` for clean imports
- Use UPPER_SNAKE_CASE for constant names

```typescript
// src/constants/api.ts
export const API_TIMEOUT = 5000
export const API_VERSION = 'v1'

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  NOT_FOUND: 404,
  SERVER_ERROR: 500,
} as const

// src/constants/index.ts
export * from './api'
export * from './config'
export * from './regex'
```
