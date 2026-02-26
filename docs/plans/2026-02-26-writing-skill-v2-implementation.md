# Writing Skill V2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Improve the writing skill with complete templates, polish functionality, context support, and web search enhancement.

**Architecture:** Update existing SKILL.md with new modules. No new files needed - all content goes into the single skill file.

**Tech Stack:** Claude Code Skills (SKILL.md format), Markdown

---

## Task 1: Complete Missing Prompt Templates

**Files:**
- Modify: `skills/writing/SKILL.md`

**Step 1: Add B站视频脚本 prompt template**

Find the A4 section in SKILL.md, add the prompt template after the 追问流程.

```markdown
**生成 prompt 模板：**
请生成一个B站视频脚本：

主题：{主题}
时长：{时长}
内容类型：{类型}
目标受众：{受众}
结构：{结构}
语言风格：{风格}

要求：
1. 内容充实，符合B站用户喜好
2. 开头能抓住观众注意力
3. 节奏适中，适合中长视频
4. 适当加入互动元素（弹幕梗、评论引导）
5. 结尾引导点赞投币收藏
```

**Step 2: Add 技术教程 prompt template**

Find the C1 section, add the prompt template after the 追问流程.

```markdown
**生成 prompt 模板：**
请生成一篇技术教程：

主题：{主题}
技术栈：{技术栈}
读者水平：{水平}
需要代码：{是/否}
长度：{长度}
需要图解：{是/否}

要求：
1. 步骤清晰，循序渐进
2. 代码完整可运行
3. 解释为什么要这么做的原理
4. 常见错误和坑点提示
5. 总结和延伸学习建议
```

**Step 3: Add 技术分析 prompt template**

Find the C2 section, add the prompt template.

```markdown
**生成 prompt 模板：**
请生成一篇技术分析文章：

主题：{主题}
分析深度：{深度}
目标读者：{读者}
需要代码示例：{是/否}

要求：
1. 深入剖析技术原理
2. 对比不同方案优缺点
3. 结合实际应用场景
4. 提供代码示例说明
5. 给出结论和建议
```

**Step 4: Add 技术科普 prompt template**

Find the C3 section, add the prompt template.

```markdown
**生成 prompt 模板：**
请生成一篇技术科普文章：

主题：{主题}
目标受众：{受众}
风格：{风格}
长度：{长度}

要求：
1. 通俗易懂，避免专业术语（必要时解释）
2. 用比喻和例子解释复杂概念
3. 适当加入趣味性
4. 控制在合适的长度
5. 让非技术读者也能看懂
```

**Step 5: Add 架构文档 prompt template**

Find the C4 section, add the prompt template.

```markdown
**生成 prompt 模板：**
请生成一份架构文档：

系统名称：{系统名}
目标读者：{读者}
详细程度：{程度}
包含部分：{部分}

要求：
1. 清晰描述系统整体架构
2. 模块划分合理，职责明确
3. 技术选型有充分理由
4. 包含必要的流程图说明
5. 部署和运维方案（如需要）
```

**Step 6: Commit**

```bash
git add skills/writing/SKILL.md
git commit -m "feat: complete missing prompt templates in writing skill"
```

---

## Task 2: Add 润色功能模块 (Polish Module)

**Files:**
- Modify: `skills/writing/SKILL.md`

**Step 1: Add 润色模块 to SKILL.md**

Add a new section after "## 技能分支":

```markdown
---

## D. 润色功能模块

### D1. 触发识别

当用户表达以下意图时，进入润色模式：
- 改写、重写、润色、优化、校对
- "帮我改一下"、"这篇不太好"
- 粘贴文章 + "怎么样"

### D2. 润色类型

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| **改写** | 不同风格/语气重写 | 风格不满意、需要不同调性 |
| **优化** | 改进内容质量 | 内容还行，想更好 |
| **校对** | 语法/错别字/格式 | 需要检查修正 |

### D3. 通用润色追问

1. 这是什么类型的文章？（或自动识别）
2. 你想要什么效果？
   - 改写：改成什么风格？（如：严肃→轻松，专业→通俗）
   - 优化：哪方面？（更有说服力/更简洁/更有趣）
   - 校对：只需要检查错别字还是全面检查？
3. 有特别关注的重点吗？（可选）

### D4. 各类型润色要点

**公众号/博客文章：**
- 标题吸引力
- 开头抓人程度
- 内容深度
- 结尾引导

**小红书：**
- emoji使用
- 话题标签
- 情感共鸣
- 互动引导

**技术文章：**
- 代码准确性
- 解释清晰度
- 步骤完整性

**故事/小说：**
- 人物刻画
- 情节张力
- 语言风格

### D5. 改写 prompt 模板

请改写以下文章：

原文：
{原文内容}

目标类型：{类型}
改写方向：{方向}
风格：{风格}
语气：{语气}

要求：
1. 保持原文核心内容不变
2. 按照指定风格/语气重写
3. 优化表达使其更符合目标类型
4. 改写后内容流畅自然

### D6. 优化 prompt 模板

请优化以下文章：

原文：
{原文内容}

文章类型：{类型}
优化方向：{方向}
重点关注：{重点}

要求：
1. 指出可以改进的地方
2. 进行针对性优化
3. 优化后内容更有吸引力
4. 保持原文的核心观点

### D7. 校对 prompt 模板

请校对以下文章：

原文：
{原文内容}

校对类型：{类型}

要求：
1. 检查错别字和标点错误
2. 检查语法错误
3. 检查格式问题
4. 列出所有修改点及原因
5. 给出校对后的完整版本

### D8. 润色输出格式

```
## 润色结果

