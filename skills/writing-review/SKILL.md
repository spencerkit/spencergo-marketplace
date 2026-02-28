---
name: writing-review
description: Content review skill - AI predicts questions, multi-dimensional review, quantitative scoring, provides improvement suggestions.
---

# Writing Review

## Overview

Standalone content review module:
1. AI predicts reader questions
2. Multi-dimensional review (logic/reader perspective/emotion/structure/AI痕迹)
3. Quantitative scoring
4. Improvement suggestions

## Usage

/writing-review

Or provide content:
- "Help me review this article: {content}"
- "Any issues with this piece?"

---

## 1. Review Dimensions

### 1.1 Logic Completeness

| Check | Description |
|-------|-------------|
| Clear viewpoint | Is main point clear? |
| Sufficient evidence | Enough support for arguments? |
| Logical flow | Smooth transitions between paragraphs? |

### 1.2 Reader Perspective

| Check | Description |
|-------|-------------|
| Concepts explained | Unexplained technical terms? |
| Difficulty match | Match reader level? |
| Predicted questions | What questions might readers have? |

### 1.3 Emotional Resonance

| Check | Description |
|-------|-------------|
| Attraction | Opening hook? |
| Empathy | Connect with reader? |
| Memorable | Any memorable points? |

### 1.4 Structure

| Check | Description |
|-------|-------------|
| Opening | Hook to continue reading? |
| Transitions | Natural between sections? |
| Ending | Strong conclusion? |

### 1.5 AI Pattern Detection

Same as writing-content self-check

---

## 2. Review Process

### Step 1: AI Predicts Questions

Based on content, predict 3-5 questions readers might ask

### Step 2: Check Coverage

Compare content against questions
Mark answered/unanswered

### Step 3: Multi-dimensional Review

Check each dimension

### Step 4: Quantitative Scoring

Score each dimension

### Step 5: Improvement Suggestions

List issues + improvement directions

---

## 3. Quantitative Scoring

### Scoring Standard

Each dimension 1-5:

| Score | Description |
|-------|-------------|
| 5 | Excellent |
| 4 | Good |
| 3 | Acceptable |
| 2 | Needs improvement |
| 1 | Serious issues |

### Dimensions

| Dimension | Weight |
|-----------|--------|
| Logic | 25% |
| Reader perspective | 25% |
| Emotion | 20% |
| Structure | 15% |
| AI patterns | 15% |

### Scoring Output

## Review Result

### Overall Score
| Dimension | Score |
|-----------|-------|
| Logic | 4/5 |
| Reader perspective | 3/5 |
| Emotion | 4/5 |
| Structure | 5/5 |
| AI patterns | 3/5 |
| Total | 3.8/5 |

### Question Check
1. Question 1 - ✓ Answered
2. Question 2 - ✓ Answered
3. Question 3 - ✗ Not fully answered

### Issues
1. [Medium] Some transitions not smooth
2. [Low] Could add more examples

### Suggestions
- Suggest adding real example in Chapter 2
- Opening could be more engaging

---

## 4. Review Output Format

## Review Complete

### Score
Total: X.X / 5.0

### Main Issues
1. xxx
2. xxx

### Suggestions
1. xxx
2. xxx

---
Need me to make changes based on suggestions?
```

---

## 5. Review Types

| Type | Description |
|------|-------------|
| Full review | All dimensions |
| Focused review | Specific dimensions only |
| Quick review | Key issues only |

---

## Next Step Guide (MUST FOLLOW)

When user confirms the review, you MUST guide them to the polish phase:

1. Tell user: "Review complete. Moving to polish phase."
2. Use Skill tool to invoke /writing-polish
3. Pass context: review report and suggestions

User can say:
- "continue" / "next" / "polish"
