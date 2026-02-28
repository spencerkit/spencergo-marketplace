---
name: naming
description: AI naming skill for any scenario - generates suitable names for projects, products, variables, functions, pets, people, brands, and more.
---

# Naming Skill

## Usage

Use when user needs naming for anything. Supports:
- Project/Product naming
- Code naming (variables/functions/classes)
- File naming
- Personal names (Chinese/English)
- Pet names
- Character/Story names
- Brand/Company names
- Book titles
- Music/Art titles
- Game IDs
- WeChat/Social media names
- Domain names
- App names
- And more (25+ scenarios)

## Process (MUST FOLLOW)

### Step 1: Identify Scenario Type

First determine what type of thing needs naming, then follow corresponding question flow:

#### A. Project/Product
Questions:
1. Core function?
2. Target users?
3. Style preference? (Tech/Chinese/ warm/Premium/Creative/Nature)
4. Keywords to include?
5. Reference style?
6. Chinese/English/Both?

#### B. Code Naming
Questions:
1. Purpose (variable/function/class/constant)?
2. Programming language?
3. Naming conventions?
4. Similar existing names?

#### C. File/Folder
Questions:
1. File function?
2. File type (.ts/.py/.js)?
3. Naming style?

#### D. Personal Names
Questions:
1. Boy/Girl/Neutral?
2. Meaning/hopes?
3. Generation character?
4. Birth season?
5. Zodiac preference?
6. Astrology?
7. Style? (Traditional/Modern/Unique/Natural/Classical)
8. Tone? (Realistic/Artful/Otherworldly/Cute/Wuxia/CEO/Sweet/Manly/Mysterious/Retro)
9. Classical source? (Poetry/Idiom/History)
10. Surname?

#### E. Pet Names
Questions:
1. Pet type (cat/dog/bird/fish)?
2. Gender?
3. Traits to reflect?
4. Source preference? (Food/Anime/Reduplication/English/Nature)
5. Style? (Cute/Cool/Food/Nature/Simple)
6. How many? (default 8)

#### F. Character Names
Questions:
1. Protagonist/Supporting/Antagonist?
2. Genre? (Fantasy/Sci-Fi/Modern/Western/History/Mystery)
3. Character traits?
4. Tone? (Realistic/Creative/Anime/Epic/Romantic/Mystery/Dark/Comedy/Healing)
5. Time period?
6. Need surname?

#### G. Brand/Company
Questions:
1. Core business?
2. Target audience?
3. Brand tone? (Premium/Friendly/Tech/Natural/Retro/Modern/Chinese)
4. Founder traits?
5. Year founded?
6. Style? (Modern/Classical/English/Wordplay/Nature/Abstract)
7. Keywords?
8. Domain needed?

... (Other scenarios follow similar pattern)

### Step 2: Generate Names

After collecting info, generate name candidates.

---

## Input Recognition

Automatically identify from user input:
1. Description: "a tool to help programmers name things"
2. Keywords: "ai, name, tool"
3. Reference: "like Claude"

---

## Language

- Default: Chinese + English bilingual
- If user specifies, follow their preference

---

## Naming Principles

**General:**
- Simple, memorable, smooth pronunciation
- No negative meanings, no ambiguity
- Follow industry conventions

**Code:**
- Variables: camelCase, descriptive
- Functions: verb + camelCase
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE

**Files:**
- kebab-case or lowercase_underscore
- Avoid special characters

---

## Output Format

Generate 8 candidates:

## Candidates

| # | Name | Explanation |
|---|------|-------------|
| 1 | NameOne | Concise, reflects... |
| 2 | NameTwo | ... |

---
Which do you prefer? Tell me number or feedback.
```

### Refinement Support

After selection:
- Change style: "more classical", "anime style", "more tech"
- Change language: "English only", "Chinese only"
- Add/remove characters: "add X character", "shorter"
- Adjust tone: "cuter", "more premium", "more poetic"

---

## Workflow

1. Identify scenario → 2. Select branch → 3. Ask questions (one at a time)
4. Generate names → 5. Present in table → 6. Wait for selection
7. Refine if needed

### Question Logic

**Skip:** Mark "optional" questions, user can say "skip"
**Parallel:** If user answers multiple, process all then continue

### Examples

User: "Help me name my cat"
1. What type of pet?
User: "Cat"
2. Gender?
...

---

## Notes

- Default to bilingual if no language specified
- Follow language conventions for code
- Always let user choose, don't decide for them

---

## Special Features

### Name Scoring

| Dimension | Score | Description |
|-----------|-------|-------------|
| Meaning | ★★★★☆ | Connotation |
| Sound | ★★★★☆ | Pronunciation |
| Uniqueness | ★★★☆☆ | Rarity |
| Applicability | ★★★★★ | Use case fit |
| Memorability | ★★★★☆ | Easy to remember |

### Matching Analysis

- Core function match: XX%
- Style preference match: XX%
- Language match: XX%
- Keywords: ✓/✗

Overall: XX%

---

## Common Styles

**Chinese Classical:**
- Poetry: from Tang/Song poems
- Chu Ci: romantic, ornate
- Idiom: historical references
- Historical figures

**Modern:**
- Simple English translation
- Creative combinations
- Natural imagery
