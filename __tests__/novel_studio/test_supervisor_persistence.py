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

    def test_approve_stage_gate_clears_opening_substage_without_marking_drafting_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '04A_开篇设计.md').write_text('# 开篇设计\n\n## 前三章任务\n- 第1章点火\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': 'opening-review',
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'openingApproved': False,
                    },
                    'review': {
                        'currentGate': 'waiting_opening_feedback',
                        'pendingArtifactPaths': ['04A_开篇设计.md'],
                        'lastPersistedStage': 'drafting',
                    },
                },
            )

            result = run_script('approve_stage_gate.py', str(project), 'waiting_opening_feedback')
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['approvals']['openingApproved'])
            self.assertEqual(state['workflow']['lastCompletedStage'], 'character-system')
            self.assertEqual(state['workflow']['currentStage'], 'drafting')
            self.assertEqual(state['workflow']['currentSubstage'], None)
            self.assertEqual(state['workflow']['nextStage'], 'drafting')
            self.assertEqual(state['workflow']['status'], 'collecting_inputs')

    def test_approve_stage_gate_rejects_final_review_when_not_deliverable(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '07_终审报告.md').write_text('# 终审报告\n\n## 最终结论\n- rework required\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'final-review',
                        'currentSubstage': None,
                        'lastCompletedStage': 'proofreading',
                        'nextStage': None,
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'finalApproved': False,
                    },
                    'review': {
                        'currentGate': 'waiting_final_review_feedback',
                        'pendingArtifactPaths': ['07_终审报告.md'],
                        'finalDecision': 'rework required',
                        'finalDeliveryReady': False,
                        'finalBlockingIssues': ['需要返工'],
                    },
                },
            )

            result = run_script('approve_stage_gate.py', str(project), 'waiting_final_review_feedback')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('final review is not ready for approval', result.stderr + result.stdout)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertFalse(state['approvals']['finalApproved'])
            self.assertEqual(state['review']['currentGate'], 'waiting_final_review_feedback')

    def test_persist_stage_artifacts_writes_whitelisted_discovery_files_and_sets_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            artifact_file = Path(tmp) / 'discovery-artifacts.json'
            artifact_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'artifactUpdates': {
                            '00B_用户偏好.md': '# 用户偏好\n\n- 爽感优先\n',
                            '00_选题报告.md': '# 选题报告\n\n## 推荐方向\n- 规则异变都市\n',
                        },
                        'summary': 'Discovery 已形成正式候选方案',
                        'blockedReasons': [],
                        'notesForNextStage': '等待确认后进入 story-planning',
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script(
                'persist_stage_artifacts.py',
                str(project),
                'discovery',
                '--artifact-file',
                str(artifact_file),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / '00B_用户偏好.md').exists())
            self.assertTrue((project / '00_选题报告.md').exists())

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['workflow']['status'], 'awaiting_user_approval')
            self.assertEqual(state['review']['currentGate'], 'waiting_discovery_feedback')
            self.assertEqual(
                state['review']['pendingArtifactPaths'],
                ['00B_用户偏好.md', '00_选题报告.md'],
            )

    def test_persist_stage_artifacts_rejects_out_of_scope_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            artifact_file = Path(tmp) / 'bad-artifacts.json'
            artifact_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'artifactUpdates': {
                            '07_终审报告.md': '# 非法写入\n',
                        },
                        'summary': '非法',
                        'blockedReasons': [],
                        'notesForNextStage': '',
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script(
                'persist_stage_artifacts.py',
                str(project),
                'discovery',
                '--artifact-file',
                str(artifact_file),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('out-of-scope artifact for discovery: 07_终审报告.md', result.stderr + result.stdout)

    def test_persist_stage_artifacts_supports_drafting_opening_substage(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            artifact_file = Path(tmp) / 'opening-artifacts.json'
            artifact_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'artifactUpdates': {
                            '04A_开篇设计.md': '# 开篇设计\n\n## 前三章任务\n- 第1章点火\n',
                        },
                        'summary': 'Opening Gate 包已成型',
                        'blockedReasons': [],
                        'notesForNextStage': '等待确认 opening gate',
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': 'opening-review',
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'producing_artifact',
                    },
                    'review': {'pendingArtifactPaths': [], 'brainstormActive': False, 'activeBranches': []},
                },
            )

            result = run_script(
                'persist_stage_artifacts.py',
                str(project),
                'drafting',
                '--substage',
                'opening-review',
                '--artifact-file',
                str(artifact_file),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / '04A_开篇设计.md').exists())

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['review']['currentGate'], 'waiting_opening_feedback')
            self.assertEqual(state['review']['pendingArtifactPaths'], ['04A_开篇设计.md'])

    def test_approve_stage_gate_advances_chapter_to_polishing_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text(
                '## 逐章规划\n### 第1章\n- 本章目标：点火\n',
                encoding='utf-8',
            )
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': None,
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'polishing',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'draftingApproved': False,
                        'polishingApproved': False,
                        'proofreadingApproved': False,
                    },
                    'review': {'currentGate': 'waiting_draft_feedback', 'pendingArtifactPaths': []},
                    'batch': {
                        'active': True,
                        'chapterPlanApproved': True,
                        'chapterTasks': [
                            {
                                'chapterLabel': '第1章',
                                'manuscriptPath': 'manuscript/第1章_开端.md',
                                'phase': 'drafting',
                                'phaseStatus': 'awaiting_user_review',
                                'lastSummary': '第1章初稿待审核',
                                'blockers': [],
                                'updatedAt': '2026-03-28T10:00:00Z',
                            }
                        ],
                        'pendingProgressItems': [],
                    },
                },
            )

            result = run_script('approve_stage_gate.py', str(project), 'waiting_draft_feedback')

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            task = state['batch']['chapterTasks'][0]
            self.assertEqual(task['phase'], 'polishing')
            self.assertEqual(task['phaseStatus'], 'queued')
            self.assertEqual(task['lastSummary'], '第1章待润色')

    def test_status_brief_shows_chapter_progress_and_pending_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'polishing',
                        'currentSubstage': None,
                        'lastCompletedStage': 'drafting',
                        'nextStage': 'proofreading',
                        'status': 'in_progress',
                    },
                    'batch': {
                        'chapterTasks': [
                            {
                                'chapterLabel': '第1章',
                                'manuscriptPath': 'manuscript/第1章_开端.md',
                                'phase': 'polishing',
                                'phaseStatus': 'in_progress',
                                'lastSummary': '第1章润色中',
                                'blockers': [],
                                'updatedAt': '2026-03-28T10:00:00Z',
                            },
                            {
                                'chapterLabel': '第2章',
                                'manuscriptPath': 'manuscript/第2章_显规.md',
                                'phase': 'proofreading',
                                'phaseStatus': 'completed',
                                'lastSummary': '第2章已完成',
                                'blockers': [],
                                'updatedAt': '2026-03-28T10:01:00Z',
                            },
                        ],
                        'pendingProgressItems': [
                            {
                                'eventId': 'e1',
                                'chapterLabel': '第1章',
                                'phase': 'polishing',
                                'phaseStatus': 'in_progress',
                                'summary': '第1章润色中',
                                'blockers': [],
                                'createdAt': '2026-03-28T10:00:00Z',
                                'reportedAt': None,
                            }
                        ],
                    },
                    'review': {'currentGate': None, 'pendingArtifactPaths': []},
                },
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('章节进度：第1章润色中；第2章已完成', result.stdout)
            self.assertIn('待汇报变更：第1章润色中', result.stdout)

    def test_promote_branch_copies_selected_artifact_and_cleans_other_branches(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            staging_a = project / 'staging' / 'story-planning' / '版本A'
            staging_b = project / 'staging' / 'story-planning' / '版本B'
            staging_a.mkdir(parents=True)
            staging_b.mkdir(parents=True)
            (staging_a / '02_大纲.md').write_text('# 大纲\n\nA 版本\n', encoding='utf-8')
            (staging_b / '02_大纲.md').write_text('# 大纲\n\nB 版本\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'story-planning',
                        'currentSubstage': None,
                        'lastCompletedStage': 'discovery',
                        'nextStage': 'character-system',
                        'status': 'brainstorming',
                    },
                    'review': {
                        'brainstormActive': True,
                        'activeBranches': ['story-planning/版本A', 'story-planning/版本B'],
                        'pendingArtifactPaths': [],
                    },
                },
            )

            result = run_script(
                'manage_stage_branches.py',
                'promote',
                str(project),
                'story-planning',
                '版本B',
                '--copy-file',
                '02_大纲.md',
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((project / '02_大纲.md').read_text(encoding='utf-8'), '# 大纲\n\nB 版本\n')
            self.assertFalse(staging_a.exists())
            self.assertFalse(staging_b.exists())

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertFalse(state['review']['brainstormActive'])
            self.assertEqual(state['review']['activeBranches'], [])
            self.assertEqual(state['review']['currentGate'], 'waiting_planning_feedback')
            self.assertEqual(state['review']['pendingArtifactPaths'], ['02_大纲.md'])
            self.assertEqual(state['workflow']['status'], 'awaiting_user_approval')

    def test_persist_stage_artifacts_writes_whitelisted_discovery_files_and_sets_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            artifact_file = Path(tmp) / 'discovery-artifacts.json'
            artifact_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'artifactUpdates': {
                            '00B_用户偏好.md': '# 用户偏好\n\n- 爽感优先\n',
                            '00_选题报告.md': '# 选题报告\n\n## 推荐方向\n- 规则异变都市\n',
                        },
                        'summary': 'Discovery 已形成正式候选方案',
                        'blockedReasons': [],
                        'notesForNextStage': '等待确认后进入 story-planning',
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script(
                'persist_stage_artifacts.py',
                str(project),
                'discovery',
                '--artifact-file',
                str(artifact_file),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / '00B_用户偏好.md').exists())
            self.assertTrue((project / '00_选题报告.md').exists())

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['workflow']['status'], 'awaiting_user_approval')
            self.assertEqual(state['review']['currentGate'], 'waiting_discovery_feedback')
            self.assertEqual(
                state['review']['pendingArtifactPaths'],
                ['00B_用户偏好.md', '00_选题报告.md'],
            )

    def test_persist_stage_artifacts_rejects_out_of_scope_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            artifact_file = Path(tmp) / 'bad-artifacts.json'
            artifact_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'artifactUpdates': {
                            '07_终审报告.md': '# 非法写入\n',
                        },
                        'summary': '非法',
                        'blockedReasons': [],
                        'notesForNextStage': '',
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script(
                'persist_stage_artifacts.py',
                str(project),
                'discovery',
                '--artifact-file',
                str(artifact_file),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('out-of-scope artifact for discovery: 07_终审报告.md', result.stderr + result.stdout)

    def test_persist_stage_artifacts_supports_drafting_opening_substage(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            artifact_file = Path(tmp) / 'opening-artifacts.json'
            artifact_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'artifactUpdates': {
                            '04A_开篇设计.md': '# 开篇设计\n\n## 前三章任务\n- 第1章点火\n',
                        },
                        'summary': 'Opening Gate 包已成型',
                        'blockedReasons': [],
                        'notesForNextStage': '等待确认 opening gate',
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': 'opening-review',
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'producing_artifact',
                    },
                    'review': {'pendingArtifactPaths': [], 'brainstormActive': False, 'activeBranches': []},
                },
            )

            result = run_script(
                'persist_stage_artifacts.py',
                str(project),
                'drafting',
                '--substage',
                'opening-review',
                '--artifact-file',
                str(artifact_file),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / '04A_开篇设计.md').exists())

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['review']['currentGate'], 'waiting_opening_feedback')
            self.assertEqual(state['review']['pendingArtifactPaths'], ['04A_开篇设计.md'])
