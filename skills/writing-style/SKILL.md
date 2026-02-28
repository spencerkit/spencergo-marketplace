---
name: writing-style
description: Style analysis skill - analyzes, extracts, and applies writing style. Provides style sample analysis, quantitative metrics, style conflict detection, and content type adaptation.
---

# Writing Style

## Overview

Standalone style analysis module:
1. Analyze style samples - Extract writing style characteristics
2. Quantitative metrics - Provide quantifiable style indicators
3. Style conflict detection - Warn when gap between original and target style is too large
4. Content type adaptation - Optimize style for different content types

## Usage

/writing-style

Or provide content directly:
- "Write in this style: {article}"
- "Analyze the style of: {content}"

## 1. Input Methods

| Type | Recognition | Processing |
|------|-------------|------------|
| Direct paste | User copies text | Analyze directly |
| File path | Local path format | Read file |
| Repository | GitHub URL | Fetch and analyze |

Limits:
- Samples: 1-3 articles
- Length: 500-3000 chars recommended

## 2. Style Analysis Elements

### Core Elements (Required)
- Vocabulary - Professional/Colloquial/Conversational/Literary/Mixed
- Sentence length - Long/Short/Mixed
- Paragraph structure - Length, hierarchy, spacing

### Extended Elements
- Tone - Serious/Casual/Playful/Warm/Sharp/Calm
- Opening - Direct/Story/Question/Conclusion-first/Suspense
- Closing - Summary/Elevation/Open/Interactive/Punchline
- Rhythm - Fast/Slow/Varied/Tight
- Personal touch - Catchphrases/Unique perspective

## 3. Quantitative Metrics

### 3.1 Basic
- Avg sentence: Short<15, Medium15-30, Long>30 chars
- Avg paragraph: Short<80, Medium80-200, Long>200
- Sentence variation: >0.6 rich, <0.3 monotone

### 3.2 Emotional
- Emotional density: >0.1 high, <0.05 calm
- Exclamation rate: >0.5/para expressive
- Question ratio: >0.15 interactive

### 3.3 Format
- Emoji density (for Xiaohongshu)
- Tag usage frequency
- Code ratio (for technical)

## 4. Content Type Adaptation

### 4.1 WeChat Articles
- Formal but accessible vocabulary
- Mixed sentence length
- Catchy opening, CTA ending

### 4.2 Xiaohongshu
- Conversational, youthful
- 1-3 emojis per paragraph
- 3-10 targeted hashtags

### 4.3 Technical Tutorials
- Professional vocabulary
- Clear code with comments
- Numbered steps

### 4.4 Stories/Novels
- Clear 1st/3rd person
- Scene/character/psychology description
- Natural dialogue

### 4.5 Short Video Scripts
- 3-second hook
- Fast rhythm
- Conversational dialogue

## 5. Style Conflict Detection

### 5.1 Types
- Sentence: Mixed→pure short >50% change
- Tone: Serious↔Casual >2 levels gap
- Structure: Essay→list format

### 5.2 Handling
Prompt user with suggestions when conflict detected.

## 6. Quick Style Identification

Questions:
1. Tone: Serious/Casual/Warm/Sharp/Humorous
2. Sentence: Long/Short/Mixed
3. Opening: Direct/Story/Question/Conclusion-first
4. Closing: Summary/Elevation/Open/Interactive
5. Perspective: 1st/2nd/3rd/Neutral

---

## Next Step Guide (MUST FOLLOW)

When user confirms the style, you MUST guide them to the outline phase:

1. Tell user: "Style confirmed. Moving to outline phase."
2. Use Skill tool to invoke /writing-outline
3. Pass context: confirmed style characteristics

DO NOT skip the outline phase and go directly to writing

User can say:
- "continue" / "next" / "start outline"
