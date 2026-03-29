# Novel Studio Cliche Exhaustion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first shippable `Cliche Exhaustion Loop` to `novel-studio`, including protocol docs, minimal state support, `staging/` branch scaffolding, and lightweight proofreading-time cliché-risk reporting.

**Architecture:** Keep the current supervisor-first workflow intact and layer the new behavior onto existing docs, state normalization, and branch-management utilities instead of inventing a second control system. Phase the implementation so deterministic docs/state/branch behavior lands first, then add a lightweight parent-side cliché-risk checker that records findings under `narrativeIntelligence.styleRisk.*` and surfaces them in status output.

**Tech Stack:** Python 3, `unittest`, existing `skills/novel-studio/scripts/*.py` CLI scripts, Markdown reference docs, `.novel-state.json`

---

## Planned File Map

**Create**
- `skills/novel-studio/references/cliche-exhaustion.md` — formal quick/deep anti-cliche protocol and `staging/` artifact contract

**Modify**
- `skills/novel-studio/SKILL.md` — skill-level operating contract for `Cliche Exhaustion Loop`
- `skills/novel-studio/README.md` — operator-facing overview of the new ideation mode
- `skills/novel-studio/references/workflow.md` — stage integration and planning gate rules
- `skills/novel-studio/references/outlining.md` — planning-stage hard gate requirements
- `skills/novel-studio/references/market-research.md` — Discovery quick-loop usage
- `skills/novel-studio/references/topic-report-template.md` — topic report sections for cliché rejection / retained novelty
- `skills/novel-studio/references/opening-design.md` — opening兑现 checks for retained novelty axes
- `skills/novel-studio/references/anti-template-checklist.md` — explicit anti-cliche pressure-test prompts
- `skills/novel-studio/references/proofreading.md` — lightweight backslide check expectations
- `skills/novel-studio/references/state-management.md` — new supervisor and style-risk state fields
- `skills/novel-studio/references/state-fields-template.md` — examples for `brainstorm*` and `styleRisk.*`
- `skills/novel-studio/references/file-structure.md` — `staging/` cliche-exhaustion branch layout
- `skills/novel-studio/scripts/revision_utils.py` — add review/style-risk defaults and normalization
- `skills/novel-studio/scripts/load_project_state.py` — normalize / reconstruct new fields
- `skills/novel-studio/scripts/novel_project_status.py` — show brainstorm-mode and cliché-risk summaries
- `skills/novel-studio/scripts/manage_stage_branches.py` — scaffold cliche-exhaustion branches, parse retained conclusions, and prune stale branches
- `skills/novel-studio/scripts/narrative_checker.py` — add lightweight cliché-risk collection helpers
- `skills/novel-studio/scripts/update_narrative_intelligence.py` — refresh cliché-risk findings on proofreading
- `skills/novel-studio/scripts/apply_stage_execution_result.py` — refresh cliché-risk findings after accepted proofreading results
- `__tests__/novel_studio/test_subagent_docs.py` — docs assertions
- `__tests__/novel_studio/test_supervisor_persistence.py` — state/status/branch scaffolding coverage
- `__tests__/novel_studio/test_narrative_intelligence_review.py` — cliché-risk runtime coverage

**Scope Cut**
- Do not add semantic or model-based cliché scoring.
- Do not create a new top-level runtime subsystem outside existing state / branch-management utilities.
- Do not let subagents write `.novel-state.json` or `staging/` control metadata.
- Do not add heavyweight final-review blocker folding for cliché findings in this slice; only status-visible risk reporting is required.

### Task 1: Add Cliche Exhaustion Protocol Docs

**Files:**
- Create: `skills/novel-studio/references/cliche-exhaustion.md`
- Modify: `skills/novel-studio/SKILL.md`
- Modify: `skills/novel-studio/README.md`
- Modify: `skills/novel-studio/references/workflow.md`
- Modify: `skills/novel-studio/references/outlining.md`
- Modify: `skills/novel-studio/references/market-research.md`
- Modify: `skills/novel-studio/references/topic-report-template.md`
- Modify: `skills/novel-studio/references/opening-design.md`
- Modify: `skills/novel-studio/references/anti-template-checklist.md`
- Modify: `skills/novel-studio/references/proofreading.md`
- Modify: `skills/novel-studio/references/state-management.md`
- Modify: `skills/novel-studio/references/state-fields-template.md`
- Modify: `skills/novel-studio/references/file-structure.md`
- Test: `__tests__/novel_studio/test_subagent_docs.py`

