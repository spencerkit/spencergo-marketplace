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

    def load_reconstructed_state(self, project: Path) -> dict:
        self.assertFalse((project / '.novel-state.json').exists())
        result = run_script('load_project_state.py', str(project))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))

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


if __name__ == '__main__':
    unittest.main()
