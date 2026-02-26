# Writing Skill V3 Implementation Plan - Style Reference

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add user-defined style reference feature to the writing skill, allowing users to provide sample articles and have AI analyze and mimic their writing style.

**Architecture:** Add new "Style Reference" module to existing SKILL.md, integrate into both writing and polish workflows.

**Tech Stack:** Claude Code Skills (SKILL.md format), Markdown

---

## Task 1: Add Style Sample Analysis Module

**Files:**
- Modify: `skills/writing/SKILL.md`

**Step 1: Add new section for style reference module**

Find the "## 网络搜索增强" section in SKILL.md, add new module after it:

```markdown
---

## F. 风格样本分析模块

### F1. 功能概述

用户可以提供自己写的文章作为风格样本，AI 分析这些文章的风格特点，然后生成/润色时模仿这种风格，减少"AI 感"。

### F2. 应用场景

1. **写作时参考风格** - 用户想写新文章时，提供样本让 AI 模仿风格
2. **润色时参考风格** - 用户有初稿，提供样本让 AI 按该风格润色

### F3. 触发场景

当用户：
- 在写作时说"参考我的风格"、"按我的风格写"
- 在润色时说"参考我之前的文章"
- 直接提供文章内容说"按这个风格"
- 回答可选追问时说"有，我的风格是..."

### F4. 输入方式

| 类型 | 识别方式 | 处理方式 |
|------|----------|----------|
| **直接粘贴** | 用户复制文章内容 | 直接分析 |
| **文件路径** | 本地路径格式 | 读取文件内容 |
| **仓库地址** | GitHub URL | 获取文件内容 |

### F5. 限制

- 样本数量：1-3篇
- 每篇长度：建议 500-3000 字
- 超出范围可以只分析部分内容

### F6. 风格分析要素

**核心要素（必分析）：**
- 用词习惯 - 专业术语/口语化/接地气/文言化
- 句子长短 - 长句多/短句多/长短交替
- 段落结构 - 段落长度、层次安排

**扩展要素（如有）：**
- 语气特点 - 严肃/轻松/俏皮/温暖/犀利
- 开头方式 - 直入主题/故事引入/提问引入/结论先行
- 结尾方式 - 总结/升华/开放/互动/金句点睛
- 叙事节奏 - 快/慢/张弛有度
- 个人特色 - 特色词/口头禅/习惯表达

### F7. 风格分析 prompt 模板

请分析以下文章的风格特点：

文章内容：
{文章内容}

请分析以下要素：

**核心要素（必分析）：**
1. 用词习惯 - 这篇文章用什么类型的词？专业/口语/接地气/文言？
2. 句子长短 - 长句多还是短句多？还是交替？
3. 段落结构 - 段落长度如何？层次怎么安排？

**扩展要素（如有）：**
4. 语气特点 - 严肃/轻松/俏皮/温暖/犀利？
5. 开头方式 - 直入主题/故事引入/提问引入/结论先行？
6. 结尾方式 - 总结/升华/开放/互动/金句点睛？
7. 叙事节奏 - 快/慢/张弛有度？
8. 个人特色 - 有没有什么特色词或口头禅？

请用 JSON 格式输出：
```json
{
  "core": {
    "vocabulary": "用词特点描述",
    "sentence": "句式特点描述",
    "structure": "结构特点描述"
  },
  "extended": {
    "tone": "语气特点描述",
    "opening": "开头特点描述",
    "closing": "结尾特点描述",
    "rhythm": "节奏特点描述",
    "personal": "个人特色描述"
  },
  "summary": "一句话风格总结"
}
```

### F8. 风格分析输出格式

```
## 风格分析结果

### 核心特点
- 用词：{xxx}
- 句式：{xxx}
- 结构：{xxx}

### 扩展特点
- 语气：{xxx}
- 开头：{xxx}
- 结尾：{xxx}
- 节奏：{xxx}
- 个人特色：{xxx}

### 风格总结
{一句话总结风格特点}
```

### F9. 风格应用 prompt 模板（写作）

请按以下风格写一篇{类型}文章：

主题：{主题}
目标读者：{读者}
风格参考：{风格分析结果}

要求：
1. 用词参考：{用词特点}
2. 句式参考：{句式特点}
3. 结构参考：{结构特点}
4. 语气参考：{语气特点}
5. 开头参考：{开头特点}
6. 结尾参考：{结尾特点}
7. 保持个人特色：{个人特色}
8. 不要有明显的 AI 写作痕迹

### F10. 风格应用 prompt 模板（润色）

请按以下风格润色文章：

原文：
{原文内容}

目标风格参考：{风格分析结果}

要求：
1. 保持原文核心内容不变
2. 用词改为：{用词特点}
3. 句式改为：{句式特点}
4. 语气改为：{语气特点}
5. 开头改为：{开头特点}
6. 结尾改为：{结尾特点}
7. 保留原文的个人特色：{个人特色}
8. 不要有明显的 AI 写作痕迹
```

