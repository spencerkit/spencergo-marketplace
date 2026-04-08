# Isolated Dispatch Template

Use this template when the parent agent is about to dispatch `drafting`, `polishing`, or `proofreading`.

## 1. Parent-side invariants
- run `scripts/run_isolated_dispatch.py` to build, launch, and extract in one step
- the child session runs in a physically separate `claude -p` process
- the child session has zero parent chat history
- the child session cannot spawn grandchildren (`Agent` tool is disabled)
- the child session cannot persist its history (`--no-session-persistence`)
- the child receives only file-embedded context in the prompt
- do not modify project files after dispatch returns and before validation finishes
- if parent-side files changed or the session was interrupted, re-run the dispatch
- all dispatch artifacts stay outside project root

## 2. Running an isolated dispatch

Drafting example:

```bash
python3 skills/novel-studio/scripts/run_isolated_dispatch.py \
  "$PROJECT_ROOT" \
  drafting \
  --batch-range "第1章-第3章" \
  --target-file "manuscript/第1章_开端.md" \
  --target-file "manuscript/第2章_转折.md" \
  --target-file "manuscript/第3章_反转.md" \
  --model sonnet \
  --timeout 300 \
  --max-budget-usd 3
```

Polishing example:

```bash
python3 skills/novel-studio/scripts/run_isolated_dispatch.py \
  "$PROJECT_ROOT" \
  polishing \
  --batch-range "第1章-第3章" \
  --target-file "manuscript/第1章_开端.md" \
  --target-file "manuscript/第2章_转折.md" \
  --target-file "manuscript/第3章_反转.md" \
  --polishing-focus "压缩开篇废话，增强结尾钩子和人物口吻区分" \
  --model sonnet \
  --timeout 300
```

Proofreading example:

```bash
python3 skills/novel-studio/scripts/run_isolated_dispatch.py \
  "$PROJECT_ROOT" \
  proofreading \
  --batch-range "第1章-第3章" \
  --model sonnet \
  --timeout 300
```

## 3. Parent dispatch skeleton

```python
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent / 'scripts'

def run_isolated_dispatch(project, stage, **kwargs):
    cmd = [
        'python3', str(SCRIPTS / 'run_isolated_dispatch.py'),
        str(project),
        stage,
    ]
    for key, value in kwargs.items():
        if isinstance(value, list):
            for item in value:
                cmd.extend([f'--{key}', str(item)])
        elif value is not None:
            cmd.extend([f'--{key.replace("_", "-")}', str(value)])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f'dispatch failed: {result.stderr}')
    return json.loads(result.stdout)

# Example usage:
dispatch_result = run_isolated_dispatch(
    project_root,
    'drafting',
    batch_range='第1章-第3章',
    target_file=[
        'manuscript/第1章_开端.md',
        'manuscript/第2章_转折.md',
        'manuscript/第3章_反转.md',
    ],
    model='sonnet',
    timeout=300,
    max_budget_usd=3,
)
```

## 4. Child prompt (auto-generated)

`run_isolated_dispatch.py` builds the child prompt automatically. It embeds:
- all `requiredInputs` file contents (outline, chapter plan, style bible, etc.)
- stage-specific task instructions (drafting / polishing / proofreading rules)
- write boundary and must-not-modify constraints
- the required protocol JSON fields

The child sees **only** this prompt — no parent chat history, no discussion context.

## 5. Parent result handling skeleton

After `run_isolated_dispatch.py` returns:

```bash
# Validate the result
python3 skills/novel-studio/scripts/validate_stage_execution_result.py \
  "$PROJECT_ROOT" \
  --bundle-file /tmp/bundle.json \
  --result-file /tmp/result.json

# Apply the validated result
python3 skills/novel-studio/scripts/apply_stage_execution_result.py \
  "$PROJECT_ROOT" \
  --bundle-file /tmp/bundle.json \
  --result-file /tmp/result.json
```

Parent handling rules:
- if validation fails, stop and surface the failure
- if the child returns `blocked` or `needs_clarification`, require non-empty `blockedReasons`
- if the child returns `completed`, require empty `blockedReasons`
- if the child returns `completed`, require every `outputContract.mustWriteFiles` path to be touched by the dispatch
- if `proofreading` returns `completed`, require non-empty judgment fields; if judgment is `needs revision`, require non-empty blockers
- if `proofreading` returns `completed` with judgment `acceptable`, require empty blockers
- if `proofreading` returns `completed` with judgment `conditionally acceptable`, require empty blockers and non-empty risks
- do not hand-edit the child result just to make validation pass
- apply only validated results
- summarize the accepted result for the user only after validation and apply succeed

## 6. What makes this different from inline work

| Property | Inline (main agent writes directly) | Isolated dispatch |
|----------|-------------------------------------|-------------------|
| Chat history | Full parent context | Zero — new `claude -p` session |
| Self-review blindness | Author reviews own text | Separate session, independent review |
| Role contamination | Writing + criticizing in same context | Different prompts, different sessions |
| Can bypass | N/A — it IS the main agent | Cannot — `Agent` tool disabled, runs via script |

The main agent **physically cannot** skip the isolated session because:
1. `run_isolated_dispatch.py` is a Python script — it runs `claude -p` internally
2. The main agent calls the script, not spawns agents itself
3. The script returns the child's result, which the main agent can only validate/apply
