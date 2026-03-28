# Novel Studio Supervisor Persistence Design

## Goal

Reshape `novel-studio` so the parent agent behaves as a workflow supervisor instead of a mixed-role writer.

The new model must fix the current failure mode where the parent:
- finishes enough stage work to count as a real artifact
- does not persist that artifact accurately
- keeps acting as if the workflow is still in open discussion

After this change:
- the parent agent owns workflow control, user communication, approval interpretation, persistence decisions, and subagent dispatch
- execution work defaults to stage subagents where appropriate
- every stage must persist approved-scope work into canonical files as soon as a minimum usable artifact exists
- open-ended discussion must not survive after a formal artifact has already been written

## Problem Statement

The current workflow drifts in two ways:

1. stage boundaries are too soft  
   The parent can move from discussion into substantial draft work without flipping the workflow into an explicit stage gate.

2. persistence is too late or absent  
   The parent can produce meaningful discovery, planning, or drafting content in chat, but fail to write it into canonical project files. This leaves `.novel-state.json` and the file tree behind the actual work.

This creates a harmful mismatch:
- files say the project is still earlier than it really is
- state says the project is still discussing
- the parent keeps improvising instead of forcing review and approval

The new design treats accurate persistence and explicit approval gates as first-class workflow guarantees.

## Non-Goals

This design does not attempt to:
- replace the existing file-backed project structure
- remove the current staged workflow
- persist runtime agent ids, session ids, execution bundles, or raw child chat history into `.novel-state.json`
- build a fully generic stage runtime abstraction in the first implementation pass
- keep historical brainstorm branches after a branch has been accepted or discarded

## User-Facing Outcome

After this change, the operator-facing behavior should be:

1. The parent agent talks to the user, decides the current stage, and decides whether the workflow is in formal mode or explicit brainstorming mode.
2. Once a stage reaches a minimum usable artifact, the workflow writes the canonical file immediately instead of keeping the result only in chat.
3. The moment a canonical file is written or refreshed, the workflow enters a stage-specific approval gate instead of pretending the work is still in discussion.
4. Brainstorming branches are allowed only when explicitly requested; they live under `staging/` and are cleaned up once a branch is adopted or rejected.
5. The parent agent no longer silently holds unpublished stage results in chat memory.

In short: the parent becomes a strict production supervisor, not an informal collaborator who may or may not have persisted the work.

## Recommended Approach

Use a supervisor-first workflow with two execution patterns:

### 1. Child produces, parent persists

Use this pattern for document-heavy stages where precise file ownership matters more than raw throughput:
- `discovery`
- `story-planning`
- `character-system`
- `drafting` opening substage
- `final-review`

In these stages:
- the child returns structured artifact updates
- the parent validates stage scope and artifact quality
- the parent writes canonical files
- the parent updates state and approval gates immediately after persistence

This is the safest way to prevent inaccurate or premature file writes in early stages.

### 2. Child writes, parent validates

Keep this pattern for execution-heavy stages where bounded filesystem writes are already a good fit:
- `drafting`
- `polishing`
- `proofreading`

In these stages:
- the parent prepares the allowed write scope
- the child writes only inside that scope
- the parent validates the actual diff and applies state changes only after validation

`proofreading` remains special: it should write only its formal report file and must never modify `manuscript/`.

## Canonical File Policy

### 1. Direct formal persistence is the default

Formal mode writes directly into canonical project files.

The workflow should not wait for stage completion before writing files.
It should write as soon as the current file reaches the stage-specific minimum usable threshold.

That means:
- discovery updates canonical discovery files during discovery
- planning updates canonical planning files during planning
- character work updates canonical character files during character-system
- drafting and polishing write canonical manuscript files directly
- proofreading writes a canonical proofreading report directly
- final review writes `07_终审报告.md` directly

### 2. `staging/` is only for explicit brainstorming or branch exploration

`staging/` is not a general scratch area.
It exists only when the user explicitly asks for:
- brainstorming
- multiple candidate directions
- branch comparison
- temporary creative divergence before selecting one branch

Recommended structure:

```text
staging/
└── <stage>/
    └── <branch-id>/
        ├── notes.md
        └── <candidate files...>
```

Rules:
- no `staging/` writes without explicit brainstorming intent
- branch ids should be stable, readable labels rather than opaque random ids
- only currently active branches may remain on disk
- once a branch is adopted, its accepted content is copied back into canonical files
- once a branch is rejected, its files are deleted
- after branch resolution, stale `staging/` files for that stage must be removed promptly

### 3. Canonical files must stay clean

The parent must not:
- append chat transcripts into canonical files
- keep abandoned branch notes in canonical locations
- create placeholder files that do not meet the stage minimum quality bar
- leave outdated candidate files next to canonical artifacts after branch resolution

## Minimum Usable Artifact Rules

Persistence should trigger when a file reaches a minimum usable threshold, not when a stage is globally complete.

### Discovery

