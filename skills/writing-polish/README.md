# Writing Polish

> 独立的润色模块 - 改写/优化/校对/去除 AI 痕迹

## 功能

### 核心功能

- **改写 (Rewrite)** - 改变风格/语气
- **优化 (Optimize)** - 提升质量
- **校对 (Proofread)** - 语法/拼写/格式检查
- **去 AI 化 (De-AI-ify)** - 去除 AI 写作痕迹

### 优化方向

- 语言表达更自然
- 逻辑更清晰
- 情感更丰富
- 去除机械感

## 使用方法

```bash
/spencergo:writing-polish
```

或描述润色需求：
- "帮我润色这篇文章"
- "把这段改得更自然"

## 触发方式

- 直接调用：`/spencergo:writing-polish`
- 描述式："润色一下"、"优化这段文字"

## 工作流程

1. 用户提供需要润色的内容
2. 选择润色类型（改写/优化/校对/去 AI 化）
3. AI 进行润色处理
4. 输出润色结果

## 示例

```
> /spencergo:writing-polish

请提供需要润色的内容，并选择润色类型：
1. 改写 - 改变风格
2. 优化 - 提升质量
3. 校对 - 检查错误
4. 去 AI 化 - 去除 AI 痕迹
```

## 安装

This skill is part of spencergo-marketplace.

Installation:
```bash
/plugin marketplace add spencerkit/spencergo-marketplace
/plugin install spencergo@spencerkit/spencergo-marketplace
```

## License

MIT
