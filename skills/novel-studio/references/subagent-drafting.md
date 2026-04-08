# Isolated Dispatch Drafting

## Default Mode
- drafting must use isolated dispatch by default
- one isolated `claude -p` session handles the approved current batch
- parent runs `scripts/run_isolated_dispatch.py` to build, launch, and extract
- the child session has zero parent chat history
- the child session cannot spawn grandchildren (`Agent` tool is disabled)
- the child receives prompt text with embedded file contents only; dispatch artifacts stay parent-side

## Allowed Writes
- only parent-approved target manuscript files
- target files must be non-empty and stay under `manuscript/`
- `must-not-modify list` must exactly equal the baseline snapshot minus `target files`
- no planning, recap, review, or state writes

## Overwrite Rule
- existing target files stay read-only unless parent sets `overwrite=true`
- fail closed when overwrite permission is missing or ambiguous
- this template assumes `overwrite=true` reflects an explicit parent-approved dispatch decision for the current target files

## Parent Preconditions
- current stage is drafting
- opening gate is explicitly approved before batch drafting starts
- chapter plan exists
- chapter plan is approved
- outline usable
- character package usable
- batch scope explicit
- no open approval gate blocks execution

## Acceptance Checklist
- only allowed files changed
- required files exist and are non-empty
- forbidden files untouched
- batch matches approved range
- return summary usable
