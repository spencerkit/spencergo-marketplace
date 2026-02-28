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

### 关键规则

- **不要跳过任何阶段**（除非用户明确要求快速模式）
- **每个阶段必须获得用户确认**后才能进入下一阶段
- **不要在内容编写阶段就调用审核**，必须等用户确认初稿
- **不要在审核阶段就自动润色**，必须等用户确认审核结果

---

**The terminal state is delivery.** Do NOT skip any phase. The ONLY flow is style → outline → content → review → polish → delivery.

<CRITICAL>
当用户说"继续"、"下一步"、"开始"等意图时，你必须：
1. 明确告诉用户要进入哪个阶段
2. 使用 Skill tool 调用对应的子模块 skill
3. 例如：用户说"继续写大纲" → 你必须调用 `/writing-outline`（通过 Skill tool）
</CRITICAL>


---

**详细流程请参考各子模块**：
- `/writing-style` - 风格分析详细流程
- `/writing-outline` - 大纲编写详细流程
- `/writing-content` - 内容编写详细流程
- `/writing-review` - 内容审核详细流程
- `/writing-polish` - 润色详细流程
