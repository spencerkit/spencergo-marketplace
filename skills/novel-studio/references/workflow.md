# Workflow

## 1. Workflow overview

Use this workflow to turn a novel idea into a structured, reviewable, and deliverable fiction project.

Exploration / brainstorming mode is **not** the default workflow.
Only use explicit exploration behavior when the user clearly asks for it with requests such as:
- 进入脑爆模式
- 进入探索模式
- 先脑暴
- 先发散
- 先不要定稿
- 先试几个版本
- 只做创意探索

When the user has not explicitly requested exploration mode:
- remain in the formal staged workflow
- prefer structured progress over open-ended ideation
- do not silently switch into freeform brainstorming

Default stage order:

1. Discovery stage
2. Story planning stage
3. Character system stage
4. Drafting stage
5. Polishing stage
6. Proofreading stage
7. Final review and delivery stage

Do not casually skip stages.
If the user explicitly asks to skip a stage, continue only after stating the risk and recording the assumption.

---

## 2. Global hard rules

### 2.1 Stage discipline
- Do not start stable planning before discovery stage is complete
- Do not start drafting before planning and character system stages are complete
- Do not polish text that is still structurally unstable
- Do not proofread text that is still under major rewrite
- Do not treat unreviewed output as final delivery

### 2.2 Universal user approval discipline
Every stage must end with:
1. structured stage report
2. iterative user feedback handling
3. explicit user approval before advancement

Without explicit user approval, remain in the current stage.

### 2.3 File discipline
All major stage outputs must be reflected in canonical project files, not only in chat.

### 2.4 Advancement discipline
Do not advance to the next stage unless:
- required inputs are present
- required outputs are produced
- completion standard is met
- no listed blocker remains unresolved
- the user explicitly approves advancement

---

## 3. Stage 1: Discovery stage

### Goal
Use hot-search/trend scan first, then discuss direction with the user, then capture the user’s preferences, then produce a formal topic decision and title decision.

### Internal sub-steps
1. hot-search / trend scan
2. initial recommendation summary
3. user discussion and preference capture
4. topic comparison
5. top recommendation
6. title candidate generation
7. structured stage report
8. iterative revision with user
9. explicit approval gate

### Required input
At least enough information to identify a rough creative area, or explicit permission to begin with broad market scanning before narrowing.

### Forbidden to start if
- the request is too vague even for broad market scanning
- user constraints directly conflict and remain unresolved at the most basic level

### Required output
This stage must produce:
- hot-search / trend-scan summary
- user preference summary
- topic comparison
- top recommendation
- title candidates
- confirmed final title or explicitly approved working title
- usable `00_选题报告.md`

### Completion standard
This stage is complete only if:
- current market signal scan exists
- user preference capture exists
- topic comparison is explicit
- one top recommendation exists
- title candidates exist
- the user explicitly confirms a final title or explicitly approves a working title
- the user explicitly approves advancing to the next stage

### Do not advance if
- hot-search / trend-scan is missing
- recommendation is generic
- title is still undecided
- user preferences are still unresolved enough to distort planning
- the user still has unresolved objections
- user approval to advance is missing

### Rollback condition
Return to discovery if later planning reveals that the chosen topic or title is no longer viable.

---

## 4. Stage 2: Story planning stage

### Goal
Turn the decided topic/title into a strong story concept and usable structural outline.

### Internal sub-steps
1. idea expansion
2. story promise definition
3. structure selection
4. outline creation
5. early chapter direction
6. structured stage report
7. iterative revision with user
8. explicit approval gate

### Required input
- confirmed final title or explicitly approved working title
- usable discovery-stage output

### Forbidden to start if
- discovery stage is incomplete
- title confirmation is incomplete

### Required output
This stage must produce:
- `01_想法.md`
- `02_大纲.md`
- optionally `04_章节骨架.md`
- a planning-stage report for user review

### Completion standard
This stage is complete only if:
- hook, protagonist setup, conflict, and story promise are explicit
- outline contains at least three major turning points
- early chapter direction exists
- escalation path is visible
- the user explicitly approves the planning result

### Do not advance if
- the outline is still summary-only
- major conflict progression is missing
- early chapter direction is absent
- the user has unresolved objections
- user approval to advance is missing

### Rollback condition
Return to planning if character or drafting stages reveal structural weakness.

---

## 5. Stage 3: Character system stage

### Goal
Build a drafting-ready character package.

### Internal sub-steps
1. protagonist definition
2. core cast definition
3. relationship structure
4. motivation/conflict/arc notes
5. file output
6. structured stage report
7. iterative revision with user
8. explicit approval gate

### Required input
- usable outline
- usable story planning output

### Forbidden to start if
- planning stage is incomplete
- protagonist role is still undefined

### Required output
This stage must produce:
- `03_人物小传.md`
- `characters/*.md` for core roles or equivalent usable character package
- a character-stage report for user review

### Completion standard
This stage is complete only if:
- protagonist definition is usable
- major supporting cast is usable
- relationship logic is understandable
- core motivations and conflicts are stated
- the user explicitly approves the character package