### 修改说明

{列出主要修改点和原因}

---

### 润色后正文

{润色后的完整文章}

---

### 额外建议

{可选：其他可以改进的方向}

---

// 继续优化选项：
// - "再改一次"
// - "回到原文"
// - "调整某部分"
```

**Step 2: Commit**

```bash
git add skills/writing/SKILL.md
git commit -m "feat: add polish module to writing skill"
```

---

## Task 3: Add 上下文处理模块 (Context Module)

**Files:**
- Modify: `skills/writing/SKILL.md`

**Step 1: Add context module to SKILL.md**

Add a new section at the beginning, after "## 技能分支":

```markdown
---

## 上下文处理

### 上下文类型识别

| 类型 | 识别方式 | 处理方式 |
|------|----------|----------|
| **纯文本** | 用户直接粘贴 | 直接使用 |
| **仓库地址** | URL包含github.com/gitlab.com | git clone → 分析代码结构 |
| **文件路径** | 本地路径格式 | 读取文件内容 |
| **无上下文** | 用户未提供 | 使用默认处理 |

### 仓库分析流程

当用户提供仓库地址时：
1. 解析仓库URL
2. Clone到临时目录
3. 分析项目结构
4. 提取关键技术信息：
   - 编程语言
   - 框架/库
   - 目录结构
   - 核心模块
5. 整理成上下文摘要
6. 融入写作 prompt

### 文件读取处理

当用户提供文件路径时：
1. 验证文件存在
2. 读取文件内容
3. 识别文件类型
4. 提取关键信息
5. 融入写作 prompt

### 技术文章上下文模板

请基于以下上下文信息写一篇技术文章：

仓库/文件上下文：
{上下文内容}

主题：{主题}
类型：{类型}
读者水平：{水平}

要求：
1. 基于提供的上下文进行分析
2. 结合实际代码示例
3. 内容准确、专业
4. 解释清晰易懂
```

**Step 2: Commit**

```bash
git add skills/writing/SKILL.md
git commit -m "feat: add context processing module to writing skill"
```

---

## Task 4: Add 网络搜索增强 (Web Search Enhancement)

**Files:**
- Modify: `skills/writing/SKILL.md`

**Step 1: Add web search module to SKILL.md**

Add a new section:

```markdown
---

## 网络搜索增强

### 触发场景

当以下情况发生时，自动触发网络搜索：
- 用户没有明确风格偏好
- 写作类型需要参考最新趋势
- 用户说"参考别人的风格"或"看看别人怎么写的"

### 搜索策略

| 写作类型 | 搜索关键词 |
|----------|------------|
| 公众号文章 | "2026 公众号 热门文章 写作风格" |
| 小红书 | "小红书 爆款笔记 特点 2026" |
| 短视频脚本 | "短视频 热门脚本 套路" |
| 技术教程 | "技术博客 最佳实践 文章风格" |
| 技术分析 | "技术深度分析 写作方法" |
| 故事 | "小说 写作技巧 热门题材 2026" |
| 诗歌 | "现代诗 写作风格 特点" |

### 处理流程

1. 根据写作类型确定搜索关键词
2. 执行搜索（最多3-5条结果）
3. 提取风格特点
4. 总结成风格建议
5. 融入生成 prompt

### 风格提取示例

搜索结果分析：
- 热门公众号文章风格：简短有力、结论先行、案例丰富
- 小红书风格：emoji多、情感强、标签精准
- 技术博客风格：代码驱动、步骤清晰、原理深入

### 搜索增强 prompt 模板

请参考以下风格来写作：

搜索分析结果：
{搜索结果分析}

主题：{主题}
类型：{类型}
目标读者：{读者}

要求：
1. 吸收搜索到的优秀风格特点
2. 结合当前主题进行创作
3. 内容既有参考性又有个人特色
```

**Step 2: Commit**

```bash
git add skills/writing/SKILL.md
git commit -m "feat: add web search enhancement to writing skill"
```

---

## Task 5: Verify and Final Review

**Step 1: Check file**

```bash
wc -l skills/writing/SKILL.md
```

Expected: 800+ lines

**Step 2: Check git status**

```bash
git status
git log --oneline -5
```

**Step 3: Final commit if needed**

```bash
git add .
git commit -m "feat: complete writing skill v2 improvements"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Complete missing prompt templates | skills/writing/SKILL.md |
| 2 | Add 润色功能模块 | skills/writing/SKILL.md |
| 3 | Add 上下文处理模块 | skills/writing/SKILL.md |
| 4 | Add 网络搜索增强 | skills/writing/SKILL.md |
| 5 | Verify | - |

---

## Next Steps

After implementation:
1. Test the skill by running `/写作`
2. Verify all new features work correctly
3. Consider future enhancements like AI 配图建议, SEO 评分
