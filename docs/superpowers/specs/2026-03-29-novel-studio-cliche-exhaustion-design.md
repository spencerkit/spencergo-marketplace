# Novel Studio Cliche Exhaustion Design

## Goal

Add a structured anti-cliche ideation layer to `novel-studio` so the workflow can deliberately exhaust high-probability LLM answers before selecting topic, planning, opening, and revision directions.

After this change:
- explicit brainstorming mode can run a file-backed `Cliche Exhaustion Loop` inside `staging/`
- `Discovery` can use a lightweight anti-cliche loop to reduce market-average topic selection
- `Story Planning` gains a hard pre-approval loop that forces cliché enumeration, rejection, mutation, and pressure-testing before formal planning approval
- `Opening` checks whether planning-stage novelty is actually delivered through the first 3 / 10 / 20 chapters instead of redoing broad ideation
- `Proofreading` can detect narrative backslide into template patterns and surface explicit cliche-risk findings
- the parent supervisor remains the only controller of branch selection, backfill, cleanup, and persistence decisions

## Problem Statement

`novel-studio` already has strong structure around approval gates, canonical file persistence, `staging/` branch control, and anti-template references.
That solves workflow sloppiness, but it does not yet directly solve a different failure mode:

- LLMs naturally produce high-probability story answers first
- the first plausible answers are often the most overused answers
- if those answers are accepted too early, later planning and drafting tend to become polished versions of familiar structures rather than genuinely fresher story engines

In practice this creates four recurring problems:

1. topic drift toward market-average choices
   Discovery can still converge too quickly on directions that are commercially legible but structurally generic.

2. structurally valid but creatively stale planning
   A planning package may satisfy outline mechanics while still relying on default protagonist desire, default escalation, default reversal shape, and default chapter promise.

3. opening-stage backslide
   Even if planning identifies a fresher engine, the first-batch opening can silently collapse back into familiar hook shapes or generic chapter-end pull.

4. no durable trace of anti-cliche reasoning
   When an operator deliberately explores beyond the first obvious answers, there is currently no standardized file structure or state summary that records:
   - the obvious cliché candidates
   - why they were rejected
   - which mutation axes were retained
   - why the final branch was selected

The design must solve these issues without weakening the existing supervisor-first workflow, without allowing freeform ideation to pollute canonical project files, and without turning the parent into an always-on scoring engine.

## Non-Goals

This design does not attempt to:
- make brainstorming the default workflow mode
- require heavy anti-cliche loops for every tiny operator request
- replace user taste judgment with automated novelty scoring
- let subagents write `.novel-state.json` or `staging/` branch-control state
- merge exploratory branch artifacts directly into canonical files without explicit selection
- add full automatic cliché scoring in the first implementation slice
- auto-generate final story quality judgments from a single numeric metric

## User-Facing Outcome

After this change, an operator using explicit exploration mode should be able to say things like:
- `先脑暴这个题材方向`
- `先发散，不要定稿`
- `进入探索模式，挖到第 15 个以后再收束`

And the parent should then:
- create a structured exploration branch under `staging/`
- force a cliché-enumeration loop before formal selection
- preserve rejection reasons and mutation logic in branch files
- only backfill canonical files after a branch is explicitly selected
- immediately clean stale sibling branches after selection

For formal planning, the parent should also be able to enforce:
- no planning approval until cliché samples were enumerated
- no planning approval until deviation reasons were written down
- no planning approval until the retained direction explains how the first 10 chapters sustain themselves without relying only on the most familiar hook pattern

## Recommended Approach

Implement a new supervisor-side ideation protocol named `Cliche Exhaustion Loop`.

This is not a standalone workflow stage.
It is a parent-controlled protocol that can be injected into existing stages under explicit conditions.

### Core Principles

1. early answers are suspicious by default
   The first obvious LLM answers are treated as cliché samples, not as trusted finalists.

2. enumerate before rejecting
   The system should first surface the default answers explicitly, then explain why they are risky.

3. novelty must land at the structural level
   Acceptable deviation should be grounded in one or more of:
   - protagonist desire
   - cost structure
   - conflict engine
   - epistemic reversal
   - relationship consequence
   - first-10-chapter payoff logic

4. exploration stays quarantined
   Cliche-exhaustion artifacts belong in `staging/` until a branch is explicitly selected and backfilled.

5. supervisor owns selection and cleanup
   The parent chooses the retained branch, writes the canonical backfill, and deletes stale branch artifacts.

## Activation Model

### 1. Explicit exploration mode remains required

The anti-cliche loop should not silently activate during ordinary production.

It may run when:
- the user explicitly requests brainstorming / exploration mode
- the parent is still inside the planning clarification loop and no formal planning approval has been requested yet

