---
name: writing-outline
description: Outline generation skill - generates structured outlines based on requirements, provides content type structure library and smart recommendations.
---

# Writing Outline

## Overview

Standalone outline generation module:
1. Generate 3-5 outline options based on requirements
2. Content type structure library with smart recommendations
3. User selects and confirms outline
4. Support outline variants and adjustments

## Usage

/spencergo:writing-outline

Or describe requirements:
- "Help me outline a WeChat article about xxx"
- "I want to write a Xiaohongshu post about xxx"

---

## 1. Content Type Structure Library

### 1.1 WeChat Articles

| Structure Type | Scenario | Template |
|----------------|----------|----------|
| Conclusion-first | Opinion/Tips | Conclusion → Reasons 1-3 → Cases → Summary |
| Story + Tips | Experience sharing | Story intro → Tips breakdown → Summary |
| List format | Tips collection | Pain point → List items → Summary |
| Comparison | Selection advice | Background → A vs B → Recommendation |
| Q&A | Q&A format | Question intro → Answers → Extension |

### 1.2 Xiaohongshu

| Structure Type | Scenario | Template |
|----------------|----------|----------|
| Tips collection | Knowledge share | Hook → 1/2/3/4 points → CTA |
| Pitfall sharing | Experience | Pitfall story → Avoid tips → CTA |
| Review/Comparison | Product selection | Intro → Products → Pros/Cons → Summary |
| Tutorial | Skill teaching | Result → Steps 1/2/3 → Notes |

### 1.3 Technical Tutorials

| Structure Type | Scenario | Template |
|----------------|----------|----------|
| Problem-driven | Problem solving | Background → Solution → Code → Summary |
| Principle exploration | Deep understanding | Phenomenon → Principle → Practice → Deep dive |
| Practical project | Hands-on | Intro → Setup → Core → Extension |
| Comparison | Tech selection | Background → Tech A → Tech B → Compare → Suggestion |

### 1.4 Stories/Novels

| Structure Type | Scenario | Template |
|----------------|----------|----------|
| Hero's journey | Growth story | Ordinary → Call → Trials → Abyss → Transformation → Return |
| Three-act | Complete story | Setup → Confrontation → Resolution |
| Traditional | Classic narrative |起 → 承 → 转 → 合 |
| Suspense | Mystery | Hook → Clues → Twist → Truth |

### 1.5 Short Video Scripts

| Structure Type | Scenario | Template |
|----------------|----------|----------|
| 3-second hook | Attention grab | Hook/Conflict/Benefit → Content → CTA |
| Suspense设置 | Curiosity driven | Suspense → Buildup → Reveal |
| Emotion climax | Emotional reach | Setup → Climax → Summary/CTA |

---

## 2. Outline Generation Process

### Step 1: Identify Content Type

Determine from user description:
- Content type (WeChat/Xiaohongshu/Technical/Story/Video)
- Topic area
- Target audience

### Step 2: Select Structure Template

Choose most suitable template from library:
- Consider content characteristics
- Consider audience preference
- Consider platform specifics

### Step 3: Generate Outline Options

Generate 3-5 options:
- Each option 3-5 sections
- Section title + brief description
- Recommend most suitable one

### Step 4: User Confirmation

- User selects or modifies
- Confirm before proceeding

---

## 3. Outline Output Format

## Outline Options

### Option A (Recommended)
1. Chapter 1: xxx
   - Subsection: xxx
2. Chapter 2: xxx
   - Subsection: xxx
3. Chapter 3: xxx

### Option B
...

---

Please select or provide feedback.
```

Confirmed:
## Confirmed Outline

1. Chapter 1: xxx
2. Chapter 2: xxx
3. Chapter 3: xxx

---
Outline confirmed. Ready for writing phase.
```

---

## 4. Outline Adjustments

User can:
- Reorder sections
- Merge/split sections
- Add/remove sections
- Modify section titles

---

## 5. Smart Recommendation Logic

Auto-recommend based on:

| Factor | Weight | Consideration |
|--------|--------|---------------|
| Content type | High | Different types match different structures |
| Topic | Medium | Tech vs Emotional |
| Audience | Medium | Professional vs General |
| Platform | Low | WeChat vs Xiaohongshu |

---

## Next Step Guide (MUST FOLLOW)

When user confirms the outline, you MUST guide them to the writing phase:

1. Tell user: "Outline confirmed. Moving to writing phase."
2. Use Skill tool to invoke /spencergo:writing-content
3. Pass context: confirmed outline structure

DO NOT skip the writing phase and go directly to review

User can say:
- "continue" / "next" / "start writing"