### Do not advance if
- protagonist identity is unstable
- supporting cast has no clear function
- relationship logic is too vague for drafting
- the user has unresolved objections
- user approval to advance is missing

### Rollback condition
Return to character system if drafting reveals role collapse or OOC caused by weak foundations.

---

## 6. Stage 4: Drafting stage

### Goal
Produce real draft chapters under explicit user supervision.

### Internal sub-steps
1. define or confirm style baseline if needed
2. draft target chapter batch
3. self-check draft batch
4. structured stage report / batch report
5. iterative revision with user
6. explicit approval gate for next batch or next stage

### Required input
- usable outline
- usable character package
- drafting scope or target chapter range

### Forbidden to start if
- planning stage is incomplete
- character stage is incomplete
- chapter intent is structurally ambiguous

### Required output
This stage must produce:
- manuscript files for the target chapter range
- prose chapters, not only summaries
- stage report or batch report for user review

### Completion standard
This stage is complete only if:
- manuscript files exist for the intended chapter range
- chapters materially move story, tension, or character
- the text is prose, not outline fragments
- the user explicitly approves either the batch continuation or stage completion

### Do not advance if
- manuscript files are missing
- intended chapter range is incomplete
- output is perfunctory or summary-like
- the user has unresolved objections
- user approval to advance is missing

### Rollback condition
Return to planning or character system if drafting repeatedly breaks due to upstream weakness.

---

## 7. Stage 5: Polishing stage

### Goal
Refine the draft range into a more readable, more human, more emotionally effective version.

### Internal sub-steps
1. polish target range
2. reduce AI texture
3. improve rhythm, clarity, emotional texture, and dialogue quality
4. structured stage report
5. iterative revision with user
6. explicit approval gate

### Required input
- stable draft manuscript for the target range
- style baseline or tone target

### Forbidden to start if
- manuscript is still under major structural rewrite
- target range is incomplete

### Required output
This stage must produce:
- polished target range
- a polishing-stage report for user review

### Completion standard
This stage is complete only if:
- the intended target range is fully polished
- obvious machine texture is materially reduced
- readability is materially improved
- the user explicitly approves the polished result

### Do not advance if
- polishing covers only part of the intended range
- obvious AI texture still dominates
- the user has unresolved objections
- user approval to advance is missing

### Rollback condition
Return to drafting if the text is too structurally weak to rescue via polishing.

---

## 8. Stage 6: Proofreading stage

### Goal
Run consistency, logic, continuity, and OOC checks before final review.

### Internal sub-steps
1. continuity check
2. logic check
3. character consistency / OOC check
4. issue summary and fix direction
5. structured stage report
6. iterative revision with user
7. explicit approval gate

### Required input
- polished manuscript
- usable outline
- usable character package

### Forbidden to start if
- no polished manuscript exists for the target range
- major rewrite is still ongoing

### Required output
This stage must produce:
- proofreading result
- issue list or explicit no-blocker statement
- a proofreading-stage report for user review

### Completion standard
This stage is complete only if:
- continuity has been checked
- logic has been checked
- character consistency / OOC has been checked
- blocking issues are either resolved or explicitly recorded
- the user explicitly approves advancement

### Do not advance if
- checks were not actually performed
- blocking contradictions remain unresolved
- severe OOC remains unresolved
- the user has unresolved objections
- user approval to advance is missing

### Rollback condition
Return to the earliest upstream stage that can really fix the issue.

---

## 9. Stage 7: Final review and delivery stage

### Goal
Decide whether the project is ready for delivery, then deliver or sync if approved.

### Internal sub-steps
1. final review judgment
2. strengths / weaknesses / blocker assessment
3. delivery readiness decision
4. structured stage report
5. iterative revision with user if needed
6. explicit approval gate
7. local delivery and optional Feishu sync

### Required input
- proofread manuscript
- final project files
- review notes or explicit no-blocker judgment

### Forbidden to start if
- proofreading is incomplete
- major blocking issues remain unresolved

### Required output
This stage must produce:
- explicit final review decision
- delivery summary
- optional Feishu sync result if requested

### Completion standard
This stage is complete only if:
- final review decision is explicit
- blocking issues are either resolved or explicitly accepted by user override
- the user explicitly approves final delivery
- requested sync is completed if requested

### Do not advance if
- final review avoids judgment
- blocking issues remain unresolved without user override
- the user has not explicitly approved final delivery
- requested sync is incomplete

### Rollback condition
Return to the earliest failing upstream stage indicated by final review.

---

## 10. Workflow mindset

This workflow is designed for **project delivery under explicit user supervision**, not casual one-shot text generation.

Always optimize for:
- clarity
- structure
- continuity
- reusability
- long-form stability
- editable output
- explicit completion gates
- explicit user approval gates
- concise reporting by default

Default communication style during the workflow:
- lead with the conclusion
- keep stage reports compact unless the user asks for detail
- avoid padded explanation, repeated framing, and lecture-style expansion
- expand only when the user explicitly asks for more detail
