# Novel Studio Chapter Progress Reporting Design

## Goal

Add a hard, file-backed chapter-progress model to `novel-studio` so the parent supervisor can reliably report chapter execution progress during drafting work instead of only reporting batch-level summaries.

After this change:
- the parent still owns workflow control, approval interpretation, persistence, and user communication
- chapter execution progress becomes an explicit part of `.novel-state.json`
- every meaningful chapter-status change can be reported to the user from state rather than improvised from chat memory
- interruption recovery no longer loses “which chapter is writing / polishing / awaiting review” information

## Problem Statement

The current supervisor-first workflow already persists stage gates and batch summaries, but it still has a blind spot:
- it knows the active batch
- it knows the last delegated stage
- it knows whether drafting / polishing / proofreading for the batch has completed
- it does not know which individual chapters are currently in progress
- it does not persist which progress changes still need to be reported to the user

This creates three practical failures:

1. progress is too coarse  
   The operator can see only batch-level status such as “drafting completed” or “last delegation summary,” not chapter-level movement such as “第2章润色中 / 第1章审核中”.

2. reporting is not durable  
   If the parent reports progress only from runtime context, interruption or restart can lose unsent progress changes.

3. status output cannot answer the user’s real question  
   `novel_project_status.py` can summarize the workflow, but it cannot describe chapter-by-chapter execution state for the active batch.

The design must fix these failures without changing the top-level workflow stage model and without weakening the existing canonical-file persistence rules.

## Non-Goals

This design does not attempt to:
- add a new top-level workflow stage
- replace the existing batch-level state fields such as `draftComplete` or `polishingComplete`
- persist runtime subagent ids, session ids, raw execution packages, or raw child conversation history
- turn `staging/` into a generic execution workspace
- expose raw protocol state directly to the user instead of human-readable progress language
- model book-level final delivery as a per-chapter runtime phase

## User-Facing Outcome

After this change, the parent supervisor should be able to produce progress updates like:
- `第1章初稿中`
- `第1章初稿待审核`
- `第2章润色中`
- `第2章校对待审核`
- `第3章阻塞：人物口吻漂移`
- `第1章已完成`

The parent may merge multiple changes into one report when they happen in the same turn, for example:

`第1章初稿待审核；第2章进入润色；第3章校对中。`

These reports must come from persisted state, not only from transient runtime memory.
In this design, `已完成` means the chapter has completed the current batch execution pipeline after proofreading approval for that batch, not that the whole book has passed final delivery.

## Recommended Approach

Use a chapter-task model under the active batch plus a lightweight persisted progress-event queue.

### 1. Chapter tasks are the source of truth

Add a chapter-level state model under `batch.chapterTasks`.

Each chapter task represents one approved chapter in the active batch and tracks:
- which workflow phase the chapter is in
- whether that phase is queued, actively running, waiting for user review, completed, or blocked
- the latest short summary
- the latest blockers
- when the task last changed

### 2. Progress reports are generated from persisted events

Add `batch.pendingProgressItems` as a lightweight queue of unsent or newly generated progress changes.

Every chapter-status transition writes an event into this queue first.
The parent supervisor then:
- reads pending events
- merges them into a concise user-facing summary
- reports the summary to the user
- marks the included events as reported

This guarantees that progress reporting survives interruption.

### 3. Status output remains human-readable

`novel_project_status.py` should continue to translate state into readable Chinese progress lines rather than dumping raw JSON concepts such as `phaseStatus=awaiting_user_review`.

## State Model

### 1. `batch.chapterTasks`

Add a new ordered list:

```json
"chapterTasks": [
  {
    "chapterLabel": "第1章",
    "manuscriptPath": "manuscript/第1章_开端.md",
    "phase": "drafting",
    "phaseStatus": "in_progress",
    "lastSummary": "已开始第1章初稿",
    "blockers": [],
    "updatedAt": "2026-03-28T10:00:00Z"
  }
]
```

Field definitions:
- `chapterLabel`: required stable identifier for the chapter inside the current batch, for example `第1章`
- `manuscriptPath`: approved canonical manuscript path when known; this may be `null` before the first concrete manuscript target is bound
- `phase`: one of `drafting`, `polishing`, or `proofreading`
- `phaseStatus`: one of `queued`, `in_progress`, `awaiting_user_review`, `completed`, or `blocked`
- `lastSummary`: latest short state summary for this chapter
- `blockers`: latest blocking reasons for this chapter
- `updatedAt`: ISO timestamp for the latest state change

Design choice:
- there is no separate `review` phase
- “审核中” is represented as `phaseStatus = awaiting_user_review` on the current phase
- `completed` means the chapter has completed the current batch execution pipeline after proofreading approval for that batch

