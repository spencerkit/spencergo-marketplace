import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / 'skills/novel-studio/scripts'


def run_script(name, *args):
    cmd = ['python3', str(SCRIPTS / name), *args]
    return subprocess.run(cmd, text=True, capture_output=True)


class NovelStudioAutopilotWorkflowTest(unittest.TestCase):
    def load_script_module(self, name: str):
        scripts_path = str(SCRIPTS)
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        return importlib.import_module(name)

    def write_state(self, project: Path, payload: dict) -> None:
        (project / '.novel-state.json').write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

    def test_load_state_adds_default_autopilot_fields(self):
        revision_utils = self.load_script_module('revision_utils')

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'workflow': {'currentStage': 'drafting'},
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            state = revision_utils.load_state(project)

            self.assertEqual(
                state['autoPilot'],
                {
                    'active': False,
                    'goalChapter': None,
                    'goalCondition': 'proofreading_completed',
                    'startedAt': None,
                    'startedBy': None,
                    'lastProgressAt': None,
                    'lastProgressSummary': None,
                    'stopReason': None,
                    'stoppedAt': None,
                    'awaitingManualResume': False,
                },
            )

    def test_load_project_state_hydrates_default_autopilot_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'workflow': {'currentStage': 'drafting'},
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script('load_project_state.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(
                state['autoPilot'],
                {
                    'active': False,
                    'goalChapter': None,
                    'goalCondition': 'proofreading_completed',
                    'startedAt': None,
                    'startedBy': None,
                    'lastProgressAt': None,
                    'lastProgressSummary': None,
                    'stopReason': None,
                    'stoppedAt': None,
                    'awaitingManualResume': False,
                },
            )

    def test_load_project_state_reconstructs_default_autopilot_fields_when_state_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            manuscript = project / 'manuscript'
            manuscript.mkdir()
            (manuscript / 'chapter-01.md').write_text('# 第一章\n\n正文', encoding='utf-8')

            result = run_script('load_project_state.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(
                state['autoPilot'],
                {
                    'active': False,
                    'goalChapter': None,
                    'goalCondition': 'proofreading_completed',
                    'startedAt': None,
                    'startedBy': None,
                    'lastProgressAt': None,
                    'lastProgressSummary': None,
                    'stopReason': None,
                    'stoppedAt': None,
                    'awaitingManualResume': False,
                },
            )

    def test_load_project_state_normalizes_legacy_autopilot_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'workflow': {'currentStage': 'drafting'},
                        'autoPilot': {
                            'active': 'false',
                            'goalChapter': 10,
                            'awaitingManualResume': 'true',
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script('load_project_state.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertFalse(state['autoPilot']['active'])
            self.assertEqual(state['autoPilot']['goalChapter'], '第10章')
            self.assertTrue(state['autoPilot']['awaitingManualResume'])

    def test_load_state_normalizes_non_dict_autopilot_to_defaults(self):
        revision_utils = self.load_script_module('revision_utils')

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()

            state = revision_utils.normalize_state(
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'autoPilot': 'broken',
                },
                project,
            )

            self.assertEqual(state['autoPilot']['goalChapter'], None)
            self.assertFalse(state['autoPilot']['active'])
            self.assertFalse(state['autoPilot']['awaitingManualResume'])

    def test_load_state_preserves_approved_chapter_progress_when_current_plan_missing(self):
        revision_utils = self.load_script_module('revision_utils')

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting'},
                    'batch': {
                        'active': True,
                        'chapterPlanApproved': True,
                        'chapterTasks': [
                            {
                                'chapterLabel': '第1章',
                                'manuscriptPath': 'manuscript/第1章.md',
                                'phase': 'proofreading',
                                'phaseStatus': 'completed',
                                'lastSummary': '第1章已完成',
                                'blockers': [],
                                'updatedAt': '2026-03-28T00:00:00Z',
                            }
                        ],
                        'pendingProgressItems': [
                            {
                                'eventId': 'progress-1',
                                'chapterLabel': '第1章',
                                'phase': 'proofreading',
                                'phaseStatus': 'completed',
                                'summary': '第1章已完成',
                                'blockers': [],
                                'createdAt': '2026-03-28T00:00:00Z',
                                'reportedAt': None,
                            }
                        ],
                    },
                },
            )

            state = revision_utils.load_state(project)

            self.assertTrue(state['batch']['chapterPlanApproved'])
            self.assertFalse(state['batch']['chapterPlanExists'])
            self.assertEqual(state['batch']['chapterTasks'][0]['chapterLabel'], '第1章')
            self.assertEqual(state['batch']['chapterTasks'][0]['phaseStatus'], 'completed')
            self.assertEqual(state['batch']['pendingProgressItems'][0]['eventId'], 'progress-1')

    def test_load_state_preserves_approved_chapter_progress_when_current_plan_is_malformed(self):
        revision_utils = self.load_script_module('revision_utils')

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text(
                '## 逐章规划\n'
                '- 只有说明，没有任何三级章节标题\n',
                encoding='utf-8',
            )
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting'},
                    'batch': {
                        'active': True,
                        'chapterPlanApproved': True,
                        'chapterTasks': [
                            {
                                'chapterLabel': '第2章',
                                'manuscriptPath': 'manuscript/第2章.md',
                                'phase': 'polishing',
                                'phaseStatus': 'in_progress',
                                'lastSummary': '第2章润色中',
                                'blockers': [],
                                'updatedAt': '2026-03-28T00:00:00Z',
                            }
                        ],
                        'pendingProgressItems': [
                            {
                                'eventId': 'progress-2',
                                'chapterLabel': '第2章',
                                'phase': 'polishing',
                                'phaseStatus': 'in_progress',
                                'summary': '第2章润色中',
                                'blockers': [],
                                'createdAt': '2026-03-28T00:00:00Z',
                                'reportedAt': None,
                            }
                        ],
                    },
                },
            )

            state = revision_utils.load_state(project)

            self.assertTrue(state['batch']['chapterPlanApproved'])
            self.assertTrue(state['batch']['chapterPlanExists'])
            self.assertEqual(state['batch']['chapterTasks'][0]['chapterLabel'], '第2章')
            self.assertEqual(state['batch']['chapterTasks'][0]['phaseStatus'], 'in_progress')
            self.assertEqual(state['batch']['pendingProgressItems'][0]['eventId'], 'progress-2')

    def test_status_brief_shows_stopped_autopilot_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'workflow': {
                            'currentStage': 'drafting',
                            'currentSubstage': None,
                            'lastCompletedStage': None,
                            'nextStage': 'drafting',
                            'status': 'in_progress',
                        },
                        'approvals': {},
                        'artifacts': {},
                        'batch': {},
                        'review': {},
                        'revision': {},
                        'autoPilot': {
                            'active': False,
                            'goalChapter': '第10章',
                            'goalCondition': 'proofreading_completed',
                            'startedAt': None,
                            'startedBy': None,
                            'lastProgressAt': '2026-03-29T10:00:00Z',
                            'lastProgressSummary': '已完成第9章校对',
                            'stopReason': '等待人工确认本轮结尾力度',
                            'stoppedAt': '2026-03-29T10:05:00Z',
                            'awaitingManualResume': True,
                        },
                        'blockingIssues': [],
                        'notes': {},
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('自动流程：已停止', result.stdout)
            self.assertIn('自动目标：第10章结束', result.stdout)
            self.assertIn('自动流程最近进度：已完成第9章校对', result.stdout)
            self.assertIn('自动流程停止原因：等待人工确认本轮结尾力度', result.stdout)

    def test_load_project_state_normalizes_terminal_goal_text_to_chapter_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'workflow': {
                            'currentStage': 'drafting',
                            'currentSubstage': None,
                            'lastCompletedStage': None,
                            'nextStage': 'drafting',
                            'status': 'in_progress',
                        },
                        'autoPilot': {
                            'goalChapter': '第10章结束',
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script('load_project_state.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['autoPilot']['goalChapter'], '第10章')

    def test_status_brief_goal_rendering_uses_normalized_chapter_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'workflow': {
                            'currentStage': 'drafting',
                            'currentSubstage': None,
                            'lastCompletedStage': None,
                            'nextStage': 'drafting',
                            'status': 'in_progress',
                        },
                        'autoPilot': {
                            'goalChapter': '第10章结束',
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('自动目标：第10章结束', result.stdout)
            self.assertNotIn('自动目标：第10章结束结束', result.stdout)

    def test_status_brief_shows_autopilot_fallback_values_when_unset(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'workflow': {
                            'currentStage': 'story-planning',
                            'currentSubstage': None,
                            'lastCompletedStage': None,
                            'nextStage': 'story-planning',
                            'status': 'collecting_inputs',
                        },
                        'review': {},
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('自动流程：未开启', result.stdout)
            self.assertIn('自动目标：无', result.stdout)
            self.assertIn('自动流程最近进度：无', result.stdout)
            self.assertIn('自动流程停止原因：无', result.stdout)

    def test_status_full_shows_autopilot_fallback_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'workflow': {
                            'currentStage': 'story-planning',
                            'currentSubstage': None,
                            'lastCompletedStage': None,
                            'nextStage': 'story-planning',
                            'status': 'collecting_inputs',
                        },
                        'review': {},
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script('novel_project_status.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('自动流程：未开启', result.stdout)
            self.assertIn('自动目标：无', result.stdout)
            self.assertIn('自动流程最近进度：无', result.stdout)
            self.assertIn('自动流程停止原因：无', result.stdout)

    def test_update_autopilot_state_activates_on_explicit_goal_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '后续你来主控，继续到第10章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'activated')
            self.assertTrue(payload['savedState']['autoPilot']['active'])
            self.assertEqual(payload['savedState']['autoPilot']['goalChapter'], '第10章')

    def test_update_autopilot_state_normalizes_chinese_numeral_goal_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '后续你来主控，继续到第十章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'activated')
            self.assertEqual(payload['savedState']['autoPilot']['goalChapter'], '第10章')

    def test_update_autopilot_state_ignores_vague_continue_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '继续',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'noop')
            self.assertFalse(payload['savedState']['autoPilot']['active'])

    def test_update_autopilot_state_does_not_activate_on_negative_or_self_owned_goal_messages(self):
        cases = (
            '我来主控，不用你继续到第10章结束',
            '不用你主控，继续到第10章结束我自己写',
            '主控权先不给你，继续到第10章结束再说',
        )

        for message in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmp:
                    project = Path(tmp) / '测试小说'
                    project.mkdir()
                    self.write_state(
                        project,
                        {
                            'project': {'title': project.name, 'rootPath': str(project)},
                            'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                        },
                    )

                    result = run_script(
                        'update_autopilot_state.py',
                        str(project),
                        '--message',
                        message,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload['action'], 'noop')
                    self.assertFalse(payload['savedState']['autoPilot']['active'])
                    self.assertIsNone(payload['savedState']['autoPilot']['goalChapter'])

    def test_update_autopilot_state_does_not_activate_on_negative_continue_variant(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '你不用继续到第10章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'noop')
            self.assertFalse(payload['savedState']['autoPilot']['active'])
            self.assertIsNone(payload['savedState']['autoPilot']['goalChapter'])

    def test_update_autopilot_state_does_not_activate_on_terminal_chapter_editing_topics(self):
        cases = (
            '后续你来主控，第10章结束得再有力一点',
            '你来主控，第10章结束部分重写一下',
        )

        for message in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmp:
                    project = Path(tmp) / '测试小说'
                    project.mkdir()
                    self.write_state(
                        project,
                        {
                            'project': {'title': project.name, 'rootPath': str(project)},
                            'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                        },
                    )

                    result = run_script(
                        'update_autopilot_state.py',
                        str(project),
                        '--message',
                        message,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload['action'], 'noop')
                    self.assertFalse(payload['savedState']['autoPilot']['active'])
                    self.assertIsNone(payload['savedState']['autoPilot']['goalChapter'])

    def test_update_autopilot_state_does_not_activate_on_self_owned_bounded_commands(self):
        cases = (
            '我继续到第10章结束',
            '我继续写到第10章结束',
            '我来继续到第10章结束',
        )

        for message in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmp:
                    project = Path(tmp) / '测试小说'
                    project.mkdir()
                    self.write_state(
                        project,
                        {
                            'project': {'title': project.name, 'rootPath': str(project)},
                            'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                        },
                    )

                    result = run_script(
                        'update_autopilot_state.py',
                        str(project),
                        '--message',
                        message,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload['action'], 'noop')
                    self.assertFalse(payload['savedState']['autoPilot']['active'])
                    self.assertIsNone(payload['savedState']['autoPilot']['goalChapter'])

    def test_update_autopilot_state_quoted_negation_reference_does_not_block_activation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '把“不给你主控”那句删掉，后续你来主控，继续到第10章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'activated')
            self.assertTrue(payload['savedState']['autoPilot']['active'])
            self.assertEqual(payload['savedState']['autoPilot']['goalChapter'], '第10章')

    def test_update_autopilot_state_colon_labeled_directive_activates_when_inactive(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '后续安排：继续到第10章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'activated')
            self.assertTrue(payload['savedState']['autoPilot']['active'])
            self.assertEqual(payload['savedState']['autoPilot']['goalChapter'], '第10章')

    def test_update_autopilot_state_colon_labeled_supersede_updates_active_goal(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T10:00:00Z',
                        'startedBy': '后续你来主控，继续到第10章结束',
                        'lastProgressAt': '2026-03-29T10:30:00Z',
                        'lastProgressSummary': '已完成第9章校对',
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '第7章不要这么写：改成继续到第12章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'superseded')
            self.assertTrue(payload['savedState']['autoPilot']['active'])
            self.assertEqual(payload['savedState']['autoPilot']['goalChapter'], '第12章')

    def test_update_autopilot_state_assistant_directed_replacement_only_phrase_does_not_activate_when_inactive(self):
        cases = (
            '后续你来主控，改成继续到第12章结束',
            '交给你，改为继续到第12章结束',
        )

        for message in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmp:
                    project = Path(tmp) / '测试小说'
                    project.mkdir()
                    self.write_state(
                        project,
                        {
                            'project': {'title': project.name, 'rootPath': str(project)},
                            'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                        },
                    )

                    result = run_script(
                        'update_autopilot_state.py',
                        str(project),
                        '--message',
                        message,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload['action'], 'noop')
                    self.assertFalse(payload['savedState']['autoPilot']['active'])
                    self.assertIsNone(payload['savedState']['autoPilot']['goalChapter'])

    def test_update_autopilot_state_quoted_positive_goal_reference_does_not_activate_when_inactive(self):
        cases = (
            '把“后续你来主控，继续到第12章结束”这句话删掉',
            '把“继续到第12章结束”这句话删掉',
        )

        for message in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmp:
                    project = Path(tmp) / '测试小说'
                    project.mkdir()
                    self.write_state(
                        project,
                        {
                            'project': {'title': project.name, 'rootPath': str(project)},
                            'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                        },
                    )

                    result = run_script(
                        'update_autopilot_state.py',
                        str(project),
                        '--message',
                        message,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload['action'], 'noop')
                    self.assertFalse(payload['savedState']['autoPilot']['active'])
                    self.assertIsNone(payload['savedState']['autoPilot']['goalChapter'])

    def test_update_autopilot_state_unquoted_reference_goal_mentions_do_not_activate_when_inactive(self):
        cases = (
            '把这句删掉：继续到第12章结束',
            '这里的文案是继续到第12章结束，不要照抄',
        )

        for message in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmp:
                    project = Path(tmp) / '测试小说'
                    project.mkdir()
                    self.write_state(
                        project,
                        {
                            'project': {'title': project.name, 'rootPath': str(project)},
                            'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                        },
                    )

                    result = run_script(
                        'update_autopilot_state.py',
                        str(project),
                        '--message',
                        message,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload['action'], 'noop')
                    self.assertFalse(payload['savedState']['autoPilot']['active'])
                    self.assertIsNone(payload['savedState']['autoPilot']['goalChapter'])

    def test_update_autopilot_state_comma_separated_reference_goal_does_not_activate_when_inactive(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '把这句删掉，继续到第12章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'noop')
            self.assertFalse(payload['savedState']['autoPilot']['active'])
            self.assertIsNone(payload['savedState']['autoPilot']['goalChapter'])

    def test_update_autopilot_state_non_direct_bounded_phrases_do_not_activate_when_inactive(self):
        cases = (
            '我自己继续到第10章结束',
            '我会继续到第10章结束',
            '不要继续到第10章结束',
            '先别继续到第10章结束',
            '文档里写着继续到第12章结束',
            '注释写着继续到第12章结束',
            '原文是继续到第12章结束',
        )

        for message in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmp:
                    project = Path(tmp) / '测试小说'
                    project.mkdir()
                    self.write_state(
                        project,
                        {
                            'project': {'title': project.name, 'rootPath': str(project)},
                            'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                        },
                    )

                    result = run_script(
                        'update_autopilot_state.py',
                        str(project),
                        '--message',
                        message,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload['action'], 'noop')
                    self.assertFalse(payload['savedState']['autoPilot']['active'])
                    self.assertIsNone(payload['savedState']['autoPilot']['goalChapter'])

    def test_update_autopilot_state_quoted_positive_goal_reference_does_not_supersede_active_autopilot(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T10:00:00Z',
                        'startedBy': '后续你来主控，继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '把“继续到第12章结束”这句话删掉',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'stopped')
            self.assertFalse(payload['savedState']['autoPilot']['active'])
            self.assertEqual(payload['savedState']['autoPilot']['stopReason'], 'user_interruption')

    def test_update_autopilot_state_comma_separated_reference_goal_does_not_supersede_active_autopilot(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T10:00:00Z',
                        'startedBy': '后续你来主控，继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '把这句删掉，改成继续到第12章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'stopped')
            self.assertFalse(payload['savedState']['autoPilot']['active'])
            self.assertEqual(payload['savedState']['autoPilot']['stopReason'], 'user_interruption')

    def test_update_autopilot_state_plain_bounded_goal_activates_when_inactive(self):
        cases = (
            ('继续到第10章结束', '第10章'),
            ('继续写到第10章结束', '第10章'),
            ('直到第10章结束', '第10章'),
        )

        for message, goal in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmp:
                    project = Path(tmp) / '测试小说'
                    project.mkdir()
                    self.write_state(
                        project,
                        {
                            'project': {'title': project.name, 'rootPath': str(project)},
                            'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                        },
                    )

                    result = run_script(
                        'update_autopilot_state.py',
                        str(project),
                        '--message',
                        message,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload['action'], 'activated')
                    self.assertTrue(payload['savedState']['autoPilot']['active'])
                    self.assertEqual(payload['savedState']['autoPilot']['goalChapter'], goal)

    def test_update_autopilot_state_inactive_mixed_order_persists_decision_goal(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '改成继续到第12章结束，继续到第10章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'activated')
            self.assertTrue(payload['savedState']['autoPilot']['active'])
            self.assertEqual(payload['savedState']['autoPilot']['goalChapter'], '第10章')

    def test_update_autopilot_state_ack_does_not_interrupt_active_autopilot(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T10:00:00Z',
                        'startedBy': '后续你来主控，继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '好',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'noop')
            self.assertTrue(payload['savedState']['autoPilot']['active'])

    def test_update_autopilot_state_ack_variants_do_not_interrupt_active_autopilot(self):
        cases = ('好的，收到', '收到，继续', '继续吧', '好的收到', '好……', '收到……', '继续……', '好的...')

        for message in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmp:
                    project = Path(tmp) / '测试小说'
                    project.mkdir()
                    self.write_state(
                        project,
                        {
                            'project': {'title': project.name, 'rootPath': str(project)},
                            'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                            'autoPilot': {
                                'active': True,
                                'goalChapter': '第10章',
                                'goalCondition': 'proofreading_completed',
                                'startedAt': '2026-03-29T10:00:00Z',
                                'startedBy': '后续你来主控，继续到第10章结束',
                                'lastProgressAt': None,
                                'lastProgressSummary': None,
                                'stopReason': None,
                                'stoppedAt': None,
                                'awaitingManualResume': False,
                            },
                        },
                    )

                    result = run_script(
                        'update_autopilot_state.py',
                        str(project),
                        '--message',
                        message,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload['action'], 'noop')
                    self.assertTrue(payload['savedState']['autoPilot']['active'])
                    self.assertIsNone(payload['savedState']['autoPilot']['stopReason'])

    def test_update_autopilot_state_empty_or_punctuation_only_input_does_not_interrupt_active_autopilot(self):
        cases = ('', '……')

        for message in cases:
            with self.subTest(message=message):
                with tempfile.TemporaryDirectory() as tmp:
                    project = Path(tmp) / '测试小说'
                    project.mkdir()
                    self.write_state(
                        project,
                        {
                            'project': {'title': project.name, 'rootPath': str(project)},
                            'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                            'autoPilot': {
                                'active': True,
                                'goalChapter': '第10章',
                                'goalCondition': 'proofreading_completed',
                                'startedAt': '2026-03-29T10:00:00Z',
                                'startedBy': '后续你来主控，继续到第10章结束',
                                'lastProgressAt': None,
                                'lastProgressSummary': None,
                                'stopReason': None,
                                'stoppedAt': None,
                                'awaitingManualResume': False,
                            },
                        },
                    )

                    result = run_script(
                        'update_autopilot_state.py',
                        str(project),
                        '--message',
                        message,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload['action'], 'noop')
                    self.assertTrue(payload['savedState']['autoPilot']['active'])
                    self.assertIsNone(payload['savedState']['autoPilot']['stopReason'])

    def test_update_autopilot_state_interrupts_on_substantive_user_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T10:00:00Z',
                        'startedBy': '后续你来主控，继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '第7章不要这么写，先停一下',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'stopped')
            self.assertFalse(payload['savedState']['autoPilot']['active'])
            self.assertEqual(payload['savedState']['autoPilot']['stopReason'], 'user_interruption')

    def test_update_autopilot_state_supersedes_active_goal_with_new_explicit_goal(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T10:00:00Z',
                        'startedBy': '后续你来主控，继续到第10章结束',
                        'lastProgressAt': '2026-03-29T10:30:00Z',
                        'lastProgressSummary': '已完成第9章校对',
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '改成继续到第12章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'superseded')
            self.assertTrue(payload['savedState']['autoPilot']['active'])
            self.assertEqual(payload['savedState']['autoPilot']['goalChapter'], '第12章')
            self.assertEqual(payload['previousStopReason'], 'superseded_by_new_user_goal')
            self.assertIsNone(payload['savedState']['autoPilot']['lastProgressAt'])
            self.assertIsNone(payload['savedState']['autoPilot']['lastProgressSummary'])

    def test_update_autopilot_state_replacement_only_phrase_does_not_activate_when_inactive(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '改成继续到第12章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'noop')
            self.assertFalse(payload['savedState']['autoPilot']['active'])
            self.assertIsNone(payload['savedState']['autoPilot']['goalChapter'])

    def test_update_autopilot_state_supersede_prefers_terminal_goal_in_mixed_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {'currentStage': 'drafting', 'status': 'awaiting_user_approval'},
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T10:00:00Z',
                        'startedBy': '后续你来主控，继续到第10章结束',
                        'lastProgressAt': '2026-03-29T10:30:00Z',
                        'lastProgressSummary': '已完成第9章校对',
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script(
                'update_autopilot_state.py',
                str(project),
                '--message',
                '第7章不要这么写，改成继续到第12章结束',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'superseded')
            self.assertEqual(payload['savedState']['autoPilot']['goalChapter'], '第12章')

    def test_approve_stage_gate_stops_autopilot_with_goal_reached_after_goal_chapter_proofreading(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text('### 第10章\n- 收束当前卷冲突\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'proofreading',
                        'currentSubstage': None,
                        'lastCompletedStage': 'polishing',
                        'nextStage': 'final-review',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'draftingApproved': True,
                        'polishingApproved': True,
                        'proofreadingApproved': False,
                    },
                    'review': {
                        'currentGate': 'waiting_proofreading_feedback',
                        'pendingArtifactPaths': ['05A_本轮校对报告.md'],
                    },
                    'batch': {
                        'active': True,
                        'chapterPlanApproved': True,
                        'proofreadingComplete': True,
                        'chapterTasks': [
                            {
                                'chapterLabel': '第10章',
                                'manuscriptPath': 'manuscript/第10章_收束.md',
                                'phase': 'proofreading',
                                'phaseStatus': 'awaiting_user_review',
                                'lastSummary': '第10章审核中',
                                'blockers': [],
                                'updatedAt': '2026-03-29T10:00:00Z',
                            }
                        ],
                        'pendingProgressItems': [],
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': '2026-03-29T10:00:00Z',
                        'lastProgressSummary': '第10章审核中',
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('approve_stage_gate.py', str(project), 'waiting_proofreading_feedback')

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertFalse(state['autoPilot']['active'])
            self.assertEqual(state['autoPilot']['stopReason'], 'goal_reached')
            self.assertEqual(state['autoPilot']['lastProgressSummary'], '第10章已完成')
            self.assertTrue(state['autoPilot']['awaitingManualResume'])
            self.assertIsNotNone(state['autoPilot']['stoppedAt'])

    def test_approve_stage_gate_does_not_mark_goal_reached_for_proofreading_needs_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text('### 第10章\n- 收束当前卷冲突\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'proofreading',
                        'currentSubstage': None,
                        'lastCompletedStage': 'polishing',
                        'nextStage': 'final-review',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'draftingApproved': True,
                        'polishingApproved': True,
                        'proofreadingApproved': False,
                    },
                    'review': {
                        'currentGate': 'waiting_proofreading_feedback',
                        'pendingArtifactPaths': ['05A_本轮校对报告.md'],
                    },
                    'batch': {
                        'active': True,
                        'chapterPlanApproved': True,
                        'proofreadingComplete': False,
                        'chapterTasks': [
                            {
                                'chapterLabel': '第10章',
                                'manuscriptPath': 'manuscript/第10章_收束.md',
                                'phase': 'proofreading',
                                'phaseStatus': 'awaiting_user_review',
                                'lastSummary': '第10章审核中：结尾信息缺口',
                                'blockers': ['结尾信息缺口'],
                                'updatedAt': '2026-03-29T10:00:00Z',
                            }
                        ],
                        'pendingProgressItems': [],
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': '2026-03-29T10:00:00Z',
                        'lastProgressSummary': '第10章审核中：结尾信息缺口',
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('approve_stage_gate.py', str(project), 'waiting_proofreading_feedback')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('proofreading is not ready for approval', result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertFalse(state['approvals']['proofreadingApproved'])
            self.assertEqual(state['workflow']['currentStage'], 'proofreading')
            self.assertEqual(state['workflow']['nextStage'], 'final-review')
            self.assertEqual(state['workflow']['status'], 'awaiting_user_approval')
            self.assertEqual(state['review']['currentGate'], 'waiting_proofreading_feedback')
            self.assertTrue(state['autoPilot']['active'])
            self.assertIsNone(state['autoPilot']['stopReason'])
            self.assertEqual(state['autoPilot']['lastProgressSummary'], '第10章审核中：结尾信息缺口')
            self.assertFalse(state['autoPilot']['awaitingManualResume'])
            self.assertIsNone(state['autoPilot']['stoppedAt'])
            task = state['batch']['chapterTasks'][0]
            self.assertEqual(task['phase'], 'proofreading')
            self.assertEqual(task['phaseStatus'], 'awaiting_user_review')
            self.assertEqual(task['blockers'], ['结尾信息缺口'])
            self.assertEqual(task['lastSummary'], '第10章审核中：结尾信息缺口')
            self.assertEqual(state['batch']['pendingProgressItems'], [])

    def test_approve_stage_gate_treats_string_false_proofreading_complete_as_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text('### 第10章\n- 收束当前卷冲突\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'proofreading',
                        'currentSubstage': None,
                        'lastCompletedStage': 'polishing',
                        'nextStage': 'final-review',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'draftingApproved': True,
                        'polishingApproved': True,
                        'proofreadingApproved': False,
                    },
                    'review': {
                        'currentGate': 'waiting_proofreading_feedback',
                        'pendingArtifactPaths': ['05A_本轮校对报告.md'],
                    },
                    'batch': {
                        'active': True,
                        'chapterPlanApproved': True,
                        'proofreadingComplete': 'false',
                        'chapterTasks': [
                            {
                                'chapterLabel': '第10章',
                                'manuscriptPath': 'manuscript/第10章_收束.md',
                                'phase': 'proofreading',
                                'phaseStatus': 'awaiting_user_review',
                                'lastSummary': '第10章审核中：结尾信息缺口',
                                'blockers': ['结尾信息缺口'],
                                'updatedAt': '2026-03-29T10:00:00Z',
                            }
                        ],
                        'pendingProgressItems': [],
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': '2026-03-29T10:00:00Z',
                        'lastProgressSummary': '第10章审核中：结尾信息缺口',
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('approve_stage_gate.py', str(project), 'waiting_proofreading_feedback')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('proofreading is not ready for approval', result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertFalse(state['approvals']['proofreadingApproved'])
            self.assertEqual(state['workflow']['currentStage'], 'proofreading')
            self.assertEqual(state['workflow']['nextStage'], 'final-review')
            self.assertEqual(state['workflow']['status'], 'awaiting_user_approval')
            self.assertEqual(state['review']['currentGate'], 'waiting_proofreading_feedback')
            self.assertTrue(state['autoPilot']['active'])
            self.assertIsNone(state['autoPilot']['stopReason'])
            self.assertEqual(state['autoPilot']['lastProgressSummary'], '第10章审核中：结尾信息缺口')
            task = state['batch']['chapterTasks'][0]
            self.assertEqual(task['phase'], 'proofreading')
            self.assertEqual(task['phaseStatus'], 'awaiting_user_review')
            self.assertEqual(task['blockers'], ['结尾信息缺口'])
            self.assertEqual(state['batch']['pendingProgressItems'], [])

    def test_advance_autopilot_confirms_scope_when_needed(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': None,
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'collecting_inputs',
                    },
                    'approvals': {
                        'characterApproved': True,
                        'openingApproved': True,
                    },
                    'review': {
                        'currentGate': None,
                        'pendingArtifactPaths': [],
                    },
                    'batch': {
                        'active': True,
                        'scopeConfirmed': False,
                        'chapterPlanApproved': False,
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('advance_autopilot.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'confirm_scope')
            state = payload['savedState']
            self.assertTrue(state['batch']['scopeConfirmed'])
            self.assertFalse(state['batch']['chapterPlanApproved'])
            self.assertTrue(state['autoPilot']['active'])

    def test_advance_autopilot_confirms_chapter_plan_when_needed(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text(
                '## 逐章规划\n'
                '### 第1章\n'
                '- 建立主角处境\n'
                '### 第2章 夜巡\n'
                '- 危险升级\n',
                encoding='utf-8',
            )
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': None,
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'collecting_inputs',
                    },
                    'approvals': {
                        'characterApproved': True,
                        'openingApproved': True,
                    },
                    'review': {
                        'currentGate': None,
                        'pendingArtifactPaths': [],
                    },
                    'batch': {
                        'active': True,
                        'scopeConfirmed': True,
                        'chapterPlanApproved': False,
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('advance_autopilot.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'approve_chapter_plan')
            state = payload['savedState']
            self.assertTrue(state['batch']['scopeConfirmed'])
            self.assertTrue(state['batch']['chapterPlanApproved'])
            self.assertEqual(
                state['batch']['chapterTasks'],
                [
                    {
                        'chapterLabel': '第1章',
                        'manuscriptPath': None,
                        'phase': 'drafting',
                        'phaseStatus': 'queued',
                        'lastSummary': None,
                        'blockers': [],
                        'updatedAt': None,
                    },
                    {
                        'chapterLabel': '第2章',
                        'manuscriptPath': None,
                        'phase': 'drafting',
                        'phaseStatus': 'queued',
                        'lastSummary': None,
                        'blockers': [],
                        'updatedAt': None,
                    },
                ],
            )

    def test_advance_autopilot_approves_chapter_plan_when_state_root_path_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project = tmp_path / '测试小说'
            stale_root = tmp_path / '旧目录'
            project.mkdir()
            stale_root.mkdir()
            (project / '05_本轮章节规划.md').write_text(
                '## 逐章规划\n'
                '### 第3章\n'
                '- 新目录中的真实规划\n',
                encoding='utf-8',
            )
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(stale_root)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': None,
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'collecting_inputs',
                    },
                    'approvals': {
                        'characterApproved': True,
                        'openingApproved': True,
                    },
                    'review': {
                        'currentGate': None,
                        'pendingArtifactPaths': [],
                    },
                    'batch': {
                        'active': True,
                        'scopeConfirmed': True,
                        'chapterPlanApproved': False,
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('advance_autopilot.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'approve_chapter_plan')
            state = payload['savedState']
            self.assertEqual(state['project']['rootPath'], str(stale_root))
            self.assertTrue(state['batch']['chapterPlanApproved'])
            self.assertEqual(
                state['batch']['chapterTasks'],
                [
                    {
                        'chapterLabel': '第3章',
                        'manuscriptPath': None,
                        'phase': 'drafting',
                        'phaseStatus': 'queued',
                        'lastSummary': None,
                        'blockers': [],
                        'updatedAt': None,
                    }
                ],
            )

    def test_advance_autopilot_does_not_approve_malformed_nonempty_chapter_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text(
                '## 逐章规划\n'
                '- 这里只有说明文字，没有任何三级章节标题\n'
                '- 因此不能安全生成 chapterTasks\n',
                encoding='utf-8',
            )
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': None,
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'collecting_inputs',
                    },
                    'approvals': {
                        'characterApproved': True,
                        'openingApproved': True,
                    },
                    'review': {
                        'currentGate': None,
                        'pendingArtifactPaths': [],
                    },
                    'batch': {
                        'active': True,
                        'scopeConfirmed': True,
                        'chapterPlanApproved': False,
                        'chapterTasks': [],
                        'pendingProgressItems': [],
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('advance_autopilot.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'noop')
            self.assertEqual(payload['reason'], 'no_safe_autopilot_action')
            state = payload['savedState']
            self.assertFalse(state['batch']['chapterPlanApproved'])
            self.assertEqual(state['batch']['chapterTasks'], [])

    def test_advance_autopilot_rebuilds_stale_chapter_tasks_from_current_plan_on_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text(
                '## 逐章规划\n'
                '### 第4章\n'
                '- 新计划第一章\n'
                '### 第5章\n'
                '- 新计划第二章\n',
                encoding='utf-8',
            )
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': None,
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'collecting_inputs',
                    },
                    'approvals': {
                        'characterApproved': True,
                        'openingApproved': True,
                    },
                    'review': {
                        'currentGate': None,
                        'pendingArtifactPaths': [],
                    },
                    'batch': {
                        'active': True,
                        'scopeConfirmed': True,
                        'chapterPlanApproved': False,
                        'chapterTasks': [
                            {
                                'chapterLabel': '第1章',
                                'manuscriptPath': 'manuscript/第1章_旧稿.md',
                                'phase': 'polishing',
                                'phaseStatus': 'in_progress',
                                'lastSummary': '旧任务',
                                'blockers': ['旧阻塞'],
                                'updatedAt': '2026-03-28T00:00:00Z',
                            }
                        ],
                        'pendingProgressItems': [
                            {
                                'eventId': 'old-progress',
                                'chapterLabel': '第1章',
                                'phase': 'polishing',
                                'phaseStatus': 'in_progress',
                                'summary': '旧进度',
                                'blockers': [],
                                'createdAt': '2026-03-28T00:00:00Z',
                                'reportedAt': None,
                            }
                        ],
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('advance_autopilot.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'approve_chapter_plan')
            state = payload['savedState']
            self.assertTrue(state['batch']['chapterPlanApproved'])
            self.assertEqual(
                state['batch']['chapterTasks'],
                [
                    {
                        'chapterLabel': '第4章',
                        'manuscriptPath': None,
                        'phase': 'drafting',
                        'phaseStatus': 'queued',
                        'lastSummary': None,
                        'blockers': [],
                        'updatedAt': None,
                    },
                    {
                        'chapterLabel': '第5章',
                        'manuscriptPath': None,
                        'phase': 'drafting',
                        'phaseStatus': 'queued',
                        'lastSummary': None,
                        'blockers': [],
                        'updatedAt': None,
                    },
                ],
            )
            self.assertEqual(state['batch']['pendingProgressItems'], [])

    def test_advance_autopilot_does_not_approve_duplicate_chapter_headings(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text(
                '## 逐章规划\n'
                '### 第1章\n'
                '- 第一版内容\n'
                '### 第1章\n'
                '- 重复标题应视为无效\n',
                encoding='utf-8',
            )
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': None,
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'collecting_inputs',
                    },
                    'approvals': {
                        'characterApproved': True,
                        'openingApproved': True,
                    },
                    'review': {
                        'currentGate': None,
                        'pendingArtifactPaths': [],
                    },
                    'batch': {
                        'active': True,
                        'scopeConfirmed': True,
                        'chapterPlanApproved': False,
                        'chapterTasks': [],
                        'pendingProgressItems': [],
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('advance_autopilot.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'noop')
            self.assertEqual(payload['reason'], 'no_safe_autopilot_action')
            state = payload['savedState']
            self.assertFalse(state['batch']['chapterPlanApproved'])
            self.assertEqual(state['batch']['chapterTasks'], [])

    def test_advance_autopilot_approves_eligible_open_review_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text('### 第10章\n- 收束当前卷冲突\n', encoding='utf-8')
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': None,
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'characterApproved': True,
                        'openingApproved': True,
                        'draftingApproved': False,
                    },
                    'review': {
                        'currentGate': 'waiting_draft_feedback',
                        'pendingArtifactPaths': ['manuscript/第10章_收束.md'],
                    },
                    'batch': {
                        'active': True,
                        'scopeConfirmed': True,
                        'chapterPlanApproved': True,
                        'chapterTasks': [
                            {
                                'chapterLabel': '第10章',
                                'manuscriptPath': 'manuscript/第10章_收束.md',
                                'phase': 'drafting',
                                'phaseStatus': 'awaiting_user_review',
                                'lastSummary': '第10章初稿待审核',
                                'blockers': [],
                                'updatedAt': '2026-03-29T10:00:00Z',
                            }
                        ],
                        'pendingProgressItems': [],
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': '2026-03-29T10:00:00Z',
                        'lastProgressSummary': '第10章初稿待审核',
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('advance_autopilot.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'approve_gate')
            self.assertEqual(payload['gate'], 'waiting_draft_feedback')
            state = payload['savedState']
            self.assertTrue(state['approvals']['draftingApproved'])
            self.assertEqual(state['workflow']['currentStage'], 'polishing')
            self.assertIsNone(state['review']['currentGate'])
            task = state['batch']['chapterTasks'][0]
            self.assertEqual(task['phase'], 'polishing')
            self.assertEqual(task['phaseStatus'], 'queued')

    def test_advance_autopilot_never_approves_final_review_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'final-review',
                        'currentSubstage': None,
                        'lastCompletedStage': 'proofreading',
                        'nextStage': None,
                        'status': 'awaiting_user_approval',
                    },
                    'approvals': {
                        'proofreadingApproved': True,
                        'finalApproved': False,
                    },
                    'review': {
                        'currentGate': 'waiting_final_review_feedback',
                        'pendingArtifactPaths': ['07_终审报告.md'],
                        'finalDecision': 'pass',
                        'finalDeliveryReady': True,
                        'finalBlockingIssues': [],
                    },
                    'batch': {
                        'active': True,
                        'scopeConfirmed': True,
                        'chapterPlanApproved': True,
                        'proofreadingComplete': True,
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': '2026-03-29T10:00:00Z',
                        'lastProgressSummary': '第10章已完成',
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('advance_autopilot.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'noop')
            self.assertEqual(payload['reason'], 'final_review_manual')
            state = payload['savedState']
            self.assertEqual(state['review']['currentGate'], 'waiting_final_review_feedback')
            self.assertFalse(state['approvals']['finalApproved'])

    def test_advance_autopilot_noops_while_formal_revision_gate_is_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': None,
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'collecting_inputs',
                    },
                    'review': {
                        'currentGate': None,
                        'pendingArtifactPaths': [],
                    },
                    'revision': {
                        'active': True,
                        'currentRevisionGate': 'awaiting_revision_plan_approval',
                    },
                    'batch': {
                        'active': True,
                        'scopeConfirmed': False,
                        'chapterPlanApproved': False,
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('advance_autopilot.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'noop')
            self.assertEqual(payload['reason'], 'formal_revision_active')
            state = payload['savedState']
            self.assertFalse(state['batch']['scopeConfirmed'])
            self.assertFalse(state['batch']['chapterPlanApproved'])

    def test_advance_autopilot_noops_while_formal_revision_blocker_is_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'workflow': {
                        'currentStage': 'drafting',
                        'currentSubstage': None,
                        'lastCompletedStage': 'character-system',
                        'nextStage': 'drafting',
                        'status': 'collecting_inputs',
                    },
                    'review': {
                        'currentGate': None,
                        'pendingArtifactPaths': [],
                    },
                    'revision': {
                        'active': True,
                        'currentRevisionGate': None,
                    },
                    'blockingIssues': [
                        'Formal revision active: awaiting_revision_result_approval',
                    ],
                    'batch': {
                        'active': True,
                        'scopeConfirmed': True,
                        'chapterPlanApproved': False,
                    },
                    'autoPilot': {
                        'active': True,
                        'goalChapter': '第10章',
                        'goalCondition': 'proofreading_completed',
                        'startedAt': '2026-03-29T09:00:00Z',
                        'startedBy': '继续到第10章结束',
                        'lastProgressAt': None,
                        'lastProgressSummary': None,
                        'stopReason': None,
                        'stoppedAt': None,
                        'awaitingManualResume': False,
                    },
                },
            )

            result = run_script('advance_autopilot.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload['action'], 'noop')
            self.assertEqual(payload['reason'], 'formal_revision_active')
            state = payload['savedState']
            self.assertTrue(state['batch']['scopeConfirmed'])
            self.assertFalse(state['batch']['chapterPlanApproved'])
