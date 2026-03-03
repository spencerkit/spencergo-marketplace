# Writing Skill V4

> Comprehensive writing skill with hybrid mode - supports independent module invocation or preset template combinations

## Features

### Core Features

- **Hybrid Mode** - Use preset templates or invoke modules independently
- **5 Independent Sub-modules** - style, outline, content, review, polish
- **Preset Templates** - Full, Quick, Polish only, Review + Polish
- **Flow Guidance** - Clear next step instructions after each phase
- **Quantitative Metrics** - Style analysis, scoring, quality checks

### Supported Content Types

- WeChat Official Account / Blog Articles
- Xiaohongshu / Weibo Posts
- Short Video Scripts
- Bilibili Video Scripts
- Technical Tutorials / Analysis
- Stories / Short Fiction

## Architecture

```
writing (Main Skill)
├── writing-style    → Style analysis
├── writing-outline  → Outline generation
├── writing-content  → Content writing
├── writing-review   → Content review
└── writing-polish   → Polish
```

## Preset Templates

| Template | Modules | Use Case |
|----------|---------|----------|
| Full writing | style → outline → content → review → polish | Complete article from scratch |
| Quick writing | style → content | Short content, familiar topic |
| Polish only | polish | Already have draft, just polish |
| Review + polish | review → polish | Written, want review + polish |

## Independent Invocation

User can invoke any sub-module directly:
```bash
/spencergo:writing-style    # Style analysis
/spencergo:writing-outline  # Outline generation
/spencergo:writing-content  # Content writing
/spencergo:writing-review   # Content review
/spencergo:writing-polish   # Polish
```

## Usage

```bash
/spencergo:writing
```

Or describe your requirements directly:
- "Write a WeChat article about AI's impact on future work"
- "Write a sci-fi short story"
- "A Python beginner tutorial"

## Workflow

1. Type `/spencergo:writing` or describe your writing needs
2. **Select template**: Full / Quick / Polish only / Review + Polish
3. **Full workflow**: Style → Outline → Content → Review → Polish → Delivery

> 💡 Say "continue" to move to next phase after each step

## 触发方式

- 直接调用：`/spencergo:writing`
- 描述式："帮我写作"、"写篇文章"

## 完整模块调用

| 模块 | 调用命令 | 功能 |
|------|----------|------|
| writing-style | `/spencergo:writing-style` | 风格分析 |
| writing-outline | `/spencergo:writing-outline` | 大纲生成 |
| writing-content | `/spencergo:writing-content` | 内容写作 |
| writing-review | `/spencergo:writing-review` | 内容审核 |
| writing-polish | `/spencergo:writing-polish` | 润色 |

## 安装

This skill is part of spencergo-marketplace.

Installation:
```bash
/plugin marketplace add spencerkit/spencergo-marketplace
/plugin install spencergo@spencerkit/spencergo-marketplace
```

## License

MIT