`final-review` remains book-level and is not represented as a per-chapter runtime phase. Otherwise finished batch chapters would remain permanently open until whole-book delivery.

### 2. `batch.pendingProgressItems`

Add a new ordered list of lightweight progress events:

```json
"pendingProgressItems": [
  {
    "eventId": "drafting-第1章-2026-03-28T10:00:00Z",
    "chapterLabel": "第1章",
    "phase": "drafting",
    "phaseStatus": "awaiting_user_review",
    "summary": "第1章初稿待审核",
    "blockers": [],
    "createdAt": "2026-03-28T10:00:00Z",
    "reportedAt": null
  }
]
```

Field definitions:
- `eventId`: stable unique id for the event
- `chapterLabel`: chapter affected by the transition
- `phase`: resulting phase after the transition
- `phaseStatus`: resulting phase status after the transition
- `summary`: user-facing summary candidate for this event
- `blockers`: blockers to surface if the event is blocked
- `createdAt`: event creation time
- `reportedAt`: `null` until the parent successfully reports the event to the user

The queue stores only lightweight progress facts. It must never store raw subagent output, runtime ids, or dispatch artifacts.

## State Initialization and Recovery

### 1. Initialization on chapter-plan approval

When the current batch chapter plan is explicitly approved, initialize `chapterTasks` from the approved chapter list in `05_本轮章节规划.md`.

Initialization rules:
- preserve chapter order from the approved plan
- create one task per approved chapter
- set each task to `phase = drafting`, `phaseStatus = queued`
- leave `manuscriptPath = null` until a concrete manuscript target is known, unless the approved plan already maps the chapter to a canonical file path
- clear stale `pendingProgressItems` from any previous batch before creating new batch tasks

### 2. Reconstruction for older projects

For older `.novel-state.json` files that do not yet contain `chapterTasks` or `pendingProgressItems`:
- normalization should add empty defaults
- if a batch is active and the chapter plan is approved, recovery code may reconstruct `chapterTasks` from the approved chapter plan plus any existing manuscript targets
- if the workflow cannot derive an unambiguous chapter list, the parent must not invent chapter tasks from guesswork

Accurate progress is a hard requirement. Ambiguous chapter identity is a blocking condition, not a cue to improvise.

## Chapter State Transitions

### 1. Phase progression

The canonical per-chapter phase progression is:

`drafting -> polishing -> proofreading -> completed`

There is no direct skip over an earlier phase for a chapter in the normal path.

### 2. Required transition points

The parent must update chapter tasks at these points:

1. chapter plan approved  
   Initialize all approved chapters as `drafting / queued`.

2. stage dispatch starts  
   Target chapters move to `<current phase> / in_progress`.

3. child result accepted with `status = completed`  
   Target chapters move to `<current phase> / awaiting_user_review`.

4. user approves the current gate  
   Target chapters move to the next phase:
   - draft approval -> `polishing / queued`
   - polishing approval -> `proofreading / queued`
   - proofreading approval -> `proofreading / completed`

5. child result accepted with `status = blocked` or `needs_clarification`  
   Target chapters move to `<current phase> / blocked`.

### 3. Transition invariants

- the parent must never jump a chapter directly from `drafting / queued` to `proofreading / in_progress`
- the parent must never mark a chapter `completed` before proofreading approval for that batch
- the parent must never update chapter progress only in chat without writing the state change
- the parent must never update chapter tasks for chapters outside the approved dispatch scope

## Chapter Scope Resolution

The parent needs an explicit way to know which chapter tasks a dispatch affects.

### 1. Required chapter-label resolution

For dispatches that affect chapter tasks, the parent must resolve an explicit ordered chapter-label list before delegation.

Recommended runtime contract:
- derive `chapterLabels` from the approved chapter plan
- include that ordered list in the dispatch package under structured inputs
- use the same `chapterLabels` during result application instead of reparsing human prose summaries

### 2. Stage-specific resolution rules

- `drafting`: `chapterLabels` must match the approved manuscript target files for the dispatch
- `polishing`: `chapterLabels` must match the approved manuscript target files for the dispatch
- `proofreading`: `chapterLabels` must represent all chapters covered by the current batch proofreading pass, even though proofreading still writes only `05A_本轮校对报告.md`

If the parent cannot derive chapter labels accurately, it must stop before dispatch and ask for correction rather than emit inaccurate chapter progress.

## Progress Event and Reporting Rules

### 1. Every transition creates an event

Whenever a chapter task changes `phase` or `phaseStatus`, the parent must append a corresponding event to `pendingProgressItems`.

### 2. Reporting is mergeable, not lossy

The parent may merge multiple pending events into one user-facing report, but merging must follow these rules:
- merge only unsent events where `reportedAt` is `null`
- collapse repeated same-turn changes for the same chapter to the latest meaningful state
- do not keep obsolete lower-value states if the chapter already advanced further in the same unsent batch
- preserve distinct chapter outcomes in the same summary
- do not merge blockers into a neutral progress line if the blocked state needs explicit attention

