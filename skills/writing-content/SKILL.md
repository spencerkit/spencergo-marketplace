---
name: writing-content
description: Content writing skill - writes based on outline, real-time style comparison, embedded self-check, supports multiple writing rhythms.
---

# Writing Content

## Overview

Standalone content writing module:
1. Write section by section based on outline
2. Real-time style comparison
3. Embedded self-check (AI痕迹/节奏/逻辑)
4. User-confirmed writing rhythm

## Usage

/writing-content

Or describe requirements:
- "Help me write an article about xxx"
- "Write based on this outline: {outline}"

---

## 1. Writing Rhythm

User chooses writing rhythm:

| Rhythm | Description | Use Case |
|--------|------------|----------|
| Per-section | Confirm each section | Long articles, important content |
| By-phase | Confirm after several sections | Medium length |
| Whole | Write all at once, then confirm | Short, familiar topics |

---

## 2. Embedded Self-Check

### 2.1 AI Pattern Detection

| Check | Issue | Action |
|-------|-------|--------|
| Filler phrases | 此外、然而、值得注意的是 | Remove or replace |
| Triple listing | 连续"第一/第二/第三" | Break structure |
| Bombastic expressions | 是...的证明/体现/标志 | Make concrete |
| Vague attribution | 专家表示、多项研究表明 | Remove or specify |
| Excessive dashes | >2 dashes | Simplify |
| Bot tone | 希望对您有帮助 | Remove |

### 2.2 Rhythm Detection

| Check | Issue | Action |
|-------|-------|--------|
| Uniform sentence length | All 15-20 chars | Mix lengths |
| Uniform paragraph length | All ~100 chars | Vary paragraph length |
| Flat emotion curve | No起伏 | Enhance variation |

### 2.3 Logic Detection

| Check | Issue | Action |
|-------|-------|--------|
| Unexplained concepts | Terms reader wont understand | Add explanation |
| Logic jump | Sudden conclusion | Add transition |
| Audience mismatch | Too deep/shallow | Adjust difficulty |

### 2.4 Content Type Checks

| Type | Checks |
|------|--------|
| Technical | Code accuracy, step completeness |
| Story | Character consistency, plot logic |
| Xiaohongshu | Emoji density, tag compliance |
| WeChat | Title appeal, opening hook |

---

## 3. Real-time Style Comparison

During writing, continuously compare:
- Vocabulary style
- Sentence patterns
- Tone consistency
- Opening/closing style

If deviation detected, auto-adjust.

---

## 4. Writing Output

### Single Section Output

## Chapter 1: xxx

{content}

---
[Style check passed ✓]
[Characters: xxx]
```

### Full Draft Output

## Full Draft

{full text}

---
Character count: ~xxx
Reading time: ~x min

---
Please review. Feedback welcome.
```

---

## 5. Opening Library

### 5.1 Story Introduction
Start with relevant story to hook reader

### 5.2 Question
Start with thought-provoking question

### 5.3 Data Impact
Use surprising data or facts

### 5.4 Conclusion First
Give conclusion first, then explain

### 5.5 Suspense
Create curiosity with suspense

### 5.6 Scene Description
Immerse reader with scene

---

## 6. Closing Library

### 6.1 Summary
Review main points

### 6.2 Elevation
Elevate to higher level

### 6.3 Open Discussion
Leave questions for reader

### 6.4 Interactive CTA
Guide comments/share/bookmark

### 6.5 Punchline
End with powerful statement

---

## 7. Writing Process

1. Receive outline and style requirements
2. Choose writing rhythm
3. Write by section
4. Self-check each section
5. Real-time style comparison
6. User confirmation
7. Continue or submit whole
8. Final review
