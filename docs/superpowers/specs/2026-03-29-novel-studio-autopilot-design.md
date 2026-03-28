# Novel Studio Autopilot Approval Design

## Goal

Add a temporary, file-backed autopilot approval layer to `novel-studio` so the parent supervisor can continue the formal workflow automatically after explicit user authorization, while preserving the existing approval-gate model, subagent execution boundaries, and progress reporting rules.

After this change:
- default behavior remains manual approval
- autopilot activates only after explicit user authorization plus an explicit terminal chapter goal
- autopilot may auto-approve scope, chapter-plan, drafting, polishing, and proofreading gates
- drafting, polishing, and proofreading work must still be executed by subagents rather than silently absorbed by the parent
- progress updates still reach the user during autopilot
- every autopilot stop must be explicit, persisted, and surfaced to the user

## Problem Statement

The current supervisor-first workflow is intentionally strict:
- persisted output opens a gate
- the parent waits for explicit human approval
- nothing advances without that approval

This is correct by default, but it creates friction for a common operator instruction:

`后续你来主控，继续到第X章结束。`

Today the parent can orchestrate the workflow, but it still cannot continue through multiple formal approval gates without the user manually re-confirming each step. That causes three practical issues:

1. high-friction long runs  
   A user who has already delegated control for a bounded run still has to manually approve every scope gate, chapter-plan gate, and execution gate.

2. no durable delegation contract  
   There is no explicit persisted record saying the parent is temporarily authorized to keep advancing until a concrete stop condition is reached.

3. stop conditions are underspecified  
   If the workflow stalls, gets blocked, or the user interrupts with new requirements, there is no dedicated persisted control layer that explains why the automated run ended.

The design must solve these issues without weakening the current gate model and without allowing the parent to bypass subagent execution.

## Non-Goals

This design does not attempt to:
- make autopilot the default mode
- permanently disable manual approval gates
- allow vague messages such as `继续` to enable automatic advancement
- let the parent directly write draft, polishing, or proofreading output instead of dispatching subagents
- auto-run book-level `final-review`
- hide or compress autopilot stop reasons into generic status text
- replace existing `review`, `revision`, or `workflow` state models

## User-Facing Outcome

After this change, the user may explicitly delegate bounded workflow control with messages like:
- `后续你来主控，继续到第10章结束`
- `继续流程，直到第12章结束`

If the delegation is accepted, the parent should:
- persist that bounded authorization
- keep advancing through formal gates within that authorized scope
- continue reporting progress such as `第8章初稿待审核；第8章进入润色；第9章初稿中`
- stop automatically when the authorized end condition is reached
- stop immediately and explicitly if a blocking condition occurs

Stopping must be visible to the operator. Example stop messages:
- `自动流程已停止：第7章润色 blocked：人物口吻漂移`
- `自动流程已停止：validate 失败，子结果未通过协议校验`
- `自动流程已停止：已达到授权终点，第10章已完成校对并自动通过审批`

## Recommended Approach

Keep the existing approval-gate system intact and add a separate top-level persisted `autoPilot` control model.

### 1. Autopilot is a temporary approval controller

Autopilot does not remove gates.
It only changes who approves them after explicit user authorization.

Normal flow:
- parent opens a gate
- user confirms
- parent calls `approve_stage_gate.py`

Autopilot flow:
- parent opens a gate
- parent checks the active `autoPilot` contract
- if auto-approval is still allowed, the parent calls `approve_stage_gate.py` automatically
- if autopilot must stop, the parent stops and reports the reason instead of advancing

### 2. Execution boundaries remain unchanged

Autopilot must never let the parent silently absorb execution work.

Hard rule:
- `drafting`, `polishing`, and `proofreading` still require subagent dispatch
- the parent may only orchestrate, validate, persist, report, and approve
- the parent must never write chapter draft / polish / proofreading outputs itself to satisfy autopilot progression

### 3. Autopilot must be bounded and durable

An autopilot authorization must:
- be created only from explicit user intent
- include an explicit terminal chapter
- be written to `.novel-state.json`
- survive interruption and restart
- end automatically when the target condition is reached or a stop condition fires

