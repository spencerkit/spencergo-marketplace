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


class RevisionWorkflowTest(unittest.TestCase):
    def create_revision_ready_project(self, root: Path) -> Path:
        project = root / '测试小说'
        project.mkdir()
        manuscript = project / 'manuscript'
        manuscript.mkdir()
        (manuscript / 'chapter-01.md').write_text('# 第一章\n\n正文', encoding='utf-8')
        (project / '05_前情回顾.md').write_text(
            '## 当前已推进到的位置\n'
            '- 第一卷中段\n\n'
            '## 最近一轮发生的关键事件\n'
            '- 主角得知真相\n\n'
            '## 当前未回收的伏笔 / 悬念\n'
            '- 黑箱来源未揭示\n\n'
            '## 下一轮写作必须记住的点\n'
            '- 保持人物关系连续\n',
            encoding='utf-8',
        )
        return project

    def test_record_feedback_creates_state_and_revision_doc(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            result = run_script(
                'record_revision_feedback.py',
                str(project),
                'character_feedback',
                'override',
                '第3章主角性格发虚',
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['revision']['active'])
            self.assertEqual(state['revision']['currentRevisionGate'], 'awaiting_revision_scope_confirmation')
            self.assertEqual(state['review']['lastUserFeedbackSummary'], '第3章主角性格发虚')

            revision_doc = (project / '06_反馈与修订.md').read_text(encoding='utf-8')
            self.assertIn('## 当前正式修订', revision_doc)
            self.assertIn('第3章主角性格发虚', revision_doc)
            self.assertIn('当前修订 gate：awaiting_revision_scope_confirmation', revision_doc)

    def test_second_active_revision_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            first = run_script(
                'record_revision_feedback.py',
                str(project),
                'plot_feedback',
                'add_on',
                '补强第1章钩子',
            )
            self.assertEqual(first.returncode, 0, first.stderr)

            second = run_script(
                'record_revision_feedback.py',
                str(project),
                'style_feedback',
                'add_on',
                '语气还不够稳',
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn('active revision', second.stderr + second.stdout)

    def test_record_feedback_resets_old_transient_revision_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            state = {
                'project': {'title': '测试小说', 'rootPath': str(project)},
                'workflow': {'currentStage': None, 'currentSubstage': None, 'lastCompletedStage': None, 'nextStage': None, 'status': 'in_progress'},
                'approvals': {},
                'artifacts': {},
                'batch': {},
                'review': {},
                'revision': {
                    'active': False,
                    'feedbackType': 'old',
                    'feedbackSummary': 'old summary',
                    'affectedStages': ['drafting'],
                    'affectedFiles': ['old.md'],
                    'overrideMode': 'add_on',
                    'scopeSummary': 'old scope',
                    'conflictSummary': 'old conflict',
                    'revisionPlanSummary': 'old plan',
                    'resultSummary': 'old result',
                    'currentRevisionGate': None,
                    'awaitingUserApproval': False,
                    'lastClosedRevision': None,
                },
                'blockingIssues': [],
                'notes': {},
            }
            (project / '.novel-state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')

            result = run_script(
                'record_revision_feedback.py',
                str(project),
                'character_feedback',
                'override',
                '新的正式反馈',
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            updated = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(updated['revision']['affectedStages'], [])
            self.assertEqual(updated['revision']['affectedFiles'], [])
            self.assertIsNone(updated['revision']['scopeSummary'])
            self.assertIsNone(updated['revision']['resultSummary'])

    def test_update_revision_scope_writes_scope_and_advances_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            run_script(
                'record_revision_feedback.py',
                str(project),
                'plot_feedback',
                'add_on',
                '加强第1章钩子',
            )

            result = run_script(
                'update_revision_scope.py',
                str(project),
                '--affected-stages',
                'drafting,polishing',
                '--affected-files',
                '05_本轮章节规划.md,manuscript/第1章_开端.md',
                '--scope-summary',
                '需要回改章节规划和第一章情绪推进',
                '--conflict-summary',
                '不覆盖主线设定，只加强开篇吸引力',
                '--plan-summary',
                '先改规划，再改正文，再复核润色判断',
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['revision']['affectedStages'], ['drafting', 'polishing'])
            self.assertEqual(state['revision']['currentRevisionGate'], 'awaiting_revision_plan_approval')
            self.assertEqual(state['revision']['scopeSummary'], '需要回改章节规划和第一章情绪推进')
            self.assertIn('05_本轮章节规划.md', (project / '06_反馈与修订.md').read_text(encoding='utf-8'))

    def test_complete_revision_cycle_result_pending_and_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            run_script('record_revision_feedback.py', str(project), 'plot_feedback', 'add_on', '加强开篇')
            run_script(
                'update_revision_scope.py',
                str(project),
                '--affected-stages',
                'drafting,polishing',
                '--affected-files',
                '05_本轮章节规划.md,manuscript/第1章_开端.md',
                '--scope-summary',
                '回改规划和正文',
                '--conflict-summary',
                '不改核心世界观',
                '--plan-summary',
                '先规划后正文',
            )

            pending = run_script(
                'complete_revision_cycle.py',
                str(project),
                'result_pending',
                '修订完成，已更新章节规划与正文',
            )
            self.assertEqual(pending.returncode, 0, pending.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['revision']['currentRevisionGate'], 'awaiting_revision_result_approval')
            self.assertEqual(state['revision']['resultSummary'], '修订完成，已更新章节规划与正文')

            close = run_script('complete_revision_cycle.py', str(project), 'close')
            self.assertEqual(close.returncode, 0, close.stderr)
            closed = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertFalse(closed['revision']['active'])
            self.assertIsNone(closed['revision']['currentRevisionGate'])
            self.assertEqual(closed['revision']['lastClosedRevision']['resultSummary'], '修订完成，已更新章节规划与正文')

    def test_complete_revision_cycle_reject_moves_back_to_plan_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            run_script('record_revision_feedback.py', str(project), 'plot_feedback', 'add_on', '加强开篇')
            run_script(
                'update_revision_scope.py',
                str(project),
                '--affected-stages',
                'drafting',
                '--affected-files',
                'manuscript/第1章_开端.md',
                '--scope-summary',
                '只回改第一章',
                '--conflict-summary',
                '不影响大纲',
                '--plan-summary',
                '改正文后再复核',
            )
            run_script('complete_revision_cycle.py', str(project), 'result_pending', '修订结果待确认')

            reject = run_script('complete_revision_cycle.py', str(project), 'reject', '主角情绪还不够狠')
            self.assertEqual(reject.returncode, 0, reject.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['revision']['currentRevisionGate'], 'awaiting_revision_plan_approval')
            self.assertEqual(state['review']['lastRejectedReason'], '主角情绪还不够狠')

    def test_status_brief_reports_revision_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            run_script('record_revision_feedback.py', str(project), 'character_feedback', 'override', '主角性格偏软')
            result = run_script('novel_project_status.py', str(project), '--brief')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('当前卡点：等待你确认修订范围', result.stdout)
            self.assertIn('建议下一步：先处理修订模式：等待你确认修订范围', result.stdout)

    def test_status_full_reports_revision_scope_and_last_closed_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            run_script('record_revision_feedback.py', str(project), 'plot_feedback', 'add_on', '加强开篇')
            run_script(
                'update_revision_scope.py',
                str(project),
                '--affected-stages',
                'drafting,polishing',
                '--affected-files',
                '05_本轮章节规划.md,manuscript/第1章_开端.md',
                '--scope-summary',
                '回改规划和正文',
                '--conflict-summary',
                '不改核心世界观',
                '--plan-summary',
                '先规划后正文',
            )
            run_script('complete_revision_cycle.py', str(project), 'result_pending', '修订完成，已更新章节规划与正文')
            run_script('complete_revision_cycle.py', str(project), 'close')

            result = run_script('novel_project_status.py', str(project))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('处理模式：无', result.stdout)
            self.assertIn('最近关闭修订：加强开篇', result.stdout)
            self.assertIn('最近关闭结果：修订完成，已更新章节规划与正文', result.stdout)

    def test_invalid_close_transition_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            run_script('record_revision_feedback.py', str(project), 'plot_feedback', 'add_on', '加强开篇')
            invalid = run_script('complete_revision_cycle.py', str(project), 'close')
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn('awaiting approval', invalid.stderr + invalid.stdout)

    def test_load_project_state_reconstructs_active_revision_from_revision_doc_when_state_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_revision_ready_project(Path(tmp))
            run_script('record_revision_feedback.py', str(project), 'character_feedback', 'override', '第3章主角性格发虚')
            run_script(
                'update_revision_scope.py',
                str(project),
                '--affected-stages',
                'drafting,polishing',
                '--affected-files',
                '05_本轮章节规划.md,manuscript/chapter-01.md',
                '--scope-summary',
                '回改章节规划和第一章人物状态',
                '--conflict-summary',
                '覆盖旧的人物语气设定',
                '--plan-summary',
                '先改规划，再改正文，再复核润色判断',
            )
            (project / '.novel-state.json').unlink()

            result = run_script('load_project_state.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['revision']['active'])
            self.assertEqual(state['revision']['feedbackType'], 'character_feedback')
            self.assertEqual(state['revision']['feedbackSummary'], '第3章主角性格发虚')
            self.assertEqual(state['revision']['currentRevisionGate'], 'awaiting_revision_plan_approval')
            self.assertEqual(state['revision']['affectedStages'], ['drafting', 'polishing'])
            self.assertEqual(
                state['revision']['affectedFiles'],
                ['05_本轮章节规划.md', 'manuscript/chapter-01.md'],
            )
            self.assertTrue(state['revision']['awaitingUserApproval'])
            self.assertIn(
                'Formal revision active: awaiting_revision_plan_approval',
                state['blockingIssues'],
            )

    def test_load_project_state_recovers_workflow_from_active_revision_doc_when_state_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_revision_ready_project(Path(tmp))
            run_script('record_revision_feedback.py', str(project), 'character_feedback', 'override', '第3章主角性格发虚')
            run_script(
                'update_revision_scope.py',
                str(project),
                '--affected-stages',
                'drafting,polishing',
                '--affected-files',
                '05_本轮章节规划.md,manuscript/chapter-01.md',
                '--scope-summary',
                '回改章节规划和第一章人物状态',
                '--conflict-summary',
                '覆盖旧的人物语气设定',
                '--plan-summary',
                '先改规划，再改正文，再复核润色判断',
            )
            (project / '.novel-state.json').unlink()

            result = run_script('load_project_state.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['workflow']['currentStage'], 'drafting')
            self.assertEqual(state['workflow']['nextStage'], 'drafting')
            self.assertEqual(state['workflow']['status'], 'awaiting_user_approval')
            self.assertEqual(state['revision']['currentRevisionGate'], 'awaiting_revision_plan_approval')

    def test_final_review_readiness_fails_when_active_revision_is_reconstructed_from_revision_doc(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_revision_ready_project(Path(tmp))
            run_script('record_revision_feedback.py', str(project), 'plot_feedback', 'add_on', '加强第1章钩子')
            (project / '.novel-state.json').unlink()

            result = run_script('check_stage_ready.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('READY: NO', result.stdout)
            self.assertIn('Current revision gate is still open', result.stdout)
            self.assertIn('awaiting_revision_scope_confirmation', result.stdout)

    def test_polishing_readiness_fails_when_active_revision_gate_is_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_revision_ready_project(Path(tmp))
            run_script('record_revision_feedback.py', str(project), 'character_feedback', 'override', '第3章主角性格发虚')
            run_script(
                'update_revision_scope.py',
                str(project),
                '--affected-stages',
                'drafting,polishing',
                '--affected-files',
                '05_本轮章节规划.md,manuscript/chapter-01.md',
                '--scope-summary',
                '回改章节规划和第一章人物状态',
                '--conflict-summary',
                '覆盖旧的人物语气设定',
                '--plan-summary',
                '先改规划，再改正文，再复核润色判断',
            )

            result = run_script('check_stage_ready.py', str(project), 'polishing')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('READY: NO', result.stdout)
            self.assertIn('Current revision gate is still open', result.stdout)
            self.assertIn('awaiting_revision_plan_approval', result.stdout)

    def test_load_project_state_reconstructs_last_closed_revision_from_revision_doc_when_state_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_revision_ready_project(Path(tmp))
            run_script('record_revision_feedback.py', str(project), 'plot_feedback', 'add_on', '加强开篇')
            run_script(
                'update_revision_scope.py',
                str(project),
                '--affected-stages',
                'drafting,polishing',
                '--affected-files',
                '05_本轮章节规划.md,manuscript/chapter-01.md',
                '--scope-summary',
                '回改规划和正文',
                '--conflict-summary',
                '不改核心世界观',
                '--plan-summary',
                '先规划后正文',
            )
            run_script('complete_revision_cycle.py', str(project), 'result_pending', '修订完成，已更新章节规划与正文')
            run_script('complete_revision_cycle.py', str(project), 'close')
            (project / '.novel-state.json').unlink()

            result = run_script('load_project_state.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertFalse(state['revision']['active'])
            self.assertIsNone(state['revision']['currentRevisionGate'])
            self.assertEqual(state['review']['lastUserFeedbackSummary'], '加强开篇')

            closed = state['revision']['lastClosedRevision']
            self.assertEqual(closed['feedbackType'], 'plot_feedback')
            self.assertEqual(closed['feedbackSummary'], '加强开篇')
            self.assertEqual(
                closed['affectedFiles'],
                ['05_本轮章节规划.md', 'manuscript/chapter-01.md'],
            )
            self.assertEqual(closed['resultSummary'], '修订完成，已更新章节规划与正文')
            self.assertEqual(closed['closeMode'], '用户确认')
            self.assertTrue(closed['closedAt'])

    def test_load_project_state_tolerates_incomplete_active_revision_doc(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_revision_ready_project(Path(tmp))
            (project / '06_反馈与修订.md').write_text(
                '# 06_反馈与修订\n\n'
                '## 当前正式修订\n'
                '- 状态：等待确认范围\n'
                '- 反馈摘要：需要回改第一章开篇钩子\n'
                '- 当前修订 gate：awaiting_revision_scope_confirmation\n'
                '- 最近更新时间：2026-03-27T00:00:00Z\n\n'
                '## 最近关闭的修订\n'
                '### 无\n'
                '- 反馈摘要：无\n'
                '- 影响范围：无\n'
                '- 修订结果：无\n'
                '- 关闭方式：无\n',
                encoding='utf-8',
            )

            result = run_script('load_project_state.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['revision']['active'])
            self.assertEqual(state['revision']['feedbackSummary'], '需要回改第一章开篇钩子')
            self.assertIsNone(state['revision']['feedbackType'])
            self.assertEqual(state['revision']['affectedStages'], [])
            self.assertEqual(state['revision']['affectedFiles'], [])
            self.assertEqual(state['revision']['currentRevisionGate'], 'awaiting_revision_scope_confirmation')
            self.assertIn(
                'Formal revision active: awaiting_revision_scope_confirmation',
                state['blockingIssues'],
            )

    def test_load_project_state_tolerates_incomplete_closed_revision_doc(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_revision_ready_project(Path(tmp))
            (project / '06_反馈与修订.md').write_text(
                '# 06_反馈与修订\n\n'
                '## 当前正式修订\n'
                '- 状态：已关闭\n'
                '- 当前修订 gate：无\n'
                '- 最近更新时间：2026-03-27T00:00:00Z\n\n'
                '## 最近关闭的修订\n'
                '### 2026-03-26T12:00:00Z\n'
                '- 修订结果：已完成必要修补\n',
                encoding='utf-8',
            )

            result = run_script('load_project_state.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertFalse(state['revision']['active'])
            self.assertIsNone(state['revision']['currentRevisionGate'])

            closed = state['revision']['lastClosedRevision']
            self.assertIsNone(closed['feedbackType'])
            self.assertIsNone(closed['feedbackSummary'])
            self.assertEqual(closed['affectedFiles'], [])
            self.assertEqual(closed['resultSummary'], '已完成必要修补')
            self.assertEqual(closed['closedAt'], '2026-03-26T12:00:00Z')
            self.assertIsNone(closed['closeMode'])

    def test_load_project_state_ignores_malformed_revision_doc_without_dirty_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_revision_ready_project(Path(tmp))
            (project / '06_反馈与修订.md').write_text(
                '# 06_反馈与修订\n\n'
                '当前正式修订\n'
                '反馈摘要 第1章需要补强\n'
                '当前修订 gate awaiting_revision_scope_confirmation\n\n'
                '最近关闭的修订\n'
                '2026-03-26T12:00:00Z plot_feedback\n'
                '修订结果 已完成必要修补\n',
                encoding='utf-8',
            )

            result = run_script('load_project_state.py', str(project))

            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertFalse(state['revision']['active'])
            self.assertIsNone(state['revision']['currentRevisionGate'])
            self.assertIsNone(state['revision']['feedbackSummary'])
            self.assertIsNone(state['revision']['lastClosedRevision'])
            self.assertEqual(
                [item for item in state['blockingIssues'] if item.startswith('Formal revision active:')],
                [],
            )


if __name__ == '__main__':
    unittest.main()
