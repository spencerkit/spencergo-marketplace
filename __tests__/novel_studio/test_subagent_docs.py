import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'skills/novel-studio/SKILL.md'
README = ROOT / 'skills/novel-studio/README.md'
SUBAGENT_EXEC = ROOT / 'skills/novel-studio/references/subagent-execution.md'
SUBAGENT_TEMPLATE = ROOT / 'skills/novel-studio/references/subagent-dispatch-template.md'
SUBAGENT_DRAFTING = ROOT / 'skills/novel-studio/references/subagent-drafting.md'
SUBAGENT_POLISHING = ROOT / 'skills/novel-studio/references/subagent-polishing.md'
SUBAGENT_PROOFREADING = ROOT / 'skills/novel-studio/references/subagent-proofreading.md'
WORKFLOW = ROOT / 'skills/novel-studio/references/workflow.md'
DRAFTING_REF = ROOT / 'skills/novel-studio/references/drafting.md'
FILE_STRUCTURE = ROOT / 'skills/novel-studio/references/file-structure.md'
STAGE_MATRIX = ROOT / 'skills/novel-studio/references/stage-reference-matrix.md'
OPENING_DESIGN = ROOT / 'skills/novel-studio/references/opening-design.md'
STYLE_BIBLE = ROOT / 'skills/novel-studio/references/style-bible.md'
PLATFORM_PROFILES = ROOT / 'skills/novel-studio/references/platform-profiles.md'
ANTI_TEMPLATE = ROOT / 'skills/novel-studio/references/anti-template-checklist.md'
LEDGERS = ROOT / 'skills/novel-studio/references/continuity-ledgers.md'
TRACK_RULES_URBAN = ROOT / 'skills/novel-studio/references/track-guides/规则异变都市.md'
TRACK_FAMILY_XIANXIA = ROOT / 'skills/novel-studio/references/track-guides/家族势力成长修仙.md'
TRACK_MYSTERY_FANTASY = ROOT / 'skills/novel-studio/references/track-guides/高设定悬疑奇幻.md'