### 2. Stage-specific intensity

Use two modes instead of one:

- `quick` mode
  For lighter topic-selection or early direction work.

- `deep` mode
  For formal `Story Planning` before planning approval.

### 3. Recommended stage usage

- `Discovery` uses `quick`
- `Story Planning` uses `deep`
- `Opening` does not rerun broad ideation; it validates delivery against retained novelty axes
- `Proofreading` does not ideate; it records backslide risks

## Protocol Design

### 1. Quick mode

Quick mode is a 3-round loop.

Purpose:
- reduce convergence on the most obvious topic or direction
- give the operator a manageable anti-cliche pass without heavy branch expansion

Rounds:

1. intuitive candidates
   - generate 5-7 high-probability options
   - explicitly label each one by cliché category

2. rejection / denial
   - explain why each intuitive option is too standard, too generic, or too dependent on default platform patterns
   - mutate away from the most obvious pattern

3. retained options
   - keep 3-5 directions only
   - for each, explain:
     - what cliché it departs from
     - what sustains the first 10 chapters
     - where it is most likely to slide back into generic form

### 2. Deep mode

Deep mode is the planning-grade anti-cliche loop.

Purpose:
- force structural divergence before formal story-planning approval

Steps:

1. cliché enumeration
   - list the 10 most obvious directions first

2. cliché diagnosis
   - explain why each one is predictable
   - distinguish “old on the surface” from “structurally weak”

3. reverse mutation
   - mutate through one or more axes:
     - desire inversion
     - cost escalation
     - conflict-engine replacement
     - epistemic reversal
     - relationship consequence
     - payoff-logic inversion

4. recombination and elimination
   - rebuild 5 candidate directions
   - reject any candidate that cannot explain:
     - first-3-chapter hook
     - first-10-chapter continuation logic
     - 20-chapter sustainability
     - what makes it non-swappable with a generic book

5. retained finalists pressure test
   - narrow to 2-3 finalists
   - each finalist must include:
     - one-sentence story promise
     - conflict engine
     - cost structure
     - first-10-chapter payoff route
     - most likely cliché backslide path

## Stage Integration

### 1. Discovery

Role:
- reduce market-average topic convergence

Allowed:
- quick loop only
- topic-level and direction-level divergence

Not allowed:
- full outline generation
- late-stage detailed chapter ideation

Canonical impact:
- retained conclusions may flow into `00_选题报告.md`
- the anti-cliche loop informs direction choice, but does not replace formal planning

### 2. Story Planning

Role:
- main control point for structural anti-cliche work

Hard gate:
- planning approval should not occur until the retained direction has:
  - cliché samples enumerated
  - rejection reasons recorded
  - first-10-chapter continuation logic explained

Canonical impact:
- selected conclusions may backfill:
  - `01_想法.md`
  - `02_大纲.md`
  - optionally `04_章节骨架.md`

### 3. Opening

Role:
- validate delivery of retained novelty, not generate new wide-branch ideas

Checks:
- did the opening revert to familiar hook patterns
- is protagonist attraction relying only on default爽点
- is chapter pull sustained by repeated same-shape hooks
- does the opening still match the planning promise

Canonical impact:
- findings shape `04A_开篇设计.md`
- failure should route back to planning or opening refinement, not silently pass forward

### 4. Proofreading

Role:
- detect backslide into template mode

Checks:
- repeated chapter-end hook shape
- repeated payoff /爽点 shape
- side plots with no consequence
- character-swap genericity
- retained novelty axes disappearing in execution

Canonical impact:
- findings should be recordable under `narrativeIntelligence.styleRisk.*`
- serious findings may later feed revision planning or final-review blockers

## `staging/` Structure

Inside `staging/<stage>/<branch-id>/`, scaffold these files for `cliche_exhaustion` branches:

- `00_脑暴任务卡.md`
- `01_直觉俗套清单.md`
- `02_反驳与否认.md`
- `03_变异候选.md`
- `04_保留候选.md`
- `05_定稿结论.md`

Responsibilities:

- `00_脑暴任务卡.md`
  records the exact ideation question and target focus

- `01_直觉俗套清单.md`
  stores first-pass cliché candidates

- `02_反驳与否认.md`
  explains why those candidates should not be accepted directly

- `03_变异候选.md`
  stores mutated alternatives grouped by novelty axis

- `04_保留候选.md`
  stores shortlisted candidates only

- `05_定稿结论.md`
  stores the retained branch and explicit backfill reason

Hard rule:
- canonical files must not be backfilled directly from `01`-`04`
- only `05_定稿结论.md` may authorize formal backfill

## State Model Changes

### 1. `review.*`

