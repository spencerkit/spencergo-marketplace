---
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "**/*.spec.tsx"
  - "**/*.test.js"
  - "**/*.spec.js"
---
# JavaScript/TypeScript Testing

> This file extends [common/testing.md](../common/testing.md) with JavaScript/TypeScript specific content.

## Test Framework

Use **Vitest** as the primary test framework:
- Faster than Jest
- Native ESM support
- Compatible with Jest API

## Test Organization

```
src/
├── components/
│   ├── button/
│   │   ├── index.tsx
│   │   └── index.test.tsx
│   └── input/
│       ├── index.tsx
│       └── index.test.tsx
├── utils/
│   ├── format.ts
│   └── format.test.ts
└── hooks/
    ├── use-counter.ts
    └── use-counter.test.ts
```

- Co-locate tests with source files
- Use `.test.ts` or `.spec.ts` extension
- Mirror source directory structure

## Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 80,
      functions: 80,
      branches: 80,
      statements: 80
    }
  }
})
```

## Testing Utilities

### React Testing

Use **Testing Library** for React components:

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { MyComponent } from './my-component'

test('renders button and handles click', () => {
  const onClick = vi.fn()
  render(<MyComponent onClick={onClick} />)

  fireEvent.click(screen.getByRole('button'))
  expect(onClick).toHaveBeenCalled()
})
```

### Mocking

```typescript
import { vi } from 'vitest'

// Mock modules
vi.mock('./api', () => ({
  fetchUser: vi.fn()
}))

// Mock functions
const mockFn = vi.fn()
mockFn.mockReturnValue('mocked')
mockFn.mockResolvedValue('async mocked')
```

## Coverage Requirements

| Type | Minimum |
|------|---------|
| Lines | 80% |
| Functions | 80% |
| Branches | 80% |
| Statements | 80% |

Run coverage:
```bash
vitest run --coverage
```