Example:
- unsent events: `第1章初稿中`, `第1章初稿待审核`, `第2章润色中`
- reported summary: `第1章初稿待审核；第2章润色中`

### 3. Reporting acknowledgment

Only after the parent successfully reports a summary to the user may it set `reportedAt` on the included events.

If the session is interrupted before reporting succeeds, the events remain pending and can be re-reported or re-merged on recovery.

## Human-Readable Mapping

The parent and status tools must use these default renderings:

| Phase | Phase status | Human text |
| --- | --- | --- |
| `drafting` | `queued` | `第X章待写` |
| `drafting` | `in_progress` | `第X章初稿中` |
| `drafting` | `awaiting_user_review` | `第X章初稿待审核` |
| `polishing` | `queued` | `第X章待润色` |
| `polishing` | `in_progress` | `第X章润色中` |
| `polishing` | `awaiting_user_review` | `第X章润色待审核` |
| `proofreading` | `queued` | `第X章待校对` |
| `proofreading` | `in_progress` | `第X章校对中` |
| `proofreading` | `awaiting_user_review` | `第X章审核中` |
| any phase | `blocked` | `第X章阻塞` |
| `proofreading` | `completed` | `第X章已完成` |

If blockers exist, append the first meaningful blocker after a colon.

Example:
- `第2章阻塞：人物口吻漂移`

## Status Summary Output

`scripts/novel_project_status.py` must expose chapter progress in both brief and full modes.

### 1. Brief mode

Add:
- `章节进度：...`
- `待汇报变更：...` when unreported events exist

Example:

```text
章节进度：第1章初稿待审核；第2章润色中；第3章已完成
待汇报变更：第2章进入润色；第1章初稿待审核
```

### 2. Full mode

Add a dedicated section listing:
- chapter label
- manuscript path if known
- current phase
- current phase status
- blockers
- updated time

The status tool should remain readable by default. Raw JSON remains available through `--json`.

## Integration Points

The design should integrate into the current supervisor persistence path rather than creating a parallel status system.

Primary integration points:
- `scripts/revision_utils.py`
  - add defaults and normalization for `batch.chapterTasks` and `batch.pendingProgressItems`
- `scripts/apply_stage_execution_result.py`
  - update chapter tasks and append progress events when accepted child results change chapter execution state
- stage approval / gate scripts
  - initialize chapter tasks on chapter-plan approval
  - advance chapter phases when the user approves draft, polishing, and proofreading gates
- `scripts/novel_project_status.py`
  - render chapter progress and pending progress changes
- state documentation
  - update state references and templates so chapter progress becomes part of the canonical persistence contract

## Error Handling

### 1. Ambiguous chapter identity

If the system cannot determine which chapter tasks a dispatch or approval applies to:
- do not guess from prose summaries
- do not emit chapter-level progress updates
- stop and surface the ambiguity as a blocking condition

### 2. Stale event cleanup

When a new batch starts:
- discard old `chapterTasks`
- discard stale unreported events from the closed batch

When a chapter advances again before pending events are reported:
- keep the latest chapter state authoritative
- allow report merging to suppress obsolete intermediate events

### 3. Backward compatibility

Older states without chapter progress fields must continue to load.
The absence of `chapterTasks` in an old state file is not itself an error.

## Testing Strategy

The implementation should add or update tests for:

1. state normalization  
   Older state files load with default `chapterTasks` and `pendingProgressItems`.

2. chapter-plan approval initialization  
   Approved chapter plans initialize ordered queued chapter tasks.

3. dispatch start transitions  
   Drafting, polishing, and proofreading dispatches mark the correct target chapters as `in_progress` and emit progress events.

4. accepted child results  
   Completed child results move chapter tasks to `awaiting_user_review`; blocked and clarification results move them to `blocked`.

5. approval transitions  
   User approval advances chapter tasks into the next queued phase and proofreading approval marks them `completed`.

6. event merging and reporting persistence  
   Multiple chapter changes can be merged into one summary without losing the latest state, and interrupted sessions do not lose unreported changes.

7. status rendering  
   `novel_project_status.py --brief` and full mode both show readable chapter progress output.

8. state hygiene  
   No runtime subagent ids, raw execution bundles, or raw child responses appear in chapter progress fields.

## Success Criteria

The design is successful when:
- the parent supervisor can always answer “哪一章在写、哪一章在润色、哪一章在审核”
- progress changes survive interruption because they are file-backed
- chapter progress reports are generated from explicit state transitions rather than improvised from runtime memory
- the feature does not weaken canonical-file persistence discipline or introduce a new top-level workflow stage
