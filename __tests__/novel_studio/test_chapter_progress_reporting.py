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


class ChapterProgressReportingTest(unittest.TestCase):
    def load_script_module(self, name: str):
        scripts_path = str(SCRIPTS)
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        return importlib.import_module(name)

    def test_default_batch_adds_chapter_progress_fields(self):
        revision_utils = self.load_script_module('revision_utils')

        batch = revision_utils.default_batch()

        self.assertEqual(batch['chapterTasks'], [])
        self.assertEqual(batch['pendingProgressItems'], [])

    def test_extract_chapter_labels_from_plan(self):
        chapter_progress_utils = self.load_script_module('chapter_progress_utils')
        plan_text = (
            '## 逐章规划\n'
            '### 第1章\n'
            '- 建立主角处境\n'
            '### 第2章 夜巡\n'
            '- 发现异常规则\n'
            '### 第1章\n'
            '- 重复条目应去重\n'
            '#### 第3章\n'
            '- 不应匹配四级标题\n'
            '### 旁支说明\n'
            '- 不应匹配非章节标题\n'
            '### 第10章 终局预热\n'
        )

        labels = chapter_progress_utils.extract_chapter_labels_from_plan(plan_text)

        self.assertEqual(labels, ['第1章', '第2章', '第10章'])

    def test_update_project_state_initializes_chapter_tasks_when_plan_is_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text(
                '## 逐章规划\n'
                '### 第1章\n'
                '- 本章目标：建立主角处境\n'
                '### 第2章 夜巡\n'
                '- 本章目标：让危险升级\n',
                encoding='utf-8',
            )

            result = run_script(
                'update_project_state.py',
                str(project),
                'batch.chapterPlanApproved',
                'true',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['batch']['chapterPlanApproved'])
            self.assertTrue(state['batch']['chapterPlanExists'])
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
            self.assertEqual(state['batch']['pendingProgressItems'], [])

    def test_normalize_state_hydrates_legacy_chapter_tasks(self):
        revision_utils = self.load_script_module('revision_utils')

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()

            state = revision_utils.normalize_state(
                {
                    'project': {'title': project.name, 'rootPath': str(project)},
                    'batch': {
                        'chapterTasks': [{'label': '第1章'}],
                    },
                },
                project,
            )

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
                    }
                ],
            )

    def test_update_project_state_preserves_progress_when_approved_plan_file_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '05_本轮章节规划.md').write_text('', encoding='utf-8')
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'batch': {
                            'chapterPlanApproved': False,
                            'chapterTasks': [
                                {
                                    'chapterLabel': '第1章',
                                    'manuscriptPath': None,
                                    'phase': 'drafting',
                                    'phaseStatus': 'in_progress',
                                    'lastSummary': 'stale summary',
                                    'blockers': ['旧阻塞'],
                                    'updatedAt': '2026-03-28T00:00:00Z',
                                }
                            ],
                            'pendingProgressItems': ['stale item'],
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script(
                'update_project_state.py',
                str(project),
                'batch.chapterPlanApproved',
                'true',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['batch']['chapterPlanApproved'])
            self.assertFalse(state['batch']['chapterPlanExists'])
            self.assertEqual(state['batch']['chapterTasks'][0]['chapterLabel'], '第1章')
            self.assertEqual(state['batch']['chapterTasks'][0]['phaseStatus'], 'in_progress')
            self.assertEqual(state['batch']['pendingProgressItems'], ['stale item'])

    def test_update_project_state_preserves_progress_when_approved_plan_file_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'batch': {
                            'chapterPlanApproved': False,
                            'chapterPlanExists': True,
                            'chapterTasks': [
                                {
                                    'chapterLabel': '第1章',
                                    'manuscriptPath': None,
                                    'phase': 'drafting',
                                    'phaseStatus': 'in_progress',
                                    'lastSummary': 'stale summary',
                                    'blockers': ['旧阻塞'],
                                    'updatedAt': '2026-03-28T00:00:00Z',
                                }
                            ],
                            'pendingProgressItems': ['stale item'],
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script(
                'update_project_state.py',
                str(project),
                'batch.chapterPlanApproved',
                'true',
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['batch']['chapterPlanApproved'])
            self.assertFalse(state['batch']['chapterPlanExists'])
            self.assertEqual(state['batch']['chapterTasks'][0]['chapterLabel'], '第1章')
            self.assertEqual(state['batch']['chapterTasks'][0]['phaseStatus'], 'in_progress')
            self.assertEqual(state['batch']['pendingProgressItems'], ['stale item'])

    def test_build_progress_report_collapses_same_chapter_to_latest_state(self):
        chapter_progress_utils = self.load_script_module('chapter_progress_utils')

        payload = chapter_progress_utils.build_progress_report(
            [
                {
                    'eventId': 'e1',
                    'chapterLabel': '第1章',
                    'phase': 'drafting',
                    'phaseStatus': 'in_progress',
                    'summary': '第1章初稿中',
                    'blockers': [],
                    'createdAt': '2026-03-28T10:00:00Z',
                    'reportedAt': None,
                },
                {
                    'eventId': 'e2',
                    'chapterLabel': '第1章',
                    'phase': 'drafting',
                    'phaseStatus': 'awaiting_user_review',
                    'summary': '第1章初稿待审核',
                    'blockers': [],
                    'createdAt': '2026-03-28T10:01:00Z',
                    'reportedAt': None,
                },
                {
                    'eventId': 'e3',
                    'chapterLabel': '第2章',
                    'phase': 'polishing',
                    'phaseStatus': 'in_progress',
                    'summary': '第2章润色中',
                    'blockers': [],
                    'createdAt': '2026-03-28T10:02:00Z',
                    'reportedAt': None,
                },
            ]
        )

        self.assertEqual(payload['eventIds'], ['e2', 'e3'])
        self.assertEqual(payload['summary'], '第1章初稿待审核；第2章润色中')

    def test_chapter_progress_report_ack_marks_events_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': project.name, 'rootPath': str(project)},
                        'workflow': {'currentStage': 'drafting', 'status': 'in_progress'},
                        'batch': {
                            'pendingProgressItems': [
                                {
                                    'eventId': 'e2',
                                    'chapterLabel': '第1章',
                                    'phase': 'drafting',
                                    'phaseStatus': 'awaiting_user_review',
                                    'summary': '第1章初稿待审核',
                                    'blockers': [],
                                    'createdAt': '2026-03-28T10:01:00Z',
                                    'reportedAt': None,
                                }
                            ]
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script('chapter_progress_report.py', str(project), '--ack', 'e2')

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertIsNotNone(state['batch']['pendingProgressItems'][0]['reportedAt'])


if __name__ == '__main__':
    unittest.main()
