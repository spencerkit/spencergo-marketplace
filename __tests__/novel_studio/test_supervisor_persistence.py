import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / 'skills/novel-studio/scripts'


def run_script(name, *args):
    cmd = ['python3', str(SCRIPTS / name), *args]
    return subprocess.run(cmd, text=True, capture_output=True)


class SupervisorPersistenceTest(unittest.TestCase):
    def write_state(self, project: Path, payload: dict) -> None:
        (project / '.novel-state.json').write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

    def test_load_state_adds_supervisor_review_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {'currentStage': 'discovery'},
                    'review': {},
                },
            )

            result = run_script('load_project_state.py', str(project))
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['workflow']['status'], 'collecting_inputs')
            self.assertEqual(state['review']['pendingArtifactPaths'], [])
            self.assertIsNone(state['review']['lastPersistedStage'])
            self.assertIsNone(state['review']['lastPersistedAt'])
            self.assertFalse(state['review']['brainstormActive'])
            self.assertEqual(state['review']['activeBranches'], [])

    def test_status_summary_prefers_discovery_feedback_gate_after_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '00_选题报告.md').write_text('# 选题报告\n\n## 推荐方向\n- 规则异变都市\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'discovery',
                        'currentSubstage': None,
                        'lastCompletedStage': None,
                        'nextStage': 'story-planning',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {'discoveryApproved': False},
                    'review': {
                        'currentGate': 'waiting_discovery_feedback',
                        'pendingArtifactPaths': ['00_选题报告.md'],
                        'brainstormActive': False,
                        'activeBranches': [],
                    },
                },
            )

            result = run_script('novel_project_status.py', str(project), '--brief')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('当前卡点：等待你确认 Discovery 阶段结果', result.stdout)
            self.assertIn('建议下一步：等待你确认 Discovery 阶段结果', result.stdout)

    def test_load_state_pending_artifacts_force_awaiting_user_approval_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '00_选题报告.md').write_text('# 选题报告\n\n## 推荐方向\n- 规则异变都市\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'discovery',
                        'currentSubstage': None,
                        'lastCompletedStage': None,
                        'nextStage': 'story-planning',
                        'status': 'in_progress',
                    },
                    'review': {
                        'currentGate': 'waiting_discovery_feedback',
                        'pendingArtifactPaths': ['00_选题报告.md'],
                    },
                },
            )

            result = run_script('load_project_state.py', str(project))
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['workflow']['status'], 'awaiting_user_approval')

    def test_load_state_pending_artifacts_force_awaiting_user_approval_without_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '00_选题报告.md').write_text('# 选题报告\n\n## 推荐方向\n- 规则异变都市\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'discovery',
                        'currentSubstage': None,
                        'lastCompletedStage': None,
                        'nextStage': 'story-planning',
                        'status': 'collecting_inputs',
                    },
                    'review': {
                        'currentGate': None,
                        'pendingArtifactPaths': ['00_选题报告.md'],
                    },
                },
            )

            result = run_script('load_project_state.py', str(project))
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['workflow']['status'], 'awaiting_user_approval')

    def test_check_stage_ready_rejects_advancement_with_open_pending_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '00_选题报告.md').write_text('# 选题报告\n\n## 推荐方向\n- 规则异变都市\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'discovery',
                        'currentSubstage': None,
                        'lastCompletedStage': None,
                        'nextStage': 'story-planning',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {'discoveryApproved': True},
                    'review': {
                        'currentGate': None,
                        'pendingArtifactPaths': ['00_选题报告.md'],
                    },
                },
            )

            result = run_script('check_stage_ready.py', str(project), 'story-planning')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Pending artifacts still await approval: 00_选题报告.md', result.stderr + result.stdout)

    def test_approve_stage_gate_clears_pending_artifacts_and_advances_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '00_选题报告.md').write_text('# 选题报告\n\n## 推荐方向\n- 规则异变都市\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'discovery',
                        'currentSubstage': None,
                        'lastCompletedStage': None,
                        'nextStage': 'story-planning',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'discoveryApproved': False,
                        'planningApproved': False,
                        'characterApproved': False,
                        'openingApproved': False,
                        'draftingApproved': False,
                        'polishingApproved': False,
                        'proofreadingApproved': False,
                        'finalApproved': False,
                    },
                    'review': {
                        'currentGate': 'waiting_discovery_feedback',
                        'pendingArtifactPaths': ['00_选题报告.md'],
                        'lastPersistedStage': 'discovery',
                    },
                },
            )

            result = run_script('approve_stage_gate.py', str(project), 'waiting_discovery_feedback')
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['approvals']['discoveryApproved'])
            self.assertEqual(state['workflow']['lastCompletedStage'], 'discovery')
            self.assertEqual(state['workflow']['currentStage'], 'story-planning')
            self.assertEqual(state['workflow']['nextStage'], 'story-planning')
            self.assertEqual(state['workflow']['status'], 'collecting_inputs')
            self.assertIsNone(state['review']['currentGate'])
            self.assertEqual(state['review']['pendingArtifactPaths'], [])

    def test_status_brief_shows_pending_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
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
                    'review': {
                        'currentGate': 'waiting_planning_feedback',
                        'pendingArtifactPaths': ['01_想法.md', '02_大纲.md'],
                    },
                },
            )

            result = run_script('novel_project_status.py', str(project), '--brief')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('当前状态：awaiting_user_approval', result.stdout)
            self.assertIn('待审批文件：01_想法.md, 02_大纲.md', result.stdout)