- [ ] **Step 1: Write the failing docs assertions**

```python
def test_docs_define_cliche_exhaustion_reference_and_workflow_hooks(self):
    skill = self.read_required_doc(SKILL)
    workflow = self.read_required_doc(WORKFLOW)
    outlining = self.read_required_doc(ROOT / 'skills/novel-studio/references/outlining.md')
    cliche = self.read_required_doc(ROOT / 'skills/novel-studio/references/cliche-exhaustion.md')

    self.assertIn('Cliche Exhaustion Loop', skill)
    self.assertIn('`Discovery` uses `quick`', cliche)
    self.assertIn('`Story Planning` uses `deep`', cliche)
    self.assertIn('planning approval should not occur until the retained direction has', workflow)
    self.assertIn('cliché samples were enumerated', outlining)


def test_file_structure_mentions_cliche_exhaustion_branch_artifacts(self):
    file_structure = self.read_required_doc(FILE_STRUCTURE)
    self.assertIn('00_脑暴任务卡.md', file_structure)
    self.assertIn('01_直觉俗套清单.md', file_structure)
    self.assertIn('05_定稿结论.md', file_structure)
```

- [ ] **Step 2: Run the docs test to verify failure**

Run:

```bash
python3 -m unittest __tests__.novel_studio.test_subagent_docs
```

Expected:
- FAIL because `references/cliche-exhaustion.md` does not exist yet
- FAIL because workflow / outlining / file-structure docs do not mention the new protocol

- [ ] **Step 3: Add the protocol reference and wire docs to it**

```markdown
<!-- skills/novel-studio/references/cliche-exhaustion.md -->
# Cliche Exhaustion

## Goal

Treat the first obvious story answers as suspicious by default.

## Modes

- `quick`: 3-round loop for Discovery and early direction work
- `deep`: 5-step loop for formal Story Planning before approval

## Required `staging/` branch files

- `00_脑暴任务卡.md`
- `01_直觉俗套清单.md`
- `02_反驳与否认.md`
- `03_变异候选.md`
- `04_保留候选.md`
- `05_定稿结论.md`

## Hard rule

Only `05_定稿结论.md` may authorize canonical backfill.
```

```markdown
<!-- skills/novel-studio/references/outlining.md -->
### Hard anti-cliche planning gate

Do not approve formal planning until the retained direction has:
- cliché samples enumerated
- rejection reasons recorded
- first-10-chapter continuation logic explained
```

```markdown
<!-- skills/novel-studio/references/file-structure.md -->
`staging/<stage>/<branch-id>/` may hold `Cliche Exhaustion Loop` artifacts:
- `00_脑暴任务卡.md`
- `01_直觉俗套清单.md`
- `02_反驳与否认.md`
- `03_变异候选.md`
- `04_保留候选.md`
- `05_定稿结论.md`
```

- [ ] **Step 4: Run the docs test again**

Run:

```bash
python3 -m unittest __tests__.novel_studio.test_subagent_docs
```

Expected:
- PASS with docs assertions covering the new protocol and branch-file layout

- [ ] **Step 5: Commit the docs task**

```bash
git add skills/novel-studio/SKILL.md \
  skills/novel-studio/README.md \
  skills/novel-studio/references/cliche-exhaustion.md \
  skills/novel-studio/references/workflow.md \
  skills/novel-studio/references/outlining.md \
  skills/novel-studio/references/market-research.md \
  skills/novel-studio/references/topic-report-template.md \
  skills/novel-studio/references/opening-design.md \
  skills/novel-studio/references/anti-template-checklist.md \
  skills/novel-studio/references/proofreading.md \
  skills/novel-studio/references/state-management.md \
  skills/novel-studio/references/state-fields-template.md \
  skills/novel-studio/references/file-structure.md \
  __tests__/novel_studio/test_subagent_docs.py
git commit -m "docs: add cliche exhaustion protocol"
```

### Task 2: Add State Defaults and Status Output for Brainstorm Control

**Files:**
- Modify: `skills/novel-studio/scripts/revision_utils.py`
- Modify: `skills/novel-studio/scripts/load_project_state.py`
- Modify: `skills/novel-studio/scripts/novel_project_status.py`
- Modify: `skills/novel-studio/references/state-management.md`
- Modify: `skills/novel-studio/references/state-fields-template.md`
- Test: `__tests__/novel_studio/test_supervisor_persistence.py`
- Test: `__tests__/novel_studio/test_narrative_intelligence_state.py`

