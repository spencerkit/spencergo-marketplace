---
name: novel-studio
description: End-to-end Chinese web novel production workflow for turning a novel idea into a structured deliverable project. Covers hot-search and trend scan, discovery discussion, requirement intake, market/topic analysis, title confirmation, story planning, outline design, character bible creation, chapter drafting, polishing, proofreading, final review, and optional Feishu Wiki sync. Use when the user wants to create, develop, optimize, or deliver a serialized novel, web fiction project, long-form Chinese fiction pipeline, or a full novel production workflow from concept to manuscript.
---

# Novel Studio

Use this skill to run a complete novel-production workflow from idea to final manuscript delivery.

This skill is designed for **Chinese web fiction / serialized novel production**, especially when the user wants a structured workflow rather than ad-hoc creative writing.

## Core operating principle

Treat novel creation as a staged production pipeline with explicit user approval gates.

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

## Hard workflow rules

- Do not begin stable planning before discovery stage is complete
- Do not begin drafting before a usable outline and usable core character package exist
- Do not begin polishing on structurally unstable draft text
- Do not begin proofreading before polishing is complete for the intended range
- Do not treat output as final delivery without final review or explicit user override
- Do not sync unstable or half-structured output to Feishu unless the user explicitly requests intermediate sync

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

Follow `references/file-structure.md` for:
- directory layout
- file naming
- chapter file placement
- character file placement
- required top-level project documents

Prefer stable filenames and predictable hierarchy over improvisational storage.

## Reference map

Use these reference files as **hard operational guidance**, not optional inspiration:

- `references/workflow.md` — full pipeline order, stage gates, approval gates, required inputs, required outputs, completion standards, advancement blocks, and rollback logic
- `references/intake.md` — user-preference capture after the initial discovery discussion
- `references/hot-search-scan.md` — hot-search / trend-scan logic, search-source priority, and pre-decision market signal scan
- `references/market-research.md` — topic analysis, market positioning, title generation, title confirmation, discovery-stage hard gates, and final topic-report requirements
- `references/topic-report-template.md` — default report template for `00_选题报告.md`
- `references/outlining.md` — idea expansion, world setup, plot structure, outline design, and planning-stage hard gates
- `references/character-bible.md` — character profiles, motivation, arc, relationship structure, and drafting gate requirements
- `references/drafting.md` — chapter drafting rules, pacing, hooks, anti-perfunctory drafting rules, and polishing gate requirements
- `references/polishing.md` — language refinement, emotional density, readability, de-AI cleanup, and proofreading gate requirements
- `references/proofreading.md` — consistency checks, logic review, OOC control, structural QA, and final-review gate requirements
- `references/final-review.md` — scoring, acceptance standard, rollback conditions, and delivery gate requirements
- `references/file-structure.md` — canonical novel project structure
- `references/feishu-sync.md` — Feishu Wiki sync rules, node creation rules, and structure mapping
- `references/state-management.md` — project-state persistence, recovery, workflow memory rules, and status-summary usage
- `references/revision-management.md` — revision-mode rules, feedback detection, scope analysis, and update order
- `references/feedback-confirmation-template.md` — default confirmation pattern when likely formal feedback is detected

## Delivery mindset

This skill is not only for “writing text.”
It is for building a **deliverable novel project** under explicit user supervision.

That means the final result should ideally include:
- clear project structure
- stable file naming
- reusable planning materials
- characters and manuscript separated cleanly
- quality review before handoff
- optional remote sync only after structure is coherent

## Project-status query rule

When the user asks about:
- current project progress
- current stage
- current batch state
- blockers
- approval status
- next-step guidance
- whether feedback has been recorded or applied

use `scripts/novel_project_status.py` as the default status-summary entry point whenever possible.

Translate the result into human-readable progress language rather than dumping raw state unless the user asks for raw detail.

## Feedback-detection rule

The user may provide revision feedback in normal conversation.
The agent should proactively detect likely formal feedback, but must not silently apply major revisions without confirmation.

If likely formal feedback is detected:
- summarize it
- classify it
- estimate impact scope
- identify conflict with prior settings if any
- ask whether to record it as formal feedback
- ask whether it should override prior settings or add a new rule

Treat `references/revision-management.md` and `references/feedback-confirmation-template.md` as the operational standard for this.

## Anti-perfunctory rule

Do not count a stage as complete merely because something exists.

Examples of non-completion:
- a discovery stage with no usable recommendation or no confirmed title / approved working title
- a planning stage with only vague summaries
- a character stage with label-only bios and no usable motivation/conflict
- a drafting stage with plot summaries pretending to be chapter prose
- a polishing stage with only superficial paraphrasing
- a proofreading stage with no real continuity / logic / OOC check
- a final review stage with no actual delivery judgment

If the current output is perfunctory, stop and repair the current stage before moving forward.

## Feishu sync rule

If the user asks to sync the novel project to Feishu Wiki, follow `references/feishu-sync.md`.

When creating Wiki nodes:
- use `docx`, not `doc`
- use `node_type: origin`
- preserve parent/child structure
- create parent nodes before child nodes
- sync in stable batches for large manuscript folders

## Working style

Be production-minded:
- structured
- concrete
- stage-aware
- quality-controlled
- explicit about blockers
- explicit about completion standards
- explicit about approval gates

Avoid:
- skipping straight from vague idea to full drafting
- mixing unrelated stages together without need
- producing text without storing a reusable project structure
- treating long-form fiction like a one-shot short answer
- silently advancing past incomplete work
- silently advancing past unapproved work

## Goal

Turn a novel idea into a stable, editable, reviewable, and optionally syncable project that can support serialized writing, revision, and downstream publishing workflows, while keeping the user in explicit control at every stage gate.