Persist as soon as each artifact becomes structurally usable:
- `00A_热点扫描.md` once there is a source-backed signal summary
- `00B_用户偏好.md` once user constraints and preferences have been structured
- `00C_底盘与切口决策.md` once a lane/platform/cut recommendation exists
- `00_选题报告.md` once the current recommendation, title candidates, and rationale are usable

Discovery therefore becomes a sequence of formal file updates, not one delayed write at the end.

### Story planning

Persist:
- `01_想法.md` once the story promise, hook, and conflict engine are usable
- `02_大纲.md` once the main progression and turning points are usable
- `04_章节骨架.md` only when a real chapter skeleton exists

Do not create empty planning shells just to satisfy file count.

### Character system

Persist:
- `03_人物小传.md` once the main cast package is usable
- `characters/*.md` one role at a time once each role is drafting-ready

Do not treat label-only profiles as usable character artifacts.

### Drafting and polishing

Persist directly into `manuscript/*.md`.

These stages must never leave their substantive output only in chat.

### Proofreading

Add a canonical proofreading report:
- `05A_本轮校对报告.md`

This file stores the latest accepted review artifact for the active batch and is overwritten on re-check.
It is not an append-only historical log.

Required contents:
- batch range
- `judgment`
- `continuity`
- `logic`
- `characterOOC`
- `blockers`
- `fixDirection`
- `summary`

### Final review

Persist directly into:
- `07_终审报告.md`

## Stage Ownership Model

### Parent agent responsibilities

The parent owns:
- determining the active stage
- determining whether the workflow is in formal mode or brainstorming mode
- checking readiness and approval gates
- defining allowed artifacts for the current step
- deciding whether a child may write directly or only propose artifact updates
- validating artifact completeness and write scope
- persisting canonical files when persistence is parent-owned
- validating child writes when persistence is child-owned
- updating `.novel-state.json`
- presenting stage reports and waiting for explicit user approval
- cleaning obsolete branches and expired staging content

### Child agent responsibilities

Children are execution workers, not workflow owners.

They must not:
- choose the active stage
- invent canonical filenames
- advance approval state
- decide that a persisted artifact can still be treated as discussion
- keep orphaned brainstorm artifacts alive after branch resolution

### Stage mode split

Use the following default ownership:

| Stage | Child behavior | Parent behavior |
| --- | --- | --- |
| `discovery` | return structured artifact updates | validate + persist + gate |
| `story-planning` | return structured artifact updates | validate + persist + gate |
| `character-system` | return structured artifact updates | validate + persist + gate |
| `drafting` opening substage | return structured artifact updates | validate + persist + gate |
| `drafting` | write approved manuscript targets | validate diff + gate |
| `polishing` | write approved manuscript targets | validate diff + gate |
| `proofreading` | write only `05A_本轮校对报告.md` | validate diff + gate |
| `final-review` | return structured report update | validate + persist + gate |

The opening package remains a `drafting` substage concern.
It should not introduce a new top-level `workflow.currentStage` value.

## Approval and Gate Model

The workflow must stop using a vague “still discussing” state once a canonical artifact has been written.

### Review gates

Expand `review.currentGate` to support all formal stages:
- `waiting_discovery_feedback`
- `waiting_planning_feedback`
- `waiting_character_feedback`
- `waiting_opening_feedback`
- `waiting_draft_feedback`
- `waiting_polishing_feedback`
- `waiting_proofreading_feedback`
- `waiting_final_review_feedback`

### Core gate rule

If any canonical artifact was newly written or refreshed for the current stage and is awaiting user decision:
- `review.pendingArtifactPaths` must be non-empty
- `review.currentGate` must point at the current stage gate
- `workflow.status` must be `awaiting_user_approval`

The workflow must not remain in:
- `collecting_inputs`
- `producing_artifact`
- `brainstorming`

while unpublished approval work already exists in canonical files.

### Approval progression

When the user explicitly approves the stage:
- clear `review.pendingArtifactPaths`
- clear the stage gate in `review.currentGate`
- mark the stage approval boolean
- update `workflow.lastCompletedStage`
- advance `workflow.currentStage` and `workflow.nextStage`

## Workflow Status Model

Replace the broad current status handling with a small explicit set:
- `collecting_inputs`
- `producing_artifact`
- `awaiting_user_approval`
- `brainstorming`
- `blocked`

### Meanings

`collecting_inputs`
- still gathering constraints or clarifications
- no canonical artifact is yet ready to persist

`producing_artifact`
- stage work is actively being turned into a formal artifact
- persistence has not happened yet

`awaiting_user_approval`
- a canonical artifact was written for the current stage
- the workflow is now waiting for explicit user feedback or approval

`brainstorming`
- explicit branch exploration is active
- staging files are allowed

`blocked`
- preconditions, validation rules, or approval rules prevent advancement

### Hard status rule

A stage with unapproved canonical artifact updates must always be `awaiting_user_approval`.

## State Model Changes

Augment `.novel-state.json` instead of replacing it.

### New or extended review fields

Under `review.*`, add:
- `pendingArtifactPaths: []`
- `lastPersistedStage: null`
- `lastPersistedAt: null`
- `brainstormActive: false`
- `activeBranches: []`