- [ ] **Step 1: Write the failing state/status tests**

```python
def test_load_state_adds_cliche_exhaustion_review_fields(self):
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / '测试小说'
        project.mkdir()
        self.write_state(
            project,
            {
                'project': {'title': '测试小说', 'rootPath': str(project)},
                'workflow': {'currentStage': 'story-planning'},
                'review': {},
                'narrativeIntelligence': {'styleRisk': {}},
            },
        )

        result = run_script('load_project_state.py', str(project))
        self.assertEqual(result.returncode, 0, result.stderr)

        state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
        self.assertIsNone(state['review']['brainstormMode'])
        self.assertIsNone(state['review']['brainstormFocus'])
        self.assertIsNone(state['review']['brainstormRound'])
        self.assertIsNone(state['review']['selectedBranch'])
        self.assertEqual(state['narrativeIntelligence']['styleRisk']['noveltyAxes'], [])
        self.assertIsNone(state['narrativeIntelligence']['styleRisk']['lastClicheScanStage'])


def test_status_brief_shows_brainstorm_focus_and_cliche_summary(self):
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / '测试小说'
        project.mkdir()
        self.write_state(
            project,
            {
                'project': {'title': '测试小说', 'rootPath': str(project)},
                'workflow': {'currentStage': 'story-planning', 'status': 'brainstorming'},
                'review': {
                    'brainstormActive': True,
                    'brainstormMode': 'cliche_exhaustion',
                    'brainstormFocus': 'story_engine',
                    'brainstormRound': 'mutation',
                },
                'narrativeIntelligence': {
                    'styleRisk': {
                        'clichePatterns': ['重复使用隐藏实力钩子'],
                        'noveltyAxes': ['desire_inversion'],
                    }
                },
            },
        )

        result = run_script('novel_project_status.py', str(project), '--brief')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('脑暴模式：cliche_exhaustion', result.stdout)
        self.assertIn('脑暴焦点：story_engine / mutation', result.stdout)
        self.assertIn('套路风险：1 条 / 新意轴：1 条', result.stdout)
```

- [ ] **Step 2: Run the targeted tests to verify failure**

Run:

```bash
python3 -m unittest \
  __tests__.novel_studio.test_supervisor_persistence \
  __tests__.novel_studio.test_narrative_intelligence_state
```

Expected:
- FAIL because `review.*` does not yet have the new brainstorm fields
- FAIL because `styleRisk` lacks `noveltyAxes` and `lastClicheScanStage`
- FAIL because `novel_project_status.py` does not print the new summary lines

- [ ] **Step 3: Add defaults, normalization, reconstruction, and status rendering**

```python
# skills/novel-studio/scripts/revision_utils.py
def default_review() -> dict:
    return {
        'currentGate': None,
        'pendingArtifactPaths': [],
        'lastPersistedStage': None,
        'lastPersistedAt': None,
        'brainstormActive': False,
        'activeBranches': [],
        'brainstormMode': None,
        'brainstormFocus': None,
        'brainstormRound': None,
        'selectedBranch': None,
        # ...
    }


def default_narrative_intelligence() -> dict:
    return {
        # ...
        'styleRisk': {
            'clichePatterns': [],
            'lastCokeScore': None,
            'lastClicheScanStage': None,
            'noveltyAxes': [],
        },
    }
```

```python
# skills/novel-studio/scripts/load_project_state.py
review = default_review()
review.update(normalized.get('review', {}))
review['activeBranches'] = normalize_path_list(review.get('activeBranches'))
review['brainstormActive'] = bool(review.get('brainstormActive', False))

style_risk = default_narrative_intelligence()['styleRisk']
style_risk.update(narrative_intelligence.get('styleRisk', {}))
style_risk['clichePatterns'] = list(style_risk.get('clichePatterns', []))
style_risk['noveltyAxes'] = list(style_risk.get('noveltyAxes', []))
```

```python
# skills/novel-studio/scripts/novel_project_status.py
def cliche_risk_summary_text(state: dict) -> str:
    style_risk = state.get('narrativeIntelligence', {}).get('styleRisk', {})
    return f"{len(style_risk.get('clichePatterns', []))} 条 / 新意轴：{len(style_risk.get('noveltyAxes', []))} 条"

# --brief branch
if review.get('brainstormActive'):
    print(f'脑暴模式：{review.get("brainstormMode") or "无"}')
    print(f'脑暴焦点：{review.get("brainstormFocus") or "无"} / {review.get("brainstormRound") or "无"}')
print(f'套路风险：{cliche_risk_summary_text(state)}')
```