**Step 2: Commit**

```bash
git add skills/writing/SKILL.md
git commit -m "feat: add style sample analysis module to writing skill"
```

---

## Task 2: Integrate Style Reference into Writing Module

**Files:**
- Modify: `skills/writing/SKILL.md`

**Step 1: Add style reference option to A1. 公众号/博客文章**

Find "可选：" section in A1, add new option:

```markdown
可选：
5. 有什么特别想表达的观点？
6. 需要加入案例或故事吗？
7. 语言偏好？（中文/英文/双语）
8. 有自己的写作风格想让我参考吗？（提供1-3篇你之前写的文章）
   - 可以粘贴文章/提供文件路径/提供仓库地址
   - 我会分析风格后按该风格写作
```

**Step 2: Add style reference option to A2. 小红书/社交媒体**

Find "可选：" section in A2, add new option:

```markdown
可选：
5. 想要什么语气？（亲切/专业/俏皮）
6. 需要加emoji或话题标签吗？
7. 有自己的写作风格想让我参考吗？
```

**Step 3: Add style reference option to A3. 短视频脚本**

Find "可选：" section in A3, add new option:

```markdown
可选：
5. 需要分镜吗？
6. 旁白还是对话形式？
7. 有自己的写作风格想让我参考吗？
```

**Step 4: Add style reference option to A4. B站视频脚本**

Find "可选：" section in A4, add new option:

```markdown
可选：
6. 需要的语言风格？（严肃/活泼/专业/搞笑）
7. 有自己的写作风格想让我参考吗？
```

**Step 5: Add style reference option to B1. 故事/小说**

Find "可选：" section in B1, add new option:

```markdown
可选：
6. 需要什么结局？（圆满/开放/悲剧）
7. 有特定的情节元素想加入吗？
8. 有自己的写作风格想让我参考吗？
```

**Step 6: Add style reference option to B2. 诗歌**

Find "可选：" section in B2, add new option:

```markdown
可选：
5. 需要押韵吗？
6. 有特定意象想用吗？（如：月亮、秋天、流水）
7. 有自己的写作风格想让我参考吗？
```

**Step 7: Add style reference option to C1-C4 技术文章**

Find each 技术文章 section, add:

```markdown
可选（技术教程）：
7. 有自己的写作风格想让我参考吗？

可选（技术分析）：
5. 有自己的写作风格想让我参考吗？

可选（技术科普）：
5. 有自己的写作风格想让我参考吗？

可选（架构文档）：
5. 有自己的写作风格想让我参考吗？
```

**Step 8: Commit**

```bash
git add skills/writing/SKILL.md
git commit -m "feat: integrate style reference into writing module"
```

---

## Task 3: Integrate Style Reference into Polish Module

**Files:**
- Modify: `skills/writing/SKILL.md`

**Step 1: Modify D3. 通用润色追问**

Update to include style reference option:

```markdown
### D3. 通用润色追问

1. 这是什么类型的文章？（或自动识别）
2. 你想要什么效果？
   - 改写：改成什么风格？（如：严肃→轻松，专业→通俗）
   - 优化：哪方面？（更有说服力/更简洁/更有趣）
   - 校对：只需要检查错别字还是全面检查？
3. 想要什么方式进行润色？
   - A. 参考风格样本 - 提供你之前写的文章，我按该风格润色
   - B. 指定风格 - 直接选择目标风格（严肃/轻松/幽默等）
   - C. 直接润色 - 不需要特定风格
4. 有特别关注的重点吗？（可选）
```

If user selects option A, trigger F. 风格样本分析 module.

**Step 2: Commit**

```bash
git add skills/writing/SKILL.md
git commit -m "feat: integrate style reference into polish module"
```

---

## Task 4: Verify and Final Review

**Step 1: Check file**

```bash
wc -l skills/writing/SKILL.md
```

Expected: 900+ lines

**Step 2: Check git status**

```bash
git status
git log --oneline -5
```

**Step 3: Final commit if needed**

```bash
git add .
git commit -m "feat: complete style reference feature for writing skill v3"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Add Style Sample Analysis Module | skills/writing/SKILL.md |
| 2 | Integrate into Writing Module | skills/writing/SKILL.md |
| 3 | Integrate into Polish Module | skills/writing/SKILL.md |
| 4 | Verify | - |

---

## Next Steps

After implementation:
1. Test the style reference feature
2. Verify analysis results are accurate
3. Consider adding more advanced features like style mixing