These fields mean:
- `pendingArtifactPaths` tracks formal files awaiting approval
- `lastPersistedStage` prevents stage drift after persistence
- `lastPersistedAt` records the last formal write moment
- `brainstormActive` marks explicit branch mode
- `activeBranches` tracks only the currently valid staging branches

### Required invariants

1. If `review.pendingArtifactPaths` is non-empty, `workflow.status` must be `awaiting_user_approval`.
2. If `workflow.status == "brainstorming"`, then `review.brainstormActive` must be `true`.
3. If `review.activeBranches` is empty, stale staging branches for resolved stages should not remain on disk.
4. Persisted stage artifacts must never leave `review.currentGate` unset.

## File Scope Enforcement

To prevent inaccurate persistence, every stage must have an explicit file whitelist.

### Discovery

Allowed canonical targets:
- `00A_热点扫描.md`
- `00B_用户偏好.md`
- `00C_底盘与切口决策.md`
- `00_选题报告.md`

### Story planning

Allowed canonical targets:
- `01_想法.md`
- `02_大纲.md`
- `04_章节骨架.md`

### Character system

Allowed canonical targets:
- `03_人物小传.md`
- `characters/*.md`

### Drafting opening substage

Allowed canonical targets:
- `04A_开篇设计.md`
- optionally `05_本轮章节规划.md` if the parent intentionally bundles opening-to-batch planning in one controlled step

### Drafting

Allowed canonical targets:
- approved `manuscript/*.md` files for the active batch only

### Polishing

Allowed canonical targets:
- approved `manuscript/*.md` files for the active batch only

### Proofreading

Allowed canonical targets:
- `05A_本轮校对报告.md`

### Final review

Allowed canonical targets:
- `07_终审报告.md`

The parent should reject any result that attempts to write outside the stage whitelist.

## Implementation Strategy

Do not begin with a fully generic runtime refactor.
Fix the stage-drift bug first.

### Phase 1: State and gate repair

Primary goal:
- eliminate the case where formal work exists but the workflow still thinks it is “in discussion”

Update:
- `skills/novel-studio/scripts/revision_utils.py`
- `skills/novel-studio/scripts/load_project_state.py`
- `skills/novel-studio/scripts/novel_project_status.py`
- `skills/novel-studio/scripts/check_stage_ready.py`

Add:
- new `workflow.status` semantics
- full-stage review gates
- pending artifact tracking
- persistence metadata fields

### Phase 2: Formal persistence protocol

Primary goal:
- force early-stage artifacts through an explicit validate-and-persist path

Add:
- stage file whitelist helpers
- minimum artifact threshold checks
- `05A_本轮校对报告.md` support
- parent-side persistence helpers for document stages

### Phase 3: Early-stage supervisor delegation

Primary goal:
- move `discovery`, `story-planning`, `character-system`, and `final-review` into subagent-assisted execution without giving children uncontrolled write authority

Add:
- structured `artifactUpdates` contracts
- stage-specific child prompts
- parent-side artifact validation and persistence

### Phase 4: Brainstorm branch lifecycle

Primary goal:
- keep explicit brainstorming useful without polluting canonical workflow state

Add:
- staging branch creation rules
- branch adoption flow
- branch cleanup flow
- stale staging cleanup enforcement

## Testing Strategy

Add or extend tests to cover:

1. persistence flips the workflow into the matching approval gate
2. persisted discovery artifacts cannot leave the workflow in discussion status
3. persisted planning artifacts cannot leave the workflow in discussion status
4. `pendingArtifactPaths` and `workflow.status` invariants hold
5. `proofreading` writes only `05A_本轮校对报告.md`
6. early-stage child results cannot write outside their file whitelist
7. explicit brainstorming writes into `staging/` only
8. branch adoption copies selected content back to canonical files and removes rejected branches
9. stale staging files are removed after branch resolution
10. `novel_project_status.py` reports the new gates and status model correctly

## Risks and Mitigations

### Risk: persistence becomes too eager

Mitigation:
- persist only after file-specific minimum usable thresholds
- reject placeholder-only outputs

### Risk: the parent still drifts after persistence

Mitigation:
- make `pendingArtifactPaths -> awaiting_user_approval` an enforced invariant
- fail validation if a persisted artifact does not set a gate

### Risk: early-stage children still write incorrect files

Mitigation:
- make early-stage children return artifact proposals instead of direct file writes
- keep direct child writes limited to execution-heavy bounded stages

### Risk: brainstorming pollutes formal workflow

Mitigation:
- allow `staging/` only under explicit brainstorming mode
- require branch cleanup immediately after branch resolution

## Summary

The first implementation goal is not “more subagents.”
It is “no more silent drift between real work, persisted files, and workflow state.”

This design gets there by making four things strict:
- canonical persistence happens as soon as a file becomes usable
- persisted artifacts immediately open a stage approval gate
- the parent agent remains the workflow supervisor and persistence authority
- brainstorming branches are explicit, bounded, and cleaned up once resolved