- [ ] **Step 4: Run the targeted tests again**

Run:

```bash
python3 -m unittest \
  __tests__.novel_studio.test_supervisor_persistence \
  __tests__.novel_studio.test_narrative_intelligence_state
```

Expected:
- PASS with normalized defaults and status output

- [ ] **Step 5: Commit the state task**

```bash
git add skills/novel-studio/scripts/revision_utils.py \
  skills/novel-studio/scripts/load_project_state.py \
  skills/novel-studio/scripts/novel_project_status.py \
  skills/novel-studio/references/state-management.md \
  skills/novel-studio/references/state-fields-template.md \
  __tests__/novel_studio/test_supervisor_persistence.py \
  __tests__/novel_studio/test_narrative_intelligence_state.py
git commit -m "feat: add cliche exhaustion state fields"
```

### Task 3: Scaffold and Promote Cliche Exhaustion Branches

**Files:**
- Modify: `skills/novel-studio/scripts/manage_stage_branches.py`
- Modify: `skills/novel-studio/scripts/novel_project_status.py`
- Test: `__tests__/novel_studio/test_supervisor_persistence.py`

- [ ] **Step 1: Write the failing branch-management tests**

```python
def test_create_cliche_exhaustion_branch_scaffolds_required_files(self):
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / '测试小说'
        project.mkdir()
        result = run_script(
            'manage_stage_branches.py',
            'create',
            str(project),
            'story-planning',
            '版本A',
            '--mode',
            'cliche_exhaustion',
            '--focus',
            'story_engine',
            '--round',
            'enumeration',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        branch = project / 'staging' / 'story-planning' / '版本A'
        self.assertTrue((branch / '00_脑暴任务卡.md').exists())
        self.assertTrue((branch / '01_直觉俗套清单.md').exists())
        self.assertTrue((branch / '05_定稿结论.md').exists())

        state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
        self.assertEqual(state['review']['brainstormMode'], 'cliche_exhaustion')
        self.assertEqual(state['review']['brainstormFocus'], 'story_engine')
        self.assertEqual(state['review']['brainstormRound'], 'enumeration')


def test_promote_cliche_exhaustion_branch_persists_selected_branch_and_novelty_axes(self):
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / '测试小说'
        project.mkdir()
        branch = project / 'staging' / 'story-planning' / '版本B'
        branch.mkdir(parents=True)
        (branch / '01_想法.md').write_text('# 想法\n\n保留版本\n', encoding='utf-8')
        (branch / '05_定稿结论.md').write_text(
            '# 定稿结论\n\n'
            '## 保留方向\n- 版本B\n\n'
            '## Novelty Axes\n- desire_inversion\n- relationship_consequence\n',
            encoding='utf-8',
        )
        self.write_state(
            project,
            {
                'project': {'title': '测试小说', 'rootPath': str(project)},
                'workflow': {'currentStage': 'story-planning', 'status': 'brainstorming'},
                'review': {'brainstormActive': True, 'activeBranches': ['story-planning/版本B']},
            },
        )

        result = run_script(
            'manage_stage_branches.py',
            'promote',
            str(project),
            'story-planning',
            '版本B',
            '--copy-file',
            '01_想法.md',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
        self.assertEqual(state['review']['selectedBranch'], 'story-planning/版本B')
        self.assertEqual(
            state['narrativeIntelligence']['styleRisk']['noveltyAxes'],
            ['desire_inversion', 'relationship_consequence'],
        )
```

- [ ] **Step 2: Run the targeted branch tests to verify failure**

Run:

```bash
python3 -m unittest __tests__.novel_studio.test_supervisor_persistence
```

Expected:
- FAIL because `manage_stage_branches.py` does not accept `--mode`, `--focus`, or `--round`
- FAIL because it does not scaffold branch files
- FAIL because promotion does not parse novelty axes or set `selectedBranch`

- [ ] **Step 3: Extend branch creation, promotion, and pruning**

