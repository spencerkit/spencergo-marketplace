# State Management

## 1. Goal

Preserve project workflow state across interruption, restart, and long production cycles.

Novel work is long-running. The workflow must not depend only on short-term chat context.

---

## 2. State file location

Use a project-local state file:

`/root/.openclaw/novels/[小说名称]/.novel-state.json`

This file is the primary structured workflow memory for the current project.

---

## 3. Required state responsibilities

The state system must record at least:
- current stage
- current substage when relevant
- last completed stage
- next intended stage
- approval status for each stage
- blocking issues
- artifact existence status
- working title / final title state
- current batch state when drafting has begun
- last update time

---

## 4. Read-before-work rule

Before starting any stage:
- load `.novel-state.json` if it exists
- determine the current stage, blockers, and next valid action from the state file
- do not infer workflow position only from vague chat memory if structured state exists

When the user asks for project status, current progress, blockers, approval state, current batch state, or next-step guidance, use `scripts/novel_project_status.py` as the default status-summary tool.

---

## 5. Write-after-stage rule

After each stage-level event, update the state file.

This includes:
- stage start
- stage completion
- user approval
- user rejection / revision request
- blocking issue creation
- rollback to an earlier stage
- final delivery
- Feishu sync completion if relevant

---

## 6. Discovery-state tracking

By the end of Discovery stage, state should reflect whether these artifacts exist:
- `00A_热点扫描.md`
- `00B_用户偏好.md`
- `00_选题报告.md`

It should also record whether:
- title is confirmed
- working title is approved
- discovery stage is approved for advancement

---

## 7. Batch-writing state tracking

Once drafting begins, state must also track the current batch.

At minimum it should record:
- current batch chapter range
- current batch chapter count
- whether batch scope is confirmed
- whether chapter-plan package exists
- whether chapter-plan package is approved
- whether draft writing is complete
- whether polishing is complete
- whether proofreading / batch final pass is complete
- whether recap has been updated
- whether the workflow is currently waiting for user decision on the next batch
- current batch focus
- current batch attraction points
- current batch climax target

---

## 8. Approval tracking

State should distinguish between:
- artifact exists
- artifact approved

These are not the same.

Examples:
- `outlineDoc: true` does not mean `outlineApproved: true`
- `topicReport: true` does not mean `discoveryApproved: true`
- `chapterPlanExists: true` does not mean `chapterPlanApproved: true`

State should also record the current review gate and the latest meaningful user feedback summary.
This makes interruption recovery much safer than relying only on boolean flags.

---

## 9. Blocking issue tracking

Blocking issues must be recorded explicitly.

Examples:
- title not confirmed
- outline has unresolved objections
- protagonist definition still unstable
- proofreading found unresolved blocker
- user asked for revision before advancement
- current batch chapter-plan not yet approved
- current batch is waiting for user decision whether to continue

Do not silently ignore blockers.

---

## 10. Fallback recovery rule

If `.novel-state.json` is missing:
- recover a provisional state from file structure and existing artifacts
- clearly mark that the state is reconstructed
- write the reconstructed state back to `.novel-state.json`

Do not rely on memory-only recovery when a structured state file can be rebuilt.

---

## 12. Required state quality

A usable state file should make it possible to answer:
- where is the project now
- what stage was last completed
- what has already been approved
- what is blocked
- what should happen next
- what batch is currently active
- whether the current batch is waiting for user approval or next-batch decision

If the state file cannot answer those, it is incomplete.
uld make it possible to answer:
- where is the project now
- what stage was last completed
- what has already been approved
- what is blocked
- what should happen next
- what batch is currently active
- whether the current batch is waiting for user approval or next-batch decision

If the state file cannot answer those, it is incomplete.
