import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / 'skills/novel-studio/scripts'

TIMELINE_ARTIFACT = '05F_时间与事件图谱.md'
FORESHADOW_TRIPLES_ARTIFACT = '05G_伏笔三元组账本.md'
THEORY_OF_MIND_ARTIFACT = '05H_角色认知与误判表.md'
CONSISTENCY_ARTIFACT = '05I_证据链与矛盾对照表.md'
NARRATIVE_ARTIFACTS = [
    TIMELINE_ARTIFACT,
    FORESHADOW_TRIPLES_ARTIFACT,
    THEORY_OF_MIND_ARTIFACT,
    CONSISTENCY_ARTIFACT,
]


def run_script(name, *args):
    cmd = ['python3', str(SCRIPTS / name), *args]
    return subprocess.run(cmd, text=True, capture_output=True)


class NarrativeIntelligenceRuntimeTest(unittest.TestCase):
    def write_state(self, project: Path, payload: dict) -> None:
        (project / '.novel-state.json').write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

    def write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    def load_reconstructed_state(self, project: Path) -> dict:
        self.assertFalse((project / '.novel-state.json').exists())
        result = run_script('load_project_state.py', str(project))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))

    def create_stage_runtime_project(self, root: Path, *, current_stage: str) -> Path:
        project = root / '测试小说'
        project.mkdir()
        (project / '00A_热点扫描.md').write_text('# scan\n', encoding='utf-8')
        (project / '00B_用户偏好.md').write_text('# intake\n', encoding='utf-8')
        (project / '00_选题报告.md').write_text('# topic\n', encoding='utf-8')
        (project / '00C_底盘与切口决策.md').write_text(
            '# 底盘与切口\n\n'
            '## 主赛道\n- 规则异变都市\n\n'
            '## 辅助风味\n- 悬疑调查\n\n'
            '## 平台模式\n- 起点模式\n',
            encoding='utf-8',
        )
        (project / '01_想法.md').write_text('# idea\n', encoding='utf-8')
        (project / '01A_风格圣经.md').write_text(
            '# 风格圣经\n\n'
            '## 平台模式\n- 起点模式\n\n'
            '## 叙述基调\n- 冷峻、克制、信息前推\n',
            encoding='utf-8',
        )
        (project / '01B_总主线与卷级推进.md').write_text('# 总主线\n\n主角逐步逼近真相。\n', encoding='utf-8')
        (project / '02_大纲.md').write_text('# outline\n\n主线推进', encoding='utf-8')
        (project / '03_人物小传.md').write_text('# roles\n\n主角：林川', encoding='utf-8')
        (project / '04A_开篇设计.md').write_text('# 开篇设计\n\n- 第1章点火\n', encoding='utf-8')
        (project / '05_本轮章节规划.md').write_text(
            '## 本轮范围\n- 第1章\n\n'
            '## 本轮写作重点\n- 开篇立钩子\n\n'
            '## 逐章规划\n'
            '### 第1章\n'
            '- 本章目标：建立主角处境\n'
            '- 出场人物：林川\n'
            '- 高潮点：结尾反转\n'
            '- 吸引点：隐藏实力\n',
            encoding='utf-8',
        )
        (project / '05_前情回顾.md').write_text(
            '## 当前已推进到的位置\n- 开篇\n\n'
            '## 最近一轮发生的关键事件\n- 无\n\n'
            '## 当前未回收的伏笔 / 悬念\n- 黑箱来历\n\n'
            '## 下一轮写作必须记住的点\n- 主角表面隐忍\n',
            encoding='utf-8',
        )
        (project / '05B_世界规则账本.md').write_text('# 世界规则账本\n\n- 失序区只在夜间扩张\n', encoding='utf-8')
        (project / '05C_伏笔回收台账.md').write_text('# 伏笔回收台账\n\n- 黑箱来源：未回收\n', encoding='utf-8')
        (project / '05D_关系状态表.md').write_text('# 关系状态表\n\n- 林川 / 顾遥：互相试探\n', encoding='utf-8')
        (project / '05E_能力与资源变化表.md').write_text('# 能力与资源变化表\n\n- 黑箱权限：一级\n', encoding='utf-8')

        characters = project / 'characters'
        characters.mkdir()
        (characters / '林川.md').write_text('# 林川\n\n性格：隐忍', encoding='utf-8')

        manuscript = project / 'manuscript'
        manuscript.mkdir()
        (manuscript / '第1章_开端.md').write_text('# 第一章\n\n正文\n', encoding='utf-8')

        self.write_state(
            project,
            {
                'project': {'title': '测试小说', 'rootPath': str(project)},
                'workflow': {
                    'currentStage': current_stage,
                    'currentSubstage': None,
                    'lastCompletedStage': 'polishing',
                    'nextStage': current_stage,
                    'status': 'in_progress',
                },
                'approvals': {
                    'discoveryApproved': True,
                    'planningApproved': True,
                    'characterApproved': True,
                    'openingApproved': True,
                    'draftingApproved': True,
                    'polishingApproved': True,
                    'proofreadingApproved': False,
                    'finalApproved': False,
                },
                'batch': {
                    'active': True,
                    'chapterRange': '第1章',
                    'chapterCount': 1,
                    'scopeConfirmed': True,
                    'chapterPlanExists': True,
                    'chapterPlanApproved': True,
                    'draftComplete': True,
                    'polishingComplete': True,
                    'proofreadingComplete': False,
                    'recapUpdated': False,
                    'awaitingNextBatchDecision': False,
                    'focus': None,
                    'attractionPoints': ['隐藏实力'],
                    'climaxTarget': '结尾反转',
                },
                'review': {'currentGate': None},
                'revision': {
                    'active': False,
                    'currentRevisionGate': None,
                    'awaitingUserApproval': False,
                },
                'blockingIssues': [],
                'notes': {
                    'platformProfile': '起点模式',
                    'primaryTrack': '规则异变都市',
                    'secondaryFlavor': '悬疑调查',
                    'styleBibleVersion': 'v1',
                },
            },
        )
        return project

    def test_approving_planning_feedback_initializes_parent_owned_intelligence_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '01_想法.md').write_text('# 想法\n\n## 核心设定\n- 规则污染\n', encoding='utf-8')
            (project / '02_大纲.md').write_text('# 大纲\n\n## 第一卷\n- 黑箱出现\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'story-planning',
                        'currentSubstage': None,
                        'lastCompletedStage': 'discovery',
                        'nextStage': 'character-system',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'discoveryApproved': True,
                        'planningApproved': False,
                    },
                    'review': {
                        'currentGate': 'waiting_planning_feedback',
                        'pendingArtifactPaths': ['01_想法.md', '02_大纲.md'],
                        'lastPersistedStage': 'story-planning',
                    },
                },
            )

            result = run_script('approve_stage_gate.py', str(project), 'waiting_planning_feedback')
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['approvals']['planningApproved'])
            self.assertEqual(state['workflow']['lastCompletedStage'], 'story-planning')
            self.assertEqual(state['workflow']['currentStage'], 'character-system')
            self.assertEqual(state['review']['pendingArtifactPaths'], [])
            self.assertTrue(state['narrativeIntelligence']['timeline']['enabled'])

            for artifact_name in NARRATIVE_ARTIFACTS:
                artifact = project / artifact_name
                self.assertTrue(artifact.exists(), f'missing artifact: {artifact_name}')
                self.assertTrue(artifact.read_text(encoding='utf-8').strip(), f'empty artifact: {artifact_name}')

    def test_approving_planning_feedback_repopulates_empty_preexisting_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '01_想法.md').write_text('# 想法\n\n## 核心设定\n- 规则污染\n', encoding='utf-8')
            (project / '02_大纲.md').write_text('# 大纲\n\n## 第一卷\n- 黑箱出现\n', encoding='utf-8')
            empty_artifact = project / TIMELINE_ARTIFACT
            empty_artifact.write_text('', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'story-planning',
                        'currentSubstage': None,
                        'lastCompletedStage': 'discovery',
                        'nextStage': 'character-system',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'discoveryApproved': True,
                        'planningApproved': False,
                    },
                    'review': {
                        'currentGate': 'waiting_planning_feedback',
                        'pendingArtifactPaths': ['01_想法.md', '02_大纲.md'],
                        'lastPersistedStage': 'story-planning',
                    },
                },
            )

            result = run_script('approve_stage_gate.py', str(project), 'waiting_planning_feedback')
            self.assertEqual(result.returncode, 0, result.stderr)

            timeline_text = empty_artifact.read_text(encoding='utf-8')
            self.assertTrue(timeline_text.strip())

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['narrativeIntelligence']['timeline']['enabled'])

            for artifact_name in NARRATIVE_ARTIFACTS:
                artifact = project / artifact_name
                self.assertTrue(artifact.exists(), f'missing artifact: {artifact_name}')
                self.assertTrue(artifact.read_text(encoding='utf-8').strip(), f'empty artifact: {artifact_name}')

    def test_load_project_state_enables_timeline_when_full_canonical_artifact_set_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()

            for artifact_name in NARRATIVE_ARTIFACTS:
                (project / artifact_name).write_text(f'# {artifact_name}\n\n已初始化\n', encoding='utf-8')

            state = self.load_reconstructed_state(project)

            self.assertTrue(state['narrativeIntelligence']['timeline']['enabled'])

    def test_load_project_state_keeps_timeline_disabled_when_one_canonical_artifact_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()

            for artifact_name in NARRATIVE_ARTIFACTS:
                content = '' if artifact_name == TIMELINE_ARTIFACT else f'# {artifact_name}\n\n已初始化\n'
                (project / artifact_name).write_text(content, encoding='utf-8')

            state = self.load_reconstructed_state(project)

            self.assertFalse(state['narrativeIntelligence']['timeline']['enabled'])

    def test_load_project_state_keeps_timeline_disabled_when_artifact_set_is_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()

            for artifact_name in NARRATIVE_ARTIFACTS[:2]:
                (project / artifact_name).write_text(f'# {artifact_name}\n\n部分初始化\n', encoding='utf-8')

            state = self.load_reconstructed_state(project)

            self.assertFalse(state['narrativeIntelligence']['timeline']['enabled'])

    def test_apply_accepted_proofreading_result_refreshes_narrative_intelligence_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_stage_runtime_project(root, current_stage='proofreading')
            bundle_file = root / 'proofreading-bundle.json'
            result_file = root / 'proofreading-result.json'

            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
                '--bundle-file',
                str(bundle_file),
                '--dispatch-dir',
                str(root / 'dispatch'),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            (project / '05A_本轮校对报告.md').write_text(
                '# 05A_本轮校对报告\n\n- judgment: acceptable\n- summary: 通过\n',
                encoding='utf-8',
            )
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['05A_本轮校对报告.md'],
                    'blockedReasons': [],
                    'summary': '本轮校对完成，可进入终审',
                    'notesForNextStage': '进入 final-review',
                    'risks': [],
                    'judgment': 'acceptable',
                    'continuity': '通过',
                    'logic': '通过',
                    'characterOOC': '无',
                    'blockers': [],
                    'fixDirection': '无需处理',
                },
            )

            apply_result = run_script(
                'apply_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertEqual(apply_result.returncode, 0, apply_result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            narrative_intelligence = state['narrativeIntelligence']

            self.assertEqual(narrative_intelligence['timeline']['lastUpdatedBatch'], '第1章')
            self.assertEqual(narrative_intelligence['timeline']['lastTouchedChapters'], ['第1章'])
            self.assertEqual(narrative_intelligence['cfpg']['lastUpdatedBatch'], '第1章')
            self.assertEqual(narrative_intelligence['theoryOfMind']['lastUpdatedBatch'], '第1章')
            self.assertEqual(narrative_intelligence['consistency']['lastCheckStage'], 'proofreading')

    def test_apply_nonaccepted_proofreading_result_does_not_refresh_narrative_intelligence_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_stage_runtime_project(root, current_stage='proofreading')
            bundle_file = root / 'proofreading-bundle.json'
            result_file = root / 'proofreading-result.json'

            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
                '--bundle-file',
                str(bundle_file),
                '--dispatch-dir',
                str(root / 'dispatch'),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            (project / '05A_本轮校对报告.md').write_text(
                '# 05A_本轮校对报告\n\n- judgment: needs revision\n- summary: 需要回修\n',
                encoding='utf-8',
            )
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['05A_本轮校对报告.md'],
                    'blockedReasons': [],
                    'summary': '本轮校对完成，但需要回修',
                    'notesForNextStage': '等待审核后回修',
                    'risks': [],
                    'judgment': 'needs revision',
                    'continuity': '存在断点',
                    'logic': '存在漏洞',
                    'characterOOC': '轻微',
                    'blockers': ['结尾信息缺口'],
                    'fixDirection': '补足关键解释并重写结尾段落',
                },
            )

            apply_result = run_script(
                'apply_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertEqual(apply_result.returncode, 0, apply_result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            narrative_intelligence = state['narrativeIntelligence']

            self.assertIsNone(narrative_intelligence['timeline']['lastUpdatedBatch'])
            self.assertEqual(narrative_intelligence['timeline']['lastTouchedChapters'], [])
            self.assertIsNone(narrative_intelligence['cfpg']['lastUpdatedBatch'])
            self.assertIsNone(narrative_intelligence['theoryOfMind']['lastUpdatedBatch'])
            self.assertIsNone(narrative_intelligence['consistency']['lastCheckStage'])

    def test_apply_conditionally_acceptable_proofreading_result_refreshes_metadata_using_cli_project_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_stage_runtime_project(root, current_stage='proofreading')
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            state['project']['rootPath'] = str(root / 'moved-project-copy')
            self.write_state(project, state)

            bundle_file = root / 'proofreading-bundle.json'
            result_file = root / 'proofreading-result.json'

            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
                '--bundle-file',
                str(bundle_file),
                '--dispatch-dir',
                str(root / 'dispatch'),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            (project / '05A_本轮校对报告.md').write_text(
                '# 05A_本轮校对报告\n\n- judgment: conditionally acceptable\n- summary: 有条件通过\n',
                encoding='utf-8',
            )
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['05A_本轮校对报告.md'],
                    'blockedReasons': [],
                    'summary': '本轮校对完成，有条件通过',
                    'notesForNextStage': '进入 final-review 前处理提示项',
                    'risks': ['段落衔接还需微调'],
                    'judgment': 'conditionally acceptable',
                    'continuity': '基本通过',
                    'logic': '基本通过',
                    'characterOOC': '无',
                    'blockers': [],
                    'fixDirection': '处理少量措辞和衔接问题',
                },
            )

            apply_result = run_script(
                'apply_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertEqual(apply_result.returncode, 0, apply_result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            narrative_intelligence = state['narrativeIntelligence']

            self.assertEqual(narrative_intelligence['timeline']['lastUpdatedBatch'], '第1章')
            self.assertEqual(narrative_intelligence['timeline']['lastTouchedChapters'], ['第1章'])
            self.assertEqual(narrative_intelligence['cfpg']['lastUpdatedBatch'], '第1章')
            self.assertEqual(narrative_intelligence['theoryOfMind']['lastUpdatedBatch'], '第1章')
            self.assertEqual(narrative_intelligence['consistency']['lastCheckStage'], 'proofreading')


if __name__ == '__main__':
    unittest.main()
