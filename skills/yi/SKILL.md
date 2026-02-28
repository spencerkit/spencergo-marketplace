---
name: yi
description: Yi Jing divination skill - uses coin toss simulation to generate hexagrams, provides interpretation and AI analysis.
---

# Yi Jing Divination

## Trigger

Use when user needs divination:
- "Help me divine"
- "Cast a hexagram"
- "Do a reading"
- "Yi Jing divination"

## Divination Process

### Step 1: Get Question

Method 1: User input directly
Ask: "What would you like to ask about?"

Method 2: Provide templates
If user unsure, offer common questions:
1. Career (work, promotion, entrepreneurship)
2. Wealth (investment, finances, income)
3. Relationships (love, marriage)
4. Academics (exams, education)
5. Health
6. Travel
7. Other

### Step 2: Cast Hexagram

Call `performDivination(question)` from `src/divination.js`:
1. Toss coins 6 times (simulate 3 coins)
2. Record each result (old yang, young yang, old yin, young yin)
3. Determine moving yao (if any)
4. Calculate main hexagram and changing hexagram

### Step 3: Output Hexagram

Call `formatOutput(divinationResult)`:
- Question
- 6 toss results
- Hexagram symbols (Unicode)
- Gua ci (judgments) and yao ci (line judgments)
- Moving yao explanation (if any)

### Step 4: AI Interpretation

Call `generateAIPrompt(question, divinationResult)`, then use LLM for interpretation.

Requirements:
1. Classical Chinese style but modern understandable
2. Answer:
   - Overall meaning of hexagram
   - Fortune for user's question
   - Suggestions
   - (If changing hexagram) What it means

## Data Files

### data/8-gua.json
8 trigrams:
- 乾, 兑, 离, 震, 巽, 坎, 艮, 坤
- Symbol, nature, yin/yang, number

### data/64-gua.json
64 hexagrams:
- Name, full name, gua ci, xiang, yao ci, liu qin, shi/ying

## Core Functions

| Function | Description |
|----------|-------------|
| yaoGua() | Simulate coin toss, return old/young yin/yang |
| yaoLiuCi() | Toss 6 times for complete hexagram |
| calcGua(yaos) | Calculate trigram numbers from yao |
| getGuaName(yaos) | Get hexagram name and symbol |
| getZhuAndBianGua(yaos) | Get main and changing hexagram |
| getGuaData(guaInfo) | Get detailed hexagram data |
| performDivination(question) | Execute full divination |
| formatOutput(divinationResult) | Format output |
| generateAIPrompt(question, result) | Generate AI prompt |

## Output Example

═══════════════════════════════════════
           YI JING DIVINATION
═══════════════════════════════════════

【Question】
"My career development?"

【Tossing Process】
1st: ●●● → Yin (old yin) ✦ moving
2nd: ○○● → Yin (young yin)
3rd: ○○○ → Yang (old yang) ✦ moving
4th: ○●○ → Yang (young yang)
5th: ●○○ → Yin (young yin)
6th: ○●○ → Yang (young yang)

【Hexagram】
Main: Xun (Wind) ☴
Change: Gen (Mountain) ☶
Moving yao: First, Top (becomes Gen)

【Interpretation】
【Gua Ci】"Xiao Heng Li You Wang, Li Jian Da Ren"
【Xiang】"Following wind, jun zi yi shen ming shi shi"

═══════════════════════════════════════

## AI Interpretation Example

Based on hexagram, AI should include:

### Hexagram Overview
Xun (Wind) hexagram, above and below Xun, wind blows everywhere... Gua ci means "Gradual success, beneficial to see great person."

### Analysis
- Currently in "advance/retreat" phase - indicates hesitation in career choices
- Xun represents wind, characteristic is "enter" - need to seize timing
- Moving yao indicates transformation period

### Fortune
Overall: Good with challenges
- Initial difficulties
- Good outcome with proper approach
- Key: "Li Jian Da Ren" - seek experienced guidance

### Suggestions
1. Go with the flow - leverage external forces
2. Balance flexibility with firm resolve
3. Seize opportunities - wind goes everywhere
4. Seek mentorship

### Changed Hexagram (Gen)
Gen means mountain - stability after changes. Stop and reflect before advancing.

---
Note: Yi Jing divination is for entertainment only. Major decisions require rational analysis.

## Notes

1. Entertainment only - not sole basis for major decisions
2. Sincerity reminder - if same question asked repeatedly, note "lack of sincerity"
3. Respect - maintain humble attitude
4. Rational view - "do your best, leave rest to fate"

## Hexagram Symbols

| Name | Symbol | Represents |
|------|--------|------------|
| 乾 | ☰ | Heaven |
| 兑 | ☱ | Lake |
| 离 | ☲ | Fire |
| 震 | ☳ | Thunder |
| 巽 | ☴ | Wind |
| 坎 | ☵ | Water |
| 艮 | ☶ | Mountain |
| 坤 | ☷ | Earth |

## Yao Explanations

- Old Yang (○): Yang changes to Yin
- Young Yang (○): Yang, unchanged
- Old Yin (●): Yin changes to Yang
- Young Yin (●): Yin, unchanged

Moving yao represents direction of change - key to interpretation.