```python
# skills/novel-studio/scripts/manage_stage_branches.py
create.add_argument('--mode', choices=['standard', 'cliche_exhaustion'], default='standard')
create.add_argument('--focus')
create.add_argument('--round')

CLEX_FILES = [
    '00_脑暴任务卡.md',
    '01_直觉俗套清单.md',
    '02_反驳与否认.md',
    '03_变异候选.md',
    '04_保留候选.md',
    '05_定稿结论.md',
]

def scaffold_cliche_exhaustion(branch_path: Path, stage: str, focus: str | None) -> None:
    contents = {
        '00_脑暴任务卡.md': f'# 脑暴任务卡\\n\\n- stage: {stage}\\n- focus: {focus or "未指定"}\\n',
        '01_直觉俗套清单.md': '# 直觉俗套清单\\n\\n',
        '02_反驳与否认.md': '# 反驳与否认\\n\\n',
        '03_变异候选.md': '# 变异候选\\n\\n',
        '04_保留候选.md': '# 保留候选\\n\\n',
        '05_定稿结论.md': '# 定稿结论\\n\\n## 保留方向\\n- 待定\\n\\n## Novelty Axes\\n',
    }
    for filename, text in contents.items():
        (branch_path / filename).write_text(text, encoding='utf-8')
```

```python
# skills/novel-studio/scripts/manage_stage_branches.py
review['brainstormMode'] = args.mode
review['brainstormFocus'] = args.focus
review['brainstormRound'] = args.round

def parse_novelty_axes(branch_root: Path) -> list[str]:
    conclusion = branch_root / '05_定稿结论.md'
    if not conclusion.exists():
        return []
    axes = []
    in_axes = False
    for raw in conclusion.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if line == '## Novelty Axes':
            in_axes = True
            continue
        if in_axes and line.startswith('## '):
            break
        if in_axes and line.startswith('- '):
            axes.append(line[2:].strip())
    return axes

review['selectedBranch'] = branch_state_key(stage, branch_id)
data['narrativeIntelligence']['styleRisk']['noveltyAxes'] = parse_novelty_axes(selected_branch)
```

- [ ] **Step 4: Run the targeted branch tests again**

Run:

```bash
python3 -m unittest __tests__.novel_studio.test_supervisor_persistence
```

Expected:
- PASS with scaffolded files, persisted mode/focus/round, and retained novelty axes

- [ ] **Step 5: Commit the branch task**

```bash
git add skills/novel-studio/scripts/manage_stage_branches.py \
  skills/novel-studio/scripts/novel_project_status.py \
  __tests__/novel_studio/test_supervisor_persistence.py
git commit -m "feat: scaffold cliche exhaustion branches"
```

### Task 4: Add Lightweight Proofreading-Time Cliche Risk Reporting

**Files:**
- Modify: `skills/novel-studio/scripts/narrative_checker.py`
- Modify: `skills/novel-studio/scripts/update_narrative_intelligence.py`
- Modify: `skills/novel-studio/scripts/apply_stage_execution_result.py`
- Modify: `skills/novel-studio/scripts/novel_project_status.py`
- Modify: `skills/novel-studio/references/proofreading.md`
- Test: `__tests__/novel_studio/test_narrative_intelligence_review.py`

- [ ] **Step 1: Write the failing cliché-risk runtime tests**

```python
def test_proofreading_refresh_records_cliche_patterns_for_duplicate_hooks(self):
    with tempfile.TemporaryDirectory() as tmp:
        project = self.create_review_project(Path(tmp), current_stage='proofreading')
        (project / '05_本轮章节规划.md').write_text(
            '## 逐章规划\\n'
            '### 第1章\\n- 本章吸引点：隐藏实力\\n- 高潮点：结尾反转\\n'
            '### 第2章\\n- 本章吸引点：隐藏实力\\n- 高潮点：结尾反转\\n',
            encoding='utf-8',
        )

        result = run_script(
            'update_narrative_intelligence.py',
            str(project),
            '--stage',
            'proofreading',
            '--chapter-label',
            '第1章',
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
        style_risk = state['narrativeIntelligence']['styleRisk']
        self.assertIn('重复吸引点：隐藏实力', style_risk['clichePatterns'])
        self.assertIn('重复高潮点：结尾反转', style_risk['clichePatterns'])
        self.assertEqual(style_risk['lastClicheScanStage'], 'proofreading')


def test_status_brief_shows_cliche_risk_count(self):
    with tempfile.TemporaryDirectory() as tmp:
        project = self.create_review_project(
            Path(tmp),
            current_stage='proofreading',
            narrative_intelligence={
                'styleRisk': {
                    'clichePatterns': ['重复吸引点：隐藏实力'],
                    'noveltyAxes': ['desire_inversion'],
                    'lastClicheScanStage': 'proofreading',
                }
            },
        )

        result = run_script('novel_project_status.py', str(project), '--brief')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('套路风险：1 条 / 新意轴：1 条', result.stdout)
```