## Activation Rules

### 1. Default behavior

Manual approval remains the default.

Autopilot must not activate from vague approvals such as:
- `继续`
- `可以`
- `好`
- `往下做`

### 2. Required activation contract

Autopilot activates only if the user message includes both:
- explicit delegation intent
- an explicit terminal chapter label

Examples that should qualify:
- `后续你来主控，继续到第10章结束`
- `继续流程，直到第12章结束`

Examples that must not qualify:
- `继续`
- `你看着办`
- `往后推进`
- `写到后面再说`

### 3. Terminal condition

The terminal condition is fixed:

`goal chapter proofreading completed and proofreading gate automatically approved`

This design intentionally stops before `final-review`.

### 4. Replacing an active authorization

If the user explicitly issues a new qualified autopilot goal while an older autopilot session is active:
- the current autopilot session must stop immediately
- its stop reason becomes `superseded_by_new_user_goal`
- a new autopilot session starts from the new user instruction

The parent must not silently merge the two authorizations.

## Scope of Automatic Approval

When `autoPilot.active = true`, the parent may automatically approve these workflow checkpoints if all other autopilot conditions are satisfied:
- current batch scope confirmation
- current batch chapter-plan approval
- `waiting_draft_feedback`
- `waiting_polishing_feedback`
- `waiting_proofreading_feedback`

It must not automatically approve:
- `final-review`
- revision gates
- any gate outside the authorized workflow path

## State Model

Add a new top-level object:

```json
"autoPilot": {
  "active": false,
  "goalChapter": null,
  "goalCondition": "proofreading_completed",
  "startedAt": null,
  "startedBy": null,
  "lastProgressAt": null,
  "lastProgressSummary": null,
  "stopReason": null,
  "stoppedAt": null,
  "awaitingManualResume": false
}
```

Field definitions:
- `active`: whether autopilot is currently authorized to continue approvals
- `goalChapter`: terminal chapter label such as `第10章`
- `goalCondition`: fixed string `proofreading_completed`
- `startedAt`: ISO timestamp for autopilot activation
- `startedBy`: the source user instruction summary that opened autopilot
- `lastProgressAt`: latest time autopilot recorded progress
- `lastProgressSummary`: latest merged progress summary sent or prepared
- `stopReason`: explicit last stop reason if autopilot has ended or paused
- `stoppedAt`: ISO timestamp for the latest autopilot stop
- `awaitingManualResume`: whether the workflow is waiting for manual intervention before autopilot can continue again

Design choice:
- `autoPilot` is top-level instead of being nested under `review` or `workflow`
- `review` continues to mean gate state
- `workflow` continues to mean stage position
- `autoPilot` is a separate temporary control contract

## State Transitions

### 1. Activation

When a qualifying user instruction is accepted:
- set `autoPilot.active = true`
- set `goalChapter`
- set `goalCondition = proofreading_completed`
- set `startedAt`
- set `startedBy`
- clear old `stopReason`
- clear old `stoppedAt`
- set `awaitingManualResume = false`

### 2. Ordinary progress

Whenever autopilot continues successfully through a loop:
- update `lastProgressAt`
- update `lastProgressSummary`

### 3. Normal completion

When the goal chapter reaches `proofreading / completed` by the current chapter-progress model and the proofreading gate has been auto-approved:
- set `active = false`
- set `stopReason = goal_reached`
- set `stoppedAt`
- set `awaitingManualResume = true`

### 4. Forced stop

When any stop condition fires:
- set `active = false`
- set `stopReason` to the explicit stop code or readable explanation
- set `stoppedAt`
- set `awaitingManualResume = true`

### 5. New authorization supersedes old

If a new explicit autopilot instruction replaces an active one:
- close the old one with `stopReason = superseded_by_new_user_goal`
- then initialize the new one

## Stop Conditions

Autopilot must stop immediately if any of these conditions occurs:

