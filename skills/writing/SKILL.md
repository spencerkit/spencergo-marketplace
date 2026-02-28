---
name: writing
description: 综合写作技能 V4（混合模式），支持模块独立调用或预设模板组合。子模块：writing-style/writing-outline/writing-content/writing-review/writing-polish
---

# 写作技能 V4 (Writing Skill - 混合模式)

## 模块架构

```
writing (主Skill)
├── writing-style    → 风格分析
├── writing-outline  → 大纲编写
├── writing-content  → 内容编写
├── writing-review   → 内容审核
└── writing-polish   → 润色
```

## 预设模板

| 模板 | 包含模块 | 适用场景 |
|------|----------|----------|
| 完整写作 | style → outline → content → review → polish | 从头写完整文章 |
| 快速写作 | style → content | 短内容、熟悉主题 |
| 仅润色 | polish | 已有初稿只需润色 |
| 审核+润色 | review → polish | 写完了想审核+优化 |

## 独立调用

用户也可以直接调用任意子模块：
- `/writing-style` - 风格分析
- `/writing-outline` - 大纲编写
- `/writing-content` - 内容编写
- `/writing-review` - 内容审核
- `/writing-polish` - 润色

## 流程指引（Claude 自动串联）

```
┌─────────────────────────────────────────────────────────────────┐
│                        写作流程图                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐  │
│   │  风格分析  │───▶│  大纲编写  │───▶│  内容编写  │───▶│  审核   │  │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬────┘  │
│        │                │                │                │        │
│        ▼                ▼                ▼                ▼        │
│   /writing-       /writing-       /writing-       /writing-     │
│     style          outline         content         review         │
│        │                │                │                │        │
│        │                │                │                ▼        │
│        │                │                │            ┌────────┐  │
│        │                │                │            │  润色   │  │
│        │                │                │            └───┬────┘  │
│        │                │                │                │        │
│        │                │                │                ▼        │
│        │                │                │            ┌────────┐  │
│        │                │                │            │  交付   │  │
│        │                │                │            └────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**每个阶段完成后必须调用对应的 skill：**

1. **风格分析** → 用户确认后 → **invoke /writing-outline**
2. **大纲编写** → 用户确认后 → **invoke /writing-content**
3. **内容编写** → 用户确认后 → **invoke /writing-review**
4. **内容审核** → 用户确认后 → **invoke /writing-polish**
5. **润色完成** → 交付

### Key Rules

- **DO NOT skip any phase** (unless user explicitly requests quick mode)
- **MUST get user confirmation** before moving to next phase
- **DO NOT invoke review** during content writing - wait for user to confirm draft
- **DO NOT auto-polish** after review - wait for user to confirm review results

---

**The terminal state is delivery.** Do NOT skip any phase. The ONLY flow is: style → outline → content → review → polish → delivery.

<CRITICAL>
When user says "continue", "next", "start", etc., you MUST:

1. Tell user which phase you're entering
2. Use Skill tool to invoke the corresponding sub-skill
3. Example: user says "continue with outline" → you MUST invoke `/writing-outline` via Skill tool
</CRITICAL>


---

**详细流程请参考各子模块**：
- `/writing-style` - 风格分析详细流程
- `/writing-outline` - 大纲编写详细流程
- `/writing-content` - 内容编写详细流程
- `/writing-review` - 内容审核详细流程
- `/writing-polish` - 润色详细流程