- [ ] **Step 2: Run the targeted runtime tests to verify failure**

Run:

```bash
python3 -m unittest __tests__.novel_studio.test_narrative_intelligence_review
```

Expected:
- FAIL because `styleRisk.clichePatterns` is never refreshed during proofreading
- FAIL because `lastClicheScanStage` is never written

- [ ] **Step 3: Add a deterministic lightweight cliché-risk checker**

```python
# skills/novel-studio/scripts/narrative_checker.py
def build_cliche_findings(project: Path, state: dict) -> dict[str, object]:
    findings = {
        'clichePatterns': [],
        'lastClicheScanStage': 'proofreading',
    }
    chapter_plan = Path(project) / '05_本轮章节规划.md'
    if not chapter_plan.exists():
        return findings

    attraction_points: dict[str, int] = {}
    climax_targets: dict[str, int] = {}
    for raw in chapter_plan.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if line.startswith('- 本章吸引点：'):
            value = line.split('：', 1)[1].strip()
            attraction_points[value] = attraction_points.get(value, 0) + 1
        if line.startswith('- 高潮点：'):
            value = line.split('：', 1)[1].strip()
            climax_targets[value] = climax_targets.get(value, 0) + 1

    findings['clichePatterns'].extend(
        f'重复吸引点：{value}' for value, count in attraction_points.items() if value and count > 1
    )
    findings['clichePatterns'].extend(
        f'重复高潮点：{value}' for value, count in climax_targets.items() if value and count > 1
    )
    return findings


def refresh_cliche_findings(project: Path, state: dict) -> dict[str, object]:
    findings = build_cliche_findings(project, state)
    narrative_intelligence = state.setdefault('narrativeIntelligence', default_narrative_intelligence())
    style_risk = narrative_intelligence.setdefault(
        'styleRisk',
        default_narrative_intelligence()['styleRisk'],
    )
    style_risk['clichePatterns'] = list(findings['clichePatterns'])
    style_risk['lastClicheScanStage'] = findings['lastClicheScanStage']
    return findings
```

```python
# skills/novel-studio/scripts/update_narrative_intelligence.py
from narrative_checker import refresh_cliche_findings, refresh_consistency_findings

if args.stage == 'proofreading':
    refresh_consistency_findings(project, state)
    refresh_cliche_findings(project, state)
```

```python
# skills/novel-studio/scripts/apply_stage_execution_result.py
from narrative_checker import refresh_cliche_findings, refresh_consistency_findings

if stage == 'proofreading':
    refresh_consistency_findings(sync_project, data)
    refresh_cliche_findings(sync_project, data)
```

- [ ] **Step 4: Run the targeted runtime tests again**

Run:

```bash
python3 -m unittest __tests__.novel_studio.test_narrative_intelligence_review
```

Expected:
- PASS with deterministic duplicate-hook findings recorded in `styleRisk.*`

- [ ] **Step 5: Commit the runtime checker task**

```bash
git add skills/novel-studio/scripts/narrative_checker.py \
  skills/novel-studio/scripts/update_narrative_intelligence.py \
  skills/novel-studio/scripts/apply_stage_execution_result.py \
  skills/novel-studio/scripts/novel_project_status.py \
  skills/novel-studio/references/proofreading.md \
  __tests__/novel_studio/test_narrative_intelligence_review.py
git commit -m "feat: record cliche risk during proofreading"
```

### Task 5: Run Full Verification and Reconcile Docs

**Files:**
- Verify only

- [ ] **Step 1: Run the full `novel_studio` suite**

Run:

```bash
python3 -m unittest discover -s __tests__/novel_studio -p 'test_*.py'
```

Expected:
- PASS with the full suite green

- [ ] **Step 2: Inspect working tree**

Run:

```bash
git status --short
```

Expected:
- empty output

- [ ] **Step 3: Reconcile any drift before completion**

If `git status --short` is not empty:

```bash
git diff --stat
```

Expected:
- only directly-related file changes remain; otherwise fix drift before claiming completion