Add these fields:

```json
"review": {
  "brainstormMode": null,
  "brainstormFocus": null,
  "brainstormRound": null,
  "selectedBranch": null
}
```

Field meanings:
- `brainstormMode`: e.g. `cliche_exhaustion`, `normal_exploration`
- `brainstormFocus`: e.g. `topic`, `story_engine`, `opening`, `twist`, `character_drive`
- `brainstormRound`: current round / step within the loop
- `selectedBranch`: retained branch id awaiting or having just completed backfill

### 2. `narrativeIntelligence.styleRisk.*`

Extend style-risk storage:

```json
"styleRisk": {
  "clichePatterns": [],
  "lastCokeScore": null,
  "lastClicheScanStage": null,
  "noveltyAxes": []
}
```

Field meanings:
- `clichePatterns`: known backslide risks or detected cliché patterns
- `lastClicheScanStage`: latest stage where cliché-risk scan ran
- `noveltyAxes`: retained axes that define where this project intentionally departs from default patterns

Design choice:
- `review.*` tracks control flow
- `styleRisk.*` tracks creative-risk state

## Branch Management Behavior

Extend existing branch-management support instead of adding a second branch-control system.

Desired capabilities:
- create `cliche_exhaustion` branches with scaffolded files
- mark one branch as selected
- immediately delete stale siblings once a branch is promoted
- clear stale selection metadata after canonical backfill completes

Hard cleanup rules:
- keep only the active branch and the selected branch during decision time
- after backfill, delete sibling branch files for that ideation focus
- do not leave expired ideation artifacts in the project tree

## Approval and Backfill Rules

### 1. Formal planning approval gate

For deep-mode `Story Planning`, the parent should not approve planning until all three are true:
- cliché samples were enumerated
- deviation reasons were written down
- first-10-chapter payoff logic was explained

### 2. Canonical file boundary

Exploration artifacts stay in `staging/`.

Canonical files remain:
- `00_选题报告.md`
- `01_想法.md`
- `02_大纲.md`
- `04A_开篇设计.md`

Only selected, retained conclusions may be copied back.

### 3. Cleanup after promotion

Once a branch is selected and backfilled:
- delete stale sibling branches
- clear obsolete branch-tracking state
- do not leave “candidate 1 / candidate 2 / candidate 3” debris in canonical files

## Implementation Phasing

## Phase 1: MVP

Focus:
- protocol + docs + state + branch scaffolding

Files:
- add `references/cliche-exhaustion.md`
- update workflow / outlining / market research / topic template / opening / proofreading / anti-template docs
- update state docs and file-structure docs
- extend `revision_utils.py`
- extend `load_project_state.py`
- extend `manage_stage_branches.py`

Tests:
- docs assertions
- state default / reconstruction coverage
- branch scaffold / branch cleanup coverage

## Phase 2: Proofreading backslide detection

Focus:
- lightweight cliché-risk detection during accepted proofreading

Files:
- extend `narrative_checker.py`
- extend `update_narrative_intelligence.py`
- extend `apply_stage_execution_result.py`
- extend `novel_project_status.py`
- optionally extend `write_final_review.py`

Tests:
- cliché-risk findings recorded in state
- status output includes cliché-risk summary
- severe findings can affect final-review blockers

## Phase 3: Advanced guidance

Focus:
- richer supervisor prompts and deeper automated pressure-test suggestions

This phase is explicitly lower priority than getting the protocol and branch discipline correct.

## Risks

1. over-mechanization
   If the anti-cliche loop becomes too rigid, it may produce procedural busywork instead of sharper taste.

2. excessive ideation drag
   If deep mode is applied everywhere, it may slow normal workflow too much.

3. false novelty
   Surface-level mutation can look fresh without changing the structural engine.

4. state bloat
   Too many ideation-control fields would make recovery and status output noisy.

Mitigations:
- keep quick mode available
- limit hard gating to `Story Planning`
- store only minimal control metadata
- defer heavy scoring until later

## Open Questions

Questions intentionally deferred to implementation planning:
- should `brainstormRound` be numeric only, or support labels like `enumeration`, `mutation`, `selection`
- should `noveltyAxes` be free text, or constrained to an enum
- should severe cliché findings feed `finalBlockingIssues` immediately, or only via revision / final-review integration
- whether `Discovery` should persist quick-mode branch artifacts every time, or only when the operator explicitly asks for visible branch files

## Recommendation

Implement the standard version in this order:

1. docs + protocol + `staging/` structure
2. minimal state fields + branch-management support
3. lightweight proofreading backslide detection

This order matches the actual theory:
- the most important change is not scoring
- the most important change is making “reject the first obvious answers” a formal production step