1. child result status is `blocked`
2. child result status is `needs_clarification`
3. validation fails
4. required output is missing
5. writes exceed approved boundaries
6. no meaningful progress is made across repeated loops
7. the authorized terminal goal is reached
8. the user sends a new substantive instruction

Hard rule:
- the parent must explicitly report why autopilot stopped
- it must not silently leave `autoPilot.active = false` without surfacing the reason

## User Message Interruption Rules

User replies during autopilot must be split into two classes.

### 1. Non-interrupting confirmations

These should not stop autopilot by themselves:
- `好`
- `收到`
- `继续`
- short acknowledgements that do not change requirements

### 2. Interrupting user input

These must stop autopilot immediately:
- a new requirement
- a correction
- a question about why the parent is doing something
- a stop or pause instruction
- a replacement autopilot target

Recommended stop reason codes:
- `user_interruption`
- `superseded_by_new_user_goal`

## Reporting Rules

### 1. Ordinary progress reporting

Autopilot must continue to report progress.

The parent may merge multiple same-loop progress changes into one message, following the existing chapter-progress merge rules.

Example:
- `第4章初稿待审核；第4章进入润色；第5章初稿中`

### 2. Stop reporting

Stop messages must never be merged away.

Whenever autopilot stops, the parent must emit a dedicated message that includes:
- autopilot has stopped
- the explicit reason
- the immediate next expected manual action when possible

Example:
- `自动流程已停止：第7章润色 blocked：人物口吻漂移。请人工处理后再决定是否重新开启自动流程。`

## Integration Points

### 1. State normalization

`revision_utils.py` and `load_project_state.py` should:
- add default `autoPilot` fields
- normalize old states that do not yet contain `autoPilot`

### 2. Gate approval control

The parent needs a dedicated helper, not scattered inline logic.

Recommended helpers:
- `start_auto_pilot(...)`
- `stop_auto_pilot(...)`
- `should_auto_approve_gate(state, gate)`
- `should_interrupt_auto_pilot_from_user_message(message, state)`

### 3. Status rendering

`novel_project_status.py --brief` should surface:
- whether autopilot is active
- current goal chapter
- latest autopilot progress summary
- whether autopilot stopped
- stop reason
- whether manual resume is required

Example:

```text
自动流程：已停止
自动目标：第10章结束
自动流程最近进度：第9章润色待审核；第10章初稿中
自动流程停止原因：已达到授权终点
```

### 4. Runtime loop placement

Autopilot should be checked by the parent immediately after:
- a gate becomes approvable
- a stop condition becomes known
- a user message arrives during an active autopilot session

The parent must never auto-approve before protocol validation and state persistence succeed.

## Invariants

- autopilot must never activate from ambiguous user phrasing
- autopilot must never directly author chapter output
- autopilot must never auto-run `final-review`
- autopilot must never hide stop reasons
- autopilot must never continue after a blocking or validation failure
- autopilot must never continue after a substantive user interruption
- autopilot must never overshoot the terminal chapter goal

## Testing Implications

At minimum the implementation should verify:

1. manual mode remains unchanged when autopilot is inactive
2. explicit authorized messages create `autoPilot`
3. vague approval messages do not create `autoPilot`
4. active autopilot can auto-approve scope and chapter-plan gates
5. drafting / polishing / proofreading still require subagent dispatch under autopilot
6. blocked child results stop autopilot and persist the stop reason
7. validation failures stop autopilot and persist the stop reason
8. reaching the goal chapter proofreading completion stops autopilot with `goal_reached`
9. pure acknowledgement messages do not interrupt autopilot
10. substantive user messages do interrupt autopilot
11. a new authorized goal supersedes the old one with persisted stop reason
12. `novel_project_status.py` surfaces autopilot state and stop reason clearly

## Open Design Choice Resolved By This Spec

This spec intentionally fixes these decisions:
- autopilot is opt-in, not default
- activation requires both explicit delegation intent and explicit terminal chapter
- terminal condition is `goal chapter proofreading completed`
- `final-review` stays manual
- pure acknowledgements do not interrupt autopilot
- stop reasons must be durable and user-visible