class NovelStudioSubagentDocsTest(unittest.TestCase):
    def read_required_doc(self, path: Path) -> str:
        self.assertTrue(
            path.exists(),
            f'Missing required doc: {path.relative_to(ROOT)}',
        )
        return path.read_text(encoding='utf-8')

    def test_skill_makes_three_stages_default_to_subagent_execution(self):
        text = self.read_required_doc(SKILL)
        self.assertIn('## Subagent execution defaults', text)
        self.assertIn(
            '- `drafting`, `polishing`, and `proofreading` default to subagent execution',
            text,
        )
        self.assertIn('- the parent agent is the orchestrator', text)
        self.assertIn('- assemble a curated execution package before delegation', text)
        self.assertIn('- delegate with `fork_context = false`', text)
        self.assertIn('- prefer `prepare_dispatch -> spawn(message=childPrompt) -> record_child_output -> finalize_dispatch` as the parent runtime loop', text)
        self.assertIn('- `scripts/subagent_dispatch_runtime.py` exposes `prepare_dispatch`, `record_child_output`, and `finalize_dispatch` for Python parents', text)
        self.assertIn('- `prepare_dispatch(...)` generates the child prompt plus parent-side dispatch artifacts', text)
        self.assertIn('- child agents still receive prompt text, not local artifact paths', text)
        self.assertIn('- `record_child_output(...)` stores raw child output parent-side only', text)
        self.assertIn('- `finalize_dispatch(...)` runs extract + validate + apply before state advancement', text)
        self.assertIn('- build the execution bundle with `scripts/build_stage_execution_package.py`', text)
        self.assertIn('- extract the child JSON result with `scripts/extract_stage_subagent_result.py`', text)
        self.assertIn('- validate child results with `scripts/validate_stage_execution_result.py`', text)
        self.assertIn('- apply accepted results with `scripts/apply_stage_execution_result.py`', text)
        self.assertIn(
            '- `references/subagent-dispatch-template.md` — concrete parent-agent dispatch skeleton, child prompt template, helper-based runtime loop, and validate/apply sequence',
            text,
        )
        self.assertIn(
            '- `references/opening-design.md` — opening-gate rules, first-3/10/20 chapter objectives, and opening approval standard',
            text,
        )
        self.assertIn(
            '- `references/style-bible.md` — style-lock contract, drift-control rules, and revision path for voice changes',
            text,
        )
        self.assertIn(
            '- `references/platform-profiles.md` — 起点 / 番茄 / 通用 platform modes and their structural implications',
            text,
        )
        self.assertIn(
            '- `references/anti-template-checklist.md` — anti-template checks for topic choice, opening quality, and chapter-level drift',
            text,
        )
        self.assertIn(
            '- `references/continuity-ledgers.md` — world rules, foreshadow, relationship, and resource ledgers for long-form stability',
            text,
        )
        self.assertIn(
            '- validate delegated outputs before advancing workflow state',
            text,
        )
        self.assertIn('- fail closed on protocol or content failure', text)
        self.assertIn('- no silent inline fallback for these stages', text)

    def test_readme_exposes_parent_orchestrated_subagent_flow(self):
        text = self.read_required_doc(README)
        self.assertIn('## Subagent 执行接入', text)
        self.assertIn('`drafting` / `polishing` / `proofreading` 默认走父 agent 编排 + subagent 执行', text)
        self.assertIn('开篇门是 drafting 之前的强制前置审批门', text)
        self.assertIn('`scripts/prepare_stage_subagent_dispatch.py`', text)
        self.assertIn('`scripts/extract_stage_subagent_result.py`', text)
        self.assertIn('`scripts/finalize_stage_subagent_dispatch.py`', text)
        self.assertIn('所有 `bundle` / `prompt` / `manifest` / `child-response` / `result` / `validated` 中间产物都必须放在项目根目录之外', text)
        self.assertIn('只把 `executionPackage` 发给子 agent', text)
        self.assertIn('`validationContext` 只留在父 agent', text)
        self.assertIn('`spawn_agent(..., fork_context=false)`', text)
        self.assertIn('`prepare -> spawn -> extract -> finalize`', text)
        self.assertIn('`prepare_stage_subagent_dispatch.py` 默认会写出 sidecar `manifest`', text)
        self.assertIn('`finalize_stage_subagent_dispatch.py` 可以用 `--manifest-file` 先校验 bundle sidecar', text)
        self.assertIn('`prepare_stage_subagent_dispatch.py` 支持 `--dispatch-dir` 生成标准化 dispatch workspace', text)
        self.assertIn('prepare 的返回结果会带 `dispatchDir`', text)
        self.assertIn('标准布局固定为 `bundle.json` / `prompt.txt` / `manifest.json` / `child-response.txt` / `result.json` / `validated.json`', text)
        self.assertIn('`rawFile` / `resultFile` / `validatedFile`', text)
        self.assertIn('如果你显式传了 `bundleFile` / `promptFile` / `manifestFile`，且三者位于同一个父目录，prepare 也会自动把这个目录当成 `dispatchDir`', text)
        self.assertIn('`extract_stage_subagent_result.py` 和 `finalize_stage_subagent_dispatch.py` 也支持直接吃 `--dispatch-dir`', text)
        self.assertIn('显式传入的 `rawFile` / `resultFile` / `bundleFile` / `manifestFile` / `validatedFile` 会覆盖 `dispatchDir` 默认路径', text)
        self.assertIn('如果父 agent 用 Python 编排，可以直接 import `scripts/subagent_dispatch_runtime.py`', text)
        self.assertIn('`prepare_dispatch(...)` 负责生成 `childPrompt`', text)
        self.assertIn('`record_child_output(...)` 只负责记录子 agent 的原始输出', text)
        self.assertIn('`finalize_dispatch(...)` 会串起 extract + validate + apply', text)
        self.assertIn('sidecar `manifest` 会同时记录 `bundle` 摘要，以及可选 `promptFile` / `promptSha256` 完整性信息', text)
        self.assertIn('`completed` 结果必须真实触达本次 dispatch 的全部 `outputContract.mustWriteFiles`', text)
        self.assertIn('`blocked` / `needs_clarification` 必须带非空 `blockedReasons`；`completed` 必须保持 `blockedReasons=[]`', text)
        self.assertIn('`proofreading` 的 `completed` 结果必须给出非空的 `continuity` / `logic` / `characterOOC` / `fixDirection`；若 judgment=`needs revision`，`blockers` 也必须非空', text)
        self.assertIn('`proofreading` 若 judgment=`acceptable`，`blockers` 必须为空', text)
        self.assertIn('`proofreading` 若 judgment=`conditionally acceptable`，`blockers` 必须为空且 `risks` 必须非空', text)

    def test_shared_protocol_reference_exists_and_defines_parent_and_child_contract(self):
        text = self.read_required_doc(SUBAGENT_EXEC)
        self.assertIn('## 1. Parent role', text)
        self.assertIn('- parent agent is the orchestrator', text)
        self.assertIn('- parent agent dispatches with `fork_context = false`', text)
        self.assertIn('## 2. Execution Package', text)
        self.assertIn(
            '- `task type` must be one of `drafting`, `polishing`, or `proofreading`',
            text,
        )
        self.assertIn(
            '- `required inputs` must be a structured named map, not freeform prose',
            text,
        )
        self.assertIn(
            '- every stage package must include non-empty `styleBible`, `mainlineSpec`, `platformProfile`, `trackGuide`, and `ledgerSnapshot`',
            text,
        )
        self.assertIn(
            '- `output contract` must state explicit required files and required return fields',
            text,
        )
        self.assertIn('## 3. Child Return Contract', text)
        self.assertIn('## 4. Failure Handling', text)
        self.assertIn('- fail closed', text)
        self.assertIn('- infrastructure failure: may retry once', text)
        self.assertIn('- protocol failure: reject result', text)
        self.assertIn('- content failure: do not advance', text)
        self.assertIn('- no silent inline fallback', text)
        self.assertIn('## 5. Parent Acceptance Duties', text)
        self.assertIn(
            '- compare the actual filesystem diff against `changedFiles` and `createdFiles` and reject mismatches',
            text,
        )
        self.assertIn(
            '- if `status` is `blocked` or `needs_clarification`, `changedFiles` and `createdFiles` must both be empty',
            text,
        )
        self.assertIn(
            '- `notesForNextStage` should be a short string or an empty string',
            text,
        )
        self.assertIn(
            '- `blockedReasons` and `risks` must be string lists',
            text,
        )
        self.assertIn(
            '- `blocked` and `needs_clarification` must include non-empty `blockedReasons`',
            text,
        )
        self.assertIn(
            '- `completed` must keep `blockedReasons` empty',
            text,
        )
        self.assertIn(
            '- if `status` is `completed`, every `outputContract.mustWriteFiles` entry must be touched by the current dispatch',
            text,
        )
        self.assertIn(
            '- `proofreading` completed results must include non-empty `continuity`, `logic`, `characterOOC`, and `fixDirection` strings',
            text,
        )
        self.assertIn(
            '- if `proofreading judgment` is `needs revision`, `blockers` must be non-empty',
            text,
        )
        self.assertIn(
            '- if `proofreading judgment` is `acceptable`, `blockers` must be empty',
            text,
        )
        self.assertIn(
            '- if `proofreading judgment` is `conditionally acceptable`, `blockers` must be empty and `risks` must be non-empty',
            text,
        )
        self.assertIn(
            'Do not persist runtime subagent ids, session ids, raw execution packages, or raw subagent conversation history.',
            text,
        )
        self.assertIn(
            '- `status` is the protocol execution state. Stage judgments such as `acceptable`, `conditionally acceptable`, and `needs revision` are separate stage-specific outputs.',
            text,
        )
        self.assertIn('## 6. Parent Runtime Loop', text)
        self.assertIn('1. run `scripts/build_stage_execution_package.py`', text)
        self.assertIn('2. send only `executionPackage` to the child', text)
        self.assertIn('3. keep `validationContext` parent-side only', text)
        self.assertIn('4. run `scripts/extract_stage_subagent_result.py` on the child raw response', text)
        self.assertIn('5. run `scripts/validate_stage_execution_result.py`', text)
        self.assertIn('6. run `scripts/apply_stage_execution_result.py` only after validation passes', text)
        self.assertIn('- keep `taskType`, `stage`, and `validationContext.stage` aligned for the same dispatch', text)
        self.assertIn('- build the bundle immediately before dispatch', text)
        self.assertIn('- do not modify project files after bundle build and before validation finishes', text)
        self.assertIn('- if `manifest.promptFile` and `manifest.promptSha256` are present, validate the prompt file contents before trusting the dispatch artifacts', text)
        self.assertIn('- verify completed results actually touched every required `outputContract.mustWriteFiles` path', text)
        self.assertIn(
            '- if parent-side files changed or the session was interrupted, discard the old bundle and rebuild a fresh one',
            text,
        )
        self.assertIn('- treat non-JSON child output as protocol failure before validation', text)
        self.assertIn('## 7. Child Prompt Contract', text)
        self.assertIn('- return one structured result only', text)
        self.assertIn('- do not echo the full execution package back', text)
        self.assertIn('- do not claim completion without populated protocol fields', text)
        self.assertIn('- if the package is insufficient, return `needs_clarification` with zero file writes', text)

    def test_parent_dispatch_template_exists_and_covers_spawn_validate_apply(self):
        text = self.read_required_doc(SUBAGENT_TEMPLATE)
        self.assertIn('## 1. Parent-side invariants', text)
        self.assertIn('- send only `executionPackage` to the child', text)
        self.assertIn('- keep `validationContext` parent-side only', text)
        self.assertIn('- delegate with `fork_context = false`', text)
        self.assertIn('- `scripts/prepare_stage_subagent_dispatch.py` prepares a reusable bundle file plus the child prompt', text)
        self.assertIn('- `scripts/prepare_stage_subagent_dispatch.py` can also emit a sidecar manifest for bundle integrity checks', text)
        self.assertIn('- `scripts/prepare_stage_subagent_dispatch.py` can return a standard dispatch workspace layout via `dispatchDir` plus raw/result/validated artifact paths', text)
        self.assertIn('- the standard `dispatchDir` layout is `bundle.json`, `prompt.txt`, `manifest.json`, `child-response.txt`, `result.json`, and `validated.json`', text)
        self.assertIn('- if explicit `bundleFile`, `promptFile`, and `manifestFile` share one parent directory, infer that parent as `dispatchDir` for the remaining artifacts', text)
        self.assertIn('- `scripts/extract_stage_subagent_result.py` turns the child raw response into exactly one JSON result object', text)
        self.assertIn('- `scripts/extract_stage_subagent_result.py` can read `rawFile` and write `resultFile` directly from `dispatchDir`', text)
        self.assertIn('- `scripts/finalize_stage_subagent_dispatch.py` validates the child result and applies accepted state updates', text)
        self.assertIn('- `scripts/finalize_stage_subagent_dispatch.py` can read `bundleFile` / `manifestFile` / `resultFile` and write `validatedFile` directly from `dispatchDir`', text)
        self.assertIn('- `scripts/subagent_dispatch_runtime.py` exposes `prepare_dispatch`, `record_child_output`, and `finalize_dispatch` for Python parents', text)
        self.assertIn('- all dispatch artifacts must stay outside project root', text)
        self.assertIn(
            '- do not add hidden requirements outside `requiredInputs`; if context is missing, fix the bundle builder or rebuild the package',
            text,
        )
        self.assertIn('## 2. Build the execution bundle', text)
        self.assertIn('build_stage_execution_package.py', text)
        self.assertIn('--dispatch-dir "$TMP_DIR"', text)
        self.assertIn('## 3. Parent dispatch skeleton', text)
        self.assertIn('spawn_agent(', text)
        self.assertIn('fork_context=False', text)
        self.assertIn('Return exactly one JSON object and nothing else.', text)
        self.assertIn('## 4. Child prompt template', text)
        self.assertIn(
            '- proofreading: read-only only; do not modify any project file; include judgment, continuity, logic, characterOOC, blockers, and fixDirection',
            text,
        )
        self.assertIn('## 5. Parent result handling skeleton', text)
        self.assertIn('extract_stage_subagent_result.py', text)
        self.assertIn('finalize_stage_subagent_dispatch.py', text)
        self.assertIn('--dispatch-dir "$TMP_DIR"', text)
        self.assertIn('If you need to deviate from the standard layout, pass explicit file arguments and let them override the `dispatchDir` defaults.', text)
        self.assertIn(
            '- if the child returns prose, multiple JSON blocks, or malformed JSON, treat it as protocol failure',
            text,
        )
        self.assertIn('- if the child returns `blocked` or `needs_clarification`, require non-empty `blockedReasons`', text)
        self.assertIn('- if the child returns `completed`, require empty `blockedReasons`', text)
        self.assertIn('- if the child returns `completed`, require every `outputContract.mustWriteFiles` path to be touched by the dispatch', text)
        self.assertIn('- if `proofreading` returns `completed`, require non-empty judgment fields; if judgment is `needs revision`, require non-empty blockers', text)
        self.assertIn('- if `proofreading` returns `completed` with judgment `acceptable`, require empty blockers', text)
        self.assertIn('- if `proofreading` returns `completed` with judgment `conditionally acceptable`, require empty blockers and non-empty risks', text)
        self.assertIn('## 6. End-to-End Parent Example', text)
        self.assertIn('from subagent_dispatch_runtime import finalize_dispatch, prepare_dispatch, record_child_output', text)
        self.assertIn('payload = prepare_dispatch(', text)
        self.assertIn('message=payload["childPrompt"]', text)
        self.assertIn('record_child_output(', text)
        self.assertIn('applied = finalize_dispatch(', text)
        self.assertIn('child_done = wait_agent(ids=[child.id], timeout_ms=180000)', text)
        self.assertIn('dispatch_dir = Path(payload["dispatchDir"])', text)
        self.assertIn('record_child_output(project_root, child_done["final_message"], dispatch_dir=dispatch_dir)', text)
        self.assertIn('- if `wait_agent` times out or returns no usable final message, treat it as infrastructure failure and retry at most once', text)

    def test_drafting_reference_defines_required_boundaries(self):
        text = self.read_required_doc(SUBAGENT_DRAFTING)
        self.assertIn('## Default Mode', text)
        self.assertIn('- drafting must use a drafting subagent by default', text)
        self.assertIn('- one subagent handles the approved current batch', text)
        self.assertIn('- parent runtime should prefer `prepare_dispatch -> spawn(message=childPrompt) -> record_child_output -> finalize_dispatch`', text)
        self.assertIn('- parent dispatch still uses `fork_context = false`', text)
        self.assertIn('- child receives prompt text only; dispatch artifacts stay parent-side', text)
        self.assertIn('## Allowed Writes', text)
        self.assertIn('- only parent-approved target manuscript files', text)
        self.assertIn('## Overwrite Rule', text)
        self.assertIn(
            '- existing target files stay read-only unless parent sets `overwrite=true`',
            text,
        )
        self.assertIn('- current stage is drafting', text)
        self.assertIn('- no open approval gate blocks execution', text)
        self.assertIn('- opening gate is explicitly approved before batch drafting starts', text)

    def test_polishing_reference_defines_required_boundaries(self):
        text = self.read_required_doc(SUBAGENT_POLISHING)
        self.assertIn('## Default Mode', text)
        self.assertIn('- polishing must use a polishing subagent by default', text)
        self.assertIn('- parent runtime should prefer `prepare_dispatch -> spawn(message=childPrompt) -> record_child_output -> finalize_dispatch`', text)
        self.assertIn('- parent dispatch still uses `fork_context = false`', text)
        self.assertIn('- child receives prompt text only; dispatch artifacts stay parent-side', text)
        self.assertIn('## Required Input', text)
        self.assertIn('- every execution package must include `polishingFocus`', text)
        self.assertIn('## Allowed Writes', text)
        self.assertIn(
            '- must not silently change upstream planning assumptions',
            text,
        )
        self.assertIn('- current stage is polishing', text)
        self.assertIn('- substantive editorial review exists', text)
        self.assertIn('- explicit optimization suggestions exist', text)

    def test_proofreading_reference_defines_required_boundaries(self):
        text = self.read_required_doc(SUBAGENT_PROOFREADING)
        self.assertIn('## Default Mode', text)
        self.assertIn('- proofreading must use a proofreading subagent by default', text)
        self.assertIn('- parent runtime should prefer `prepare_dispatch -> spawn(message=childPrompt) -> record_child_output -> finalize_dispatch`', text)
        self.assertIn('- parent dispatch still uses `fork_context = false`', text)
        self.assertIn('- child receives prompt text only; dispatch artifacts stay parent-side', text)
        self.assertIn('## Read-Only Rule', text)
        self.assertIn('- this role is read-only', text)
        self.assertIn('- must not modify manuscript files', text)
        self.assertIn('- must not modify any project file', text)
        self.assertIn('- execution package must set `target files` to an empty list', text)
        self.assertIn(
            '- execution package must set `must-not-modify list` to an explicit project-root-relative path list that covers the entire project',
            text,
        )
        self.assertIn('- this subagent is a batch gate, not a silent fixer', text)
        self.assertIn('- current stage is proofreading', text)
        self.assertIn('## Required Judgment', text)
        self.assertIn('- acceptable', text)
        self.assertIn('- conditionally acceptable', text)
        self.assertIn('- needs revision', text)
        self.assertIn('- completed proofreading results must keep protocol `blockedReasons` empty', text)
        self.assertIn('- if judgment is `needs revision`, blockers must be non-empty', text)
        self.assertIn('- if judgment is `acceptable`, blockers must be empty', text)
        self.assertIn('- if judgment is `conditionally acceptable`, blockers must be empty and risks must be non-empty', text)
        self.assertIn('- continuity / logic / character-OOC / fix direction must be explicit non-empty strings', text)

    def test_existing_drafting_reference_preserves_subagent_write_boundary(self):
        text = self.read_required_doc(DRAFTING_REF)
        self.assertIn(
            'Do not start batch drafting until the opening gate has been explicitly approved.',
            text,
        )
        self.assertIn(
            'The drafting subagent should modify only the target manuscript files for the approved chapter range.',
            text,
        )
        self.assertIn(
            'Do not modify planning, recap, review, or state artifacts during drafting execution.',
            text,
        )
        self.assertIn(
            '- overwrite an existing target manuscript file only when the parent has explicitly granted overwrite permission for that dispatch',
            text,
        )
        self.assertIn(
            'Preferred parent runtime loop: `prepare_dispatch -> spawn(message=childPrompt) -> record_child_output -> finalize_dispatch`.',
            text,
        )
        self.assertIn(
            'Use `scripts/subagent_dispatch_runtime.py` when the parent is coordinating drafting in Python.',
            text,
        )

    def test_workflow_preserves_subagent_stage_gates(self):
        text = self.read_required_doc(WORKFLOW)
        self.assertIn(
            'Default parent runtime loop: `prepare_dispatch -> spawn(message=childPrompt) -> record_child_output -> finalize_dispatch`.',
            text,
        )
        self.assertIn(
            'The parent still sends only `childPrompt` to the child subagent and keeps dispatch artifacts parent-side.',
            text,
        )
        self.assertIn(
            'The drafting subagent must not be dispatched until the chapter-plan package for the target batch exists and is explicitly approved.',
            text,
        )
        self.assertIn(
            'Before the first batch of prose drafting, the project must pass the opening gate with an approved `04A_开篇设计.md`.',
            text,
        )
        self.assertIn(
            '- the target batch cannot yet be turned into a usable chapter-plan package',
            text,
        )
        self.assertIn('- a substantive editorial review', text)
        self.assertIn('- explicit optimization suggestions', text)
        self.assertIn('- the review is vague or empty', text)
        self.assertIn('- scene-tone mismatch remains unresolved', text)
        self.assertIn('- obvious outline/style mismatch remains unresolved', text)
        self.assertIn('- continuity check result', text)
        self.assertIn(
            '- the report clearly states whether the batch is acceptable, conditionally acceptable, or needs revision',
            text,
        )
        self.assertIn('- the batch no longer matches the approved chapter plan', text)
        self.assertIn(
            '- the batch drifts from the outline or intended style in a major way',
            text,
        )

    def test_polishing_reference_mentions_helper_runtime_loop(self):
        text = self.read_required_doc(ROOT / 'skills/novel-studio/references/polishing.md')
        self.assertIn(
            'Preferred parent runtime loop: `prepare_dispatch -> spawn(message=childPrompt) -> record_child_output -> finalize_dispatch`.',
            text,
        )
        self.assertIn(
            'Use `scripts/subagent_dispatch_runtime.py` when the parent is coordinating polishing in Python.',
            text,
        )

    def test_proofreading_reference_mentions_helper_runtime_loop(self):
        text = self.read_required_doc(ROOT / 'skills/novel-studio/references/proofreading.md')
        self.assertIn(
            'Preferred parent runtime loop: `prepare_dispatch -> spawn(message=childPrompt) -> record_child_output -> finalize_dispatch`.',
            text,
        )
        self.assertIn(
            'The child still receives prompt text only; proofreading dispatch artifacts stay parent-side.',
            text,
        )

    def test_file_structure_covers_discovery_and_batch_artifacts(self):
        text = self.read_required_doc(FILE_STRUCTURE)
        self.assertIn('00A_热点扫描.md', text)
        self.assertIn('00B_用户偏好.md', text)
        self.assertIn('00C_底盘与切口决策.md', text)
        self.assertIn('01A_风格圣经.md', text)
        self.assertIn('01B_总主线与卷级推进.md', text)
        self.assertIn('04A_开篇设计.md', text)
        self.assertIn('05_前情回顾.md', text)
        self.assertIn('05_本轮章节规划.md', text)
        self.assertIn('05B_世界规则账本.md', text)
        self.assertIn('05C_伏笔回收台账.md', text)
        self.assertIn('05D_关系状态表.md', text)
        self.assertIn('05E_能力与资源变化表.md', text)
        self.assertIn('### 4.1 `00A_热点扫描.md`', text)
        self.assertIn('### 4.2 `00B_用户偏好.md`', text)
        self.assertIn('### 4.3 `00C_底盘与切口决策.md`', text)
        self.assertIn('### 4.5 `01A_风格圣经.md`', text)
        self.assertIn('### 4.6 `01B_总主线与卷级推进.md`', text)
        self.assertIn('### 4.8 `05_前情回顾.md`', text)
        self.assertIn('### 4.9 `05_本轮章节规划.md`', text)
        self.assertIn('- create before drafting prose generation begins for the current batch', text)
        self.assertIn('- populate `05_本轮章节规划.md`', text)

    def test_stage_matrix_keeps_proofreading_as_read_only_gate(self):
        text = self.read_required_doc(STAGE_MATRIX)
        self.assertIn('校对结论、修订建议、明确 judgment', text)
        self.assertNotIn('修订后的 `manuscript/*.md`', text)

    def test_new_strategy_and_opening_references_exist(self):
        opening = self.read_required_doc(OPENING_DESIGN)
        self.assertIn('Opening Gate', opening)
        self.assertIn('前三章', opening)
        self.assertIn('前十章', opening)
        self.assertIn('前二十章', opening)

        style = self.read_required_doc(STYLE_BIBLE)
        self.assertIn('风格漂移', style)
        self.assertIn('V1', style)
        self.assertIn('风格修订单', style)

        platform = self.read_required_doc(PLATFORM_PROFILES)
        self.assertIn('起点模式', platform)
        self.assertIn('番茄模式', platform)
        self.assertIn('通用模式', platform)

        anti_template = self.read_required_doc(ANTI_TEMPLATE)
        self.assertIn('只有题材名', anti_template)
        self.assertIn('替换角色名后仍成立', anti_template)

        ledgers = self.read_required_doc(LEDGERS)
        self.assertIn('世界规则账本', ledgers)
        self.assertIn('伏笔回收台账', ledgers)
        self.assertIn('关系状态表', ledgers)
        self.assertIn('能力与资源变化表', ledgers)

    def test_track_guide_references_cover_three_priority_lanes(self):
        urban = self.read_required_doc(TRACK_RULES_URBAN)
        self.assertIn('规则异变都市', urban)
        self.assertIn('最稳发动机', urban)
        self.assertIn('最常见死法', urban)

        family = self.read_required_doc(TRACK_FAMILY_XIANXIA)
        self.assertIn('家族势力成长修仙', family)
        self.assertIn('势力经营', family)

        mystery = self.read_required_doc(TRACK_MYSTERY_FANTASY)
        self.assertIn('高设定悬疑奇幻', mystery)
        self.assertIn('认知博弈', mystery)

    def test_docs_define_supervisor_persistence_and_proofreading_report(self):
        skill = self.read_required_doc(SKILL)
        self.assertIn(
            'the parent agent owns workflow control, user communication, approval interpretation, persistence decisions, and subagent dispatch',
            skill,
        )
        self.assertIn('only explicit brainstorming mode may write to `staging/`', skill)

        workflow = self.read_required_doc(WORKFLOW)
        self.assertIn(
            'the moment a canonical file is written or refreshed, the workflow enters a stage-specific approval gate',
            workflow,
        )
        self.assertIn('`awaiting_user_approval`', workflow)

        file_structure = self.read_required_doc(FILE_STRUCTURE)
        self.assertIn('05A_本轮校对报告.md', file_structure)
        self.assertIn('staging/', file_structure)

        proofreading = self.read_required_doc(ROOT / 'skills/novel-studio/references/proofreading.md')
        self.assertIn('05A_本轮校对报告.md', proofreading)
        self.assertIn('Proofreading is diagnostic. Do not do silent fixing during proofreading.', proofreading)

        state_management = self.read_required_doc(ROOT / 'skills/novel-studio/references/state-management.md')
        self.assertIn('pendingArtifactPaths', state_management)
        self.assertIn('lastPersistedStage', state_management)
        self.assertIn('brainstormActive', state_management)
        self.assertIn('activeBranches', state_management)

    def test_docs_define_chapter_progress_reporting_contract(self):
        skill = self.read_required_doc(SKILL)
        self.assertIn('chapter progress becomes an explicit part of `.novel-state.json`', skill)
        self.assertIn('report chapter progress from state transitions rather than chat memory', skill)

        readme = self.read_required_doc(README)
        self.assertIn('第1章初稿中', readme)
        self.assertIn('chapter_progress_report.py', readme)

        state_management = self.read_required_doc(ROOT / 'skills/novel-studio/references/state-management.md')
        self.assertIn('chapterTasks', state_management)
        self.assertIn('pendingProgressItems', state_management)

        subagent_execution = self.read_required_doc(ROOT / 'skills/novel-studio/references/subagent-execution.md')
        self.assertIn('chapterLabels', subagent_execution)
        self.assertIn('lightweight progress events', subagent_execution)

    def test_state_management_doc_uses_project_local_state_file_path(self):
        state_management = self.read_required_doc(ROOT / 'skills/novel-studio/references/state-management.md')
        self.assertIn('Use a project-local state file:', state_management)
        self.assertIn('`.novel-state.json`', state_management)
        self.assertNotIn('/root/.openclaw/novels/[小说名称]/.novel-state.json', state_management)

    def test_docs_define_autopilot_activation_and_manual_boundaries(self):
        skill = self.read_required_doc(SKILL)
        self.assertIn('## Autopilot approval defaults', skill)
        self.assertIn('- default remains manual approval at every gate', skill)
        self.assertIn('- autopilot activates only after explicit bounded user authorization with a terminal chapter goal such as `继续到第10章结束`', skill)
        self.assertIn('- vague approval like `继续` or `好` does not activate autopilot', skill)
        self.assertIn('- autopilot does not change ownership: the parent remains the orchestrator, while `drafting`, `polishing`, and `proofreading` still belong to their subagents', skill)
        self.assertIn('- final review and final delivery remain manual; never auto-approve `waiting_final_review_feedback`', skill)

        readme = self.read_required_doc(README)
        self.assertIn('### Autopilot 自动推进', readme)
        self.assertIn('默认仍是手动审批。没有明确授权时，所有审批门继续人工确认。', readme)
        self.assertIn('只有用户给出显式、带终点章节的授权才会开启 autopilot，例如 `后续你来主控，继续到第10章结束`。单独一句 `继续` 不算。', readme)
        self.assertIn('`advance_autopilot.py` 每次只前进一步：补 `scopeConfirmed`、在 `05_本轮章节规划.md` 可安全解析时批准 `chapterPlanApproved` 并重建 `chapterTasks`、或代批 `waiting_draft_feedback` / `waiting_polishing_feedback` / `waiting_proofreading_feedback`。', readme)
        self.assertIn('目标章节达到经批准的 proofreading 完成状态', readme)
        self.assertIn('`waiting_final_review_feedback` 永远不自动批准；最终审校和最终交付仍是人工决定。', readme)

        workflow = self.read_required_doc(WORKFLOW)
        self.assertIn('### 2.5 Autopilot overlay', workflow)
        self.assertIn('- `scripts/advance_autopilot.py` advances at most one safe step per call', workflow)
        self.assertIn('- one-step advancement is limited to confirming `batch.scopeConfirmed`, safely approving `batch.chapterPlanApproved` from a parseable `05_本轮章节规划.md`, or approving an eligible open review gate', workflow)
        self.assertIn('- eligible auto-approvable review gates are only `waiting_draft_feedback`, `waiting_polishing_feedback`, and `waiting_proofreading_feedback`', workflow)
        self.assertIn('- when the goal chapter reaches approved proofreading completion, halt autopilot with stop reason `goal_reached`', workflow)
        self.assertIn('- never auto-approve `waiting_final_review_feedback`; `advance_autopilot.py` returns `final_review_manual` and final review stays manual', workflow)
        self.assertIn('Autopilot must not approve this gate. Final review and final delivery remain manual.', workflow)

    def test_docs_define_autopilot_state_progress_and_stop_contract(self):
        readme = self.read_required_doc(README)
        self.assertIn('**自动推进状态**：`autoPilot` 是否开启、终点章节、最近进度、停止原因', readme)
        self.assertIn('自动推进期间仍持续汇报章节进度；不会因为进入 autopilot 就停止 `chapterTasks` / `pendingProgressItems` 的更新和对外汇报。', readme)

        state_management = self.read_required_doc(ROOT / 'skills/novel-studio/references/state-management.md')
        self.assertIn('- autopilot goal / latest progress / stop reason state when bounded automation is active', state_management)
        self.assertIn('- autopilot activation, supersede, progress update, and explicit stop events', state_management)
        self.assertIn('## 9. Autopilot-state tracking', state_management)
        self.assertIn('- the normalized terminal goal chapter under `goalChapter`', state_management)
        self.assertIn('- the latest merged progress timestamp and summary under `lastProgressAt` / `lastProgressSummary`', state_management)
        self.assertIn('- the explicit stop reason under `stopReason`', state_management)
        self.assertIn('- stop reasons must stay explicit, for example `blocked: 人物口吻漂移`, `user_interruption`, or `goal_reached`', state_management)
        self.assertIn('- if the user replaces the bounded goal, record `superseded_by_new_user_goal` for the old run before starting the new one', state_management)

        state_fields = self.read_required_doc(ROOT / 'skills/novel-studio/references/state-fields-template.md')
        self.assertIn('"autoPilot": {', state_fields)
        self.assertIn('"goalChapter": "第10章"', state_fields)
        self.assertIn('"goalCondition": "proofreading_completed"', state_fields)
        self.assertIn('"lastProgressSummary": "第3章润色中"', state_fields)
        self.assertIn('"stopReason": null', state_fields)
        self.assertIn('"currentStage": "polishing"', state_fields)
        self.assertIn('"nextStage": "proofreading"', state_fields)
        self.assertIn('"polishingComplete": true', state_fields)
        self.assertIn('"phaseStatus": "awaiting_user_review"', state_fields)
        self.assertIn('"lastSummary": "第1章润色待审核"', state_fields)
        self.assertIn('"pendingProgressItems": []', state_fields)
        self.assertIn('"currentGate": "waiting_polishing_feedback"', state_fields)
        self.assertIn('Autopilot notes:', state_fields)
        self.assertIn('- `stopReason` stays `null` while automation is active; when stopped, record explicit values such as `blocked: 人物口吻漂移`, `user_interruption`, or `goal_reached`.', state_fields)

        subagent_execution = self.read_required_doc(ROOT / 'skills/novel-studio/references/subagent-execution.md')
        self.assertIn('Autopilot does not change this ownership model:', subagent_execution)
        self.assertIn('- `drafting`, `polishing`, and `proofreading` still belong to their subagents even when autopilot is active', subagent_execution)
        self.assertIn('- keep surfacing merged chapter progress during automation from file-backed state', subagent_execution)
        self.assertIn('- if a child returns `blocked` or `needs_clarification`, stop autopilot with an explicit reason and wait for manual resume', subagent_execution)
