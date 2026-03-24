---
name: novel-studio
description: Use when the user wants to create, develop, or deliver a Chinese web novel or serialized fiction project from concept to manuscript, and they need structured workflow with explicit approval gates at each stage. Also applies when skipping stages, jumping to drafting without outline, or producing unstable output without persistent project structure.
---

# Novel Studio

Use this skill to run a complete novel-production workflow from idea to final manuscript delivery.

This skill is designed for **Chinese web fiction / serialized novel production**, especially when the user wants a structured workflow rather than ad-hoc creative writing.

## Core operating principle

Treat novel creation as a staged production pipeline with explicit user approval gates.

**Violating the letter of these rules is violating the spirit of these rules.**

Do not jump forward casually.
Do not skip key checkpoints unless the user explicitly asks to skip them.
Do not treat partially completed work as finished.
Do not advance when the current stage has not met its completion standard.
Do not auto-advance after a stage report.

Default order:

1. Discovery stage
2. Story planning stage
3. Character system stage
4. Drafting stage
5. Polishing stage
6. Proofreading stage
7. Final review and delivery stage

## Delivery mindset

This skill is not only for "writing text."
It is for building a **deliverable novel project** under explicit user supervision.

That means the final result should include: clear project structure, stable file naming, reusable planning materials, characters and manuscript separated cleanly, and quality review before handoff.

## Hard workflow rules

- Do not begin stable planning before discovery stage is complete
- Do not begin drafting before a usable outline and usable core character package exist
- Do not begin polishing on structurally unstable draft text
- Do not begin proofreading before polishing is complete for the intended range
- Do not treat output as final delivery without final review or explicit user override

## Universal user approval gate

Every stage must follow this pattern:

1. complete the internal stage work
2. prepare a structured stage report
3. present the result to the user
4. accept iterative feedback and revise within the same stage
5. wait for explicit user approval
6. only then move to the next stage

Without explicit approval, remain in the current stage.

## Explicit approval rule

Treat only clear user approval as permission to advance.
Examples of valid approval:
- 可以了
- 确认
- 继续
- 进入下一阶段
- 开始下一轮

Do not treat vague positivity as automatic approval.
If approval is ambiguous, ask again.

## File-backed completion rule

A stage is not complete if its core output exists only in chat and is not reflected in canonical project files.

Follow `references/file-structure.md` for directory layout, file naming, chapter/character file placement, and required top-level documents.

## Reference map

**Mandatory operational guidance — these are requirements, not suggestions.**

Read the relevant reference before entering each stage:

**Discovery** — `references/workflow.md` (full pipeline order, stage gates, approval gates, rollback logic) · `references/hot-search-scan.md` (trend-scan logic, search-source priority) · `references/market-research.md` (topic analysis, title generation, discovery hard gates)

**Story planning** — `references/outlining.md` (idea expansion, world setup, plot structure, planning hard gates) · `references/topic-report-template.md` (default template for 00_选题报告.md)

**Character system** — `references/character-bible.md` (profiles, motivation, arc, relationship structure, drafting gate requirements)

**Drafting** — `references/drafting.md` (chapter rules, pacing, hooks, anti-perfunctory rules, polishing gate) · `references/chapter-plan-template.md` (chapter outline template)

**Polishing** — `references/polishing.md` (language refinement, emotional density, de-AI cleanup, proofreading gate)

**Proofreading** — `references/proofreading.md` (consistency checks, logic review, OOC control, structural QA, final-review gate)

**Final review** — `references/final-review.md` (scoring, acceptance standard, rollback conditions, delivery gate)

**State & persistence** — `references/state-management.md` · `references/revision-management.md` · `references/feedback-confirmation-template.md`

**File structure** — `references/file-structure.md` (canonical project directory layout)

## Red Flags — STOP and repair current stage

- Skipping from vague idea straight to full drafting
- Mixing unrelated stages together without need
- Producing text without storing a reusable project structure
- Treating long-form fiction like a one-shot short answer
- Silently advancing past incomplete work
- Silently advancing past unapproved work
- Marking a stage complete without persistent file output
- Not waiting for explicit user approval before advancing

## Rationalization excuses — these mean STOP

| Excuse | Reality |
|--------|---------|
| “User said 可以，看起来不错” | Vague positivity ≠ explicit approval. Ask again. |
| “I can refine it later” | Polishing on unstable draft = rework. Fix the stage first. |
| “The outline is close enough” | No usable outline = no drafting. Write it. |
| “Characters are clear in my head” | No character file = no character system. Document it. |
| “This is faster” | Skipped stages = broken pipeline. Follow the order. |
| “User asked to skip” | Only explicit skip request overrides the rules. |

## Project-status query

When the user asks about progress, current stage, blockers, or approval status, use `scripts/novel_project_status.py` as the default entry point. Translate the result into human-readable language.

## Feedback detection

If likely formal revision feedback is detected in conversation, summarize it, classify it, estimate impact, identify conflicts with prior settings, and ask whether to record it as formal feedback before applying.

See `references/revision-management.md` and `references/feedback-confirmation-template.md`.

## Working style

Be production-minded: structured, concrete, stage-aware, quality-controlled, explicit about blockers and completion standards.

## Anti-perfunctory rule

Do not count a stage as complete merely because something exists.

Examples of non-completion:
- Discovery with no confirmed title or usable recommendation
- Planning with only vague summaries
- Character stage with label-only bios and no motivation/conflict
- Drafting with plot summaries pretending to be chapter prose
- Polishing with only superficial paraphrasing
- Proofreading with no continuity/logic/OOC check
- Final review with no actual delivery judgment

If the current output is perfunctory, stop and repair the current stage before moving forward.
