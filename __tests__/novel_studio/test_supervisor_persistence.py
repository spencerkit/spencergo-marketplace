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
                    'approvals': {'discoveryApproved': False},
                    'review': {
                        'currentGate': 'waiting_discovery_feedback',
                        'pendingArtifactPaths': ['00_选题报告.md'],
                    },
                },
            )

            result = run_script('check_stage_ready.py', str(project), 'story-planning')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Current review gate is still open: waiting_discovery_feedback', result.stderr + result.stdout)
