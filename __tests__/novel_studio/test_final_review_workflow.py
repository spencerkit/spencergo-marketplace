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


class FinalReviewWorkflowTest(unittest.TestCase):
    def create_final_review_project(
        self,
        root: Path,
        *,
        write_state: bool = True,
        proofreading_complete: bool = True,
        recap: str = (
            '## 当前已推进到的位置\n'
            '- 第一卷完结\n\n'
            '## 最近一轮发生的关键事件\n'
            '- 主角完成反转\n\n'
            '## 当前未回收的伏笔 / 悬念\n'
            '- 黑箱来源未揭示\n\n'
            '## 下一轮写作必须记住的点\n'
            '- 保持配角动机连续\n'
        ),
        report: str | None = None,
        final_decision=None,
        final_delivery_ready: bool = False,
        final_blocking_issues=None,
        final_review_summary: str = '',
        final_approved: bool = False,
        current_gate=None,
        revision_gate=None,
        revision_active: bool = False,
        revision_awaiting_user_approval: bool = False,
    ) -> Path:
        project = root / '测试小说'
        project.mkdir()
        manuscript = project / 'manuscript'
        manuscript.mkdir()
        (manuscript / 'chapter-01.md').write_text('# 第一章\n\n正文', encoding='utf-8')

        if recap is not None:
            (project / '05_前情回顾.md').write_text(recap, encoding='utf-8')
        if report is not None:
            (project / '07_终审报告.md').write_text(report, encoding='utf-8')

        state = {
            'project': {'title': '测试小说', 'rootPath': str(project)},
            'workflow': {
                'currentStage': 'final-review',
                'currentSubstage': None,
                'lastCompletedStage': 'proofreading',
                'nextStage': None,
                'status': 'in_progress',
            },
            'approvals': {},
            'artifacts': {},
            'batch': {
                'active': True,
                'proofreadingComplete': proofreading_complete,
            },
            'review': {
                'currentGate': current_gate,
                'finalDecision': final_decision,
                'finalDeliveryReady': final_delivery_ready,
                'finalBlockingIssues': final_blocking_issues or [],
                'finalReviewSummary': final_review_summary,
            },
            'revision': {
                'currentGate': revision_gate,
                'active': revision_active,
                'awaitingUserApproval': revision_awaiting_user_approval,
                'currentRevisionGate': revision_gate,
            },
            'blockingIssues': [],
            'notes': {},
        }
        state['approvals']['finalApproved'] = final_approved
        if write_state:
            (project / '.novel-state.json').write_text(
                json.dumps(state, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
        return project

    def test_load_project_state_normalizes_existing_state_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            (project / '.novel-state.json').write_text(
                json.dumps(
                    {
                        'project': {'title': '测试小说', 'rootPath': str(project)},
                        'workflow': {'status': 'legacy'},
                        'review': {},
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            result = run_script('load_project_state.py', str(project))
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertIn('finalDecision', state['review'])
            self.assertIn('finalDeliveryReady', state['review'])
            self.assertIn('finalBlockingIssues', state['review'])
            self.assertIn('finalReviewSummary', state['review'])
            self.assertFalse(state['review']['finalDeliveryReady'])
            self.assertEqual(state['review']['finalBlockingIssues'], [])

    def test_load_project_state_reconstructs_final_review_fields_from_report_when_state_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = (
                '# 07_终审报告\n\n'
                '## 最终结论\n'
                '- conditional pass\n'
                '- 摘要：终审接近通过，但还有一处关键动机需要补强。\n\n'
                '## 是否可交付\n'
                '- false\n\n'
                '## 主要优点\n'
                '- 结尾情绪稳定\n\n'
                '## 主要问题\n'
                '- 个别动机句偏弱\n\n'
                '## 阻塞问题\n'
                '- 终章关键动机还需再压实\n\n'
                '## 建议动作\n'
                '- 补强终章动机句\n'
            )
            project = self.create_final_review_project(
                Path(tmp),
                write_state=False,
                report=report,
            )

            result = run_script('load_project_state.py', str(project))
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['review']['finalDecision'], 'conditional pass')
            self.assertFalse(state['review']['finalDeliveryReady'])
            self.assertEqual(state['review']['finalBlockingIssues'], ['终章关键动机还需再压实'])
            self.assertEqual(
                state['review']['finalReviewSummary'],
                '终审接近通过，但还有一处关键动机需要补强。',
            )
            self.assertEqual(state['workflow']['currentStage'], 'final-review')
            self.assertNotEqual(state['workflow']['nextStage'], 'polishing')

    def test_write_final_review_generates_report_and_syncs_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()

            result = run_script(
                'write_final_review.py',
                str(project),
                '--decision',
                'conditional pass',
                '--delivery-ready',
                'false',
                '--strengths',
                '结尾收束稳定',
                '--issues',
                '个别段落节奏偏慢',
                '--blockers',
                '终章关键动机还需再压实',
                '--actions',
                '补强终章动机句',
                '--summary',
                '整体可进入交付前最后修补，但仍有一个阻塞项待处理。',
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['review']['finalDecision'], 'conditional pass')
            self.assertFalse(state['review']['finalDeliveryReady'])
            self.assertEqual(state['review']['finalBlockingIssues'], ['终章关键动机还需再压实'])
            self.assertEqual(
                state['review']['finalReviewSummary'],
                '整体可进入交付前最后修补，但仍有一个阻塞项待处理。',
            )
            self.assertIn(
                'Final review blocker: 终章关键动机还需再压实',
                state['blockingIssues'],
            )

            report = (project / '07_终审报告.md').read_text(encoding='utf-8')
            self.assertIn('## 最终结论', report)
            self.assertIn('## 是否可交付', report)
            self.assertIn('## 主要优点', report)
            self.assertIn('## 主要问题', report)
            self.assertIn('## 阻塞问题', report)
            self.assertIn('## 建议动作', report)
            self.assertIn('conditional pass', report)
            self.assertIn('false', report)
            self.assertIn('终章关键动机还需再压实', report)
            self.assertIn('整体可进入交付前最后修补，但仍有一个阻塞项待处理。', report)

    def test_write_final_review_rejects_rework_required_with_delivery_ready_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()

            result = run_script(
                'write_final_review.py',
                str(project),
                '--decision',
                'rework required',
                '--delivery-ready',
                'true',
                '--strengths',
                '设定清晰',
                '--issues',
                '终章逻辑需要返工',
                '--actions',
                '重写终章逻辑链',
                '--summary',
                '当前版本必须返工后再评估。',
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('rework required', result.stderr)
            self.assertIn('delivery-ready=true', result.stderr)
            self.assertFalse((project / '07_终审报告.md').exists())

    def test_write_final_review_rejects_pass_with_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()

            result = run_script(
                'write_final_review.py',
                str(project),
                '--decision',
                'pass',
                '--delivery-ready',
                'false',
                '--blockers',
                '仍有关键设定未闭环',
                '--actions',
                '先补齐关键设定说明',
                '--summary',
                '整体质量达标，但仍存在阻塞项。',
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('pass', result.stderr)
            self.assertIn('blockers', result.stderr)
            self.assertFalse((project / '07_终审报告.md').exists())

    def test_record_revision_feedback_preserves_final_review_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            state = {
                'project': {'title': '测试小说', 'rootPath': str(project)},
                'workflow': {
                    'currentStage': None,
                    'currentSubstage': None,
                    'lastCompletedStage': None,
                    'nextStage': None,
                    'status': 'in_progress',
                },
                'approvals': {},
                'artifacts': {},
                'batch': {},
                'review': {
                    'finalDecision': 'pass',
                    'finalDeliveryReady': True,
                    'finalBlockingIssues': ['旧阻塞项'],
                    'finalReviewSummary': '终审已通过',
                    'futureFlag': 'keep-me',
                },
                'revision': {},
                'blockingIssues': ['Final review blocker: 旧阻塞项'],
                'notes': {},
            }
            (project / '.novel-state.json').write_text(
                json.dumps(state, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )

            result = run_script(
                'record_revision_feedback.py',
                str(project),
                'character_feedback',
                'override',
                '新的正式反馈',
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            updated = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(updated['review']['finalDecision'], 'pass')
            self.assertTrue(updated['review']['finalDeliveryReady'])
            self.assertEqual(updated['review']['finalBlockingIssues'], ['旧阻塞项'])
            self.assertEqual(updated['review']['finalReviewSummary'], '终审已通过')
            self.assertEqual(updated['review']['futureFlag'], 'keep-me')
            self.assertIn('Final review blocker: 旧阻塞项', updated['blockingIssues'])

    def test_final_review_readiness_fails_when_proofreading_not_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                proofreading_complete=False,
            )

            result = run_script('check_stage_ready.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('READY: NO', result.stdout)
            self.assertIn('proofreading is not marked complete', result.stdout)

    def test_final_review_readiness_fails_when_recap_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                recap=None,
            )

            result = run_script('check_stage_ready.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('READY: NO', result.stdout)
            self.assertIn('05_前情回顾.md is missing or empty', result.stdout)

    def test_final_review_completion_fails_when_report_and_state_disagree(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = (
                '# 07_终审报告\n\n'
                '## 最终结论\n'
                '- pass\n'
                '- 摘要：终审通过\n\n'
                '## 是否可交付\n'
                '- true\n\n'
                '## 主要优点\n'
                '- 优点\n\n'
                '## 主要问题\n'
                '- 问题\n\n'
                '## 阻塞问题\n'
                '- 无\n\n'
                '## 建议动作\n'
                '- 直接交付\n'
            )
            project = self.create_final_review_project(
                Path(tmp),
                report=report,
                final_decision='conditional pass',
                final_delivery_ready=False,
                final_review_summary='可以交付，但建议补一处说明',
            )

            result = run_script('check_stage_complete.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('COMPLETE: NO', result.stdout)
            self.assertIn('review.finalDecision', result.stdout)
            self.assertIn('review.finalDeliveryReady', result.stdout)

    def test_final_review_completion_fails_when_summary_and_blockers_disagree(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = (
                '# 07_终审报告\n\n'
                '## 最终结论\n'
                '- conditional pass\n'
                '- 摘要：终审接近通过，但仍需先处理关键阻塞项。\n\n'
                '## 是否可交付\n'
                '- false\n\n'
                '## 主要优点\n'
                '- 情绪收束稳定\n\n'
                '## 主要问题\n'
                '- 个别解释还可再压缩\n\n'
                '## 阻塞问题\n'
                '- 终章关键动机还需再压实\n\n'
                '## 建议动作\n'
                '- 补强终章动机句\n'
            )
            project = self.create_final_review_project(
                Path(tmp),
                report=report,
                final_decision='conditional pass',
                final_delivery_ready=False,
                final_blocking_issues=['另一个阻塞项'],
                final_review_summary='旧摘要：可以直接交付。',
            )

            result = run_script('check_stage_complete.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('COMPLETE: NO', result.stdout)
            self.assertIn('review.finalBlockingIssues', result.stdout)
            self.assertIn('review.finalReviewSummary', result.stdout)

    def test_final_review_completion_fails_when_rework_required_is_marked_delivery_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = (
                '# 07_终审报告\n\n'
                '## 最终结论\n'
                '- rework required\n'
                '- 摘要：当前版本必须返工后再评估。\n\n'
                '## 是否可交付\n'
                '- true\n\n'
                '## 主要优点\n'
                '- 核心设定明确\n\n'
                '## 主要问题\n'
                '- 终章逻辑断裂\n\n'
                '## 阻塞问题\n'
                '- 无\n\n'
                '## 建议动作\n'
                '- 返工终章逻辑链\n'
            )
            project = self.create_final_review_project(
                Path(tmp),
                report=report,
                final_decision='rework required',
                final_delivery_ready=True,
                final_review_summary='当前版本必须返工后再评估。',
            )

            result = run_script('check_stage_complete.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('COMPLETE: NO', result.stdout)
            self.assertIn('delivery-ready=true', result.stdout)
            self.assertIn('rework required', result.stdout)

    def test_final_review_completion_fails_when_pass_has_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = (
                '# 07_终审报告\n\n'
                '## 最终结论\n'
                '- pass\n'
                '- 摘要：整体质量达标，但还有阻塞项未清理。\n\n'
                '## 是否可交付\n'
                '- false\n\n'
                '## 主要优点\n'
                '- 文风稳定\n\n'
                '## 主要问题\n'
                '- 尾声说明略少\n\n'
                '## 阻塞问题\n'
                '- 终章关键设定仍未闭环\n\n'
                '## 建议动作\n'
                '- 先补齐终章设定说明\n'
            )
            project = self.create_final_review_project(
                Path(tmp),
                report=report,
                final_decision='pass',
                final_delivery_ready=False,
                final_blocking_issues=['终章关键设定仍未闭环'],
                final_review_summary='整体质量达标，但还有阻塞项未清理。',
            )

            result = run_script('check_stage_complete.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('COMPLETE: NO', result.stdout)
            self.assertIn('pass cannot be combined with blockers', result.stdout)

    def test_final_review_completion_passes_when_report_and_state_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = (
                '# 07_终审报告\n\n'
                '## 最终结论\n'
                '- conditional pass\n'
                '- 摘要：可以交付，但建议补一处说明\n\n'
                '## 是否可交付\n'
                '- false\n\n'
                '## 主要优点\n'
                '- 结尾稳定\n\n'
                '## 主要问题\n'
                '- 个别解释偏弱\n\n'
                '## 阻塞问题\n'
                '- 无\n\n'
                '## 建议动作\n'
                '- 补一句背景说明\n'
            )
            project = self.create_final_review_project(
                Path(tmp),
                report=report,
                final_decision='conditional pass',
                final_delivery_ready=False,
                final_review_summary='可以交付，但建议补一处说明',
            )

            result = run_script('check_stage_complete.py', str(project), 'final-review')

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('COMPLETE: YES', result.stdout)

    def test_final_review_readiness_fails_when_already_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = (
                '# 07_终审报告\n\n'
                '## 最终结论\n'
                '- pass\n'
                '- 摘要：终审通过\n\n'
                '## 是否可交付\n'
                '- true\n\n'
                '## 主要优点\n'
                '- 优点\n\n'
                '## 主要问题\n'
                '- 无\n\n'
                '## 阻塞问题\n'
                '- 无\n\n'
                '## 建议动作\n'
                '- 直接交付\n'
            )
            project = self.create_final_review_project(
                Path(tmp),
                report=report,
                final_decision='pass',
                final_delivery_ready=True,
            )

            result = run_script('check_stage_ready.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('READY: NO', result.stdout)
            self.assertIn('already completed', result.stdout)

    def test_final_review_readiness_fails_when_report_exists_but_state_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = (
                '# 07_终审报告\n\n'
                '## 最终结论\n'
                '- pass\n'
                '- 摘要：终审通过\n\n'
                '## 是否可交付\n'
                '- true\n\n'
                '## 主要优点\n'
                '- 优点\n\n'
                '## 主要问题\n'
                '- 无\n\n'
                '## 阻塞问题\n'
                '- 无\n\n'
                '## 建议动作\n'
                '- 直接交付\n'
            )
            project = self.create_final_review_project(
                Path(tmp),
                write_state=False,
                report=report,
            )

            result = run_script('check_stage_ready.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('READY: NO', result.stdout)
            self.assertIn('already completed', result.stdout)

    def test_final_review_readiness_mixed_case_stage_still_obeys_review_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                current_gate='awaiting_final_review_signoff',
            )

            result = run_script('check_stage_ready.py', str(project), 'Final-Review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('READY: NO', result.stdout)
            self.assertIn('Current review gate is still open', result.stdout)

    def test_final_review_readiness_fails_when_recap_structure_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                recap='只有一行总结，没有结构化章节',
            )

            result = run_script('check_stage_ready.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('READY: NO', result.stdout)
            self.assertIn('05_前情回顾.md missing required sections', result.stdout)

    def test_final_review_readiness_passes_when_prerequisites_are_met_and_not_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(Path(tmp))

            result = run_script('check_stage_ready.py', str(project), 'final-review')

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('READY: YES', result.stdout)

    def test_final_review_readiness_fails_when_state_file_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(Path(tmp))
            (project / '.novel-state.json').write_text('{ invalid json', encoding='utf-8')

            result = run_script('check_stage_ready.py', str(project), 'final-review')

            self.assertNotEqual(result.returncode, 0)
            self.assertIn('READY: NO', result.stdout)
            self.assertIn('.novel-state.json', result.stdout)

    def test_status_brief_includes_final_review_summary_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                final_decision='pass',
                final_delivery_ready=True,
                final_review_summary='终审通过，可进入最终交付确认。',
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('终审结论：pass', result.stdout)
            self.assertIn('可交付：是', result.stdout)
            self.assertIn('终审摘要：终审通过，可进入最终交付确认。', result.stdout)

    def test_status_full_includes_final_review_section_and_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                final_decision='conditional pass',
                final_delivery_ready=False,
                final_blocking_issues=['终章转折动机还需补强'],
                final_review_summary='整体接近交付，但仍需先处理阻塞项。',
            )

            result = run_script('novel_project_status.py', str(project))

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('[终审状态]', result.stdout)
            self.assertIn('终审结论：conditional pass', result.stdout)
            self.assertIn('终审可交付：否', result.stdout)
            self.assertIn('终审摘要：整体接近交付，但仍需先处理阻塞项。', result.stdout)
            self.assertIn('终审阻塞项：', result.stdout)
            self.assertIn('- 终章转折动机还需补强', result.stdout)

    def test_status_next_step_requests_final_delivery_confirmation_after_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                final_decision='pass',
                final_delivery_ready=True,
                final_review_summary='终审通过。',
                final_approved=False,
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('建议下一步：请确认最终交付。', result.stdout)

    def test_status_next_step_does_not_request_final_delivery_when_pass_not_delivery_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                final_decision='pass',
                final_delivery_ready=False,
                final_review_summary='终审通过，但当前版本还不能交付。',
                final_approved=False,
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('可交付：否', result.stdout)
            self.assertNotIn('建议下一步：请确认最终交付。', result.stdout)
            self.assertIn(
                '建议下一步：终审已通过，但当前版本尚不可交付：请先补齐交付前收尾项。',
                result.stdout,
            )

    def test_status_next_step_prioritizes_final_review_blockers_for_conditional_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                final_decision='conditional pass',
                final_delivery_ready=False,
                final_blocking_issues=['终章转折动机还需补强'],
                final_review_summary='先修补阻塞项。',
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(
                '建议下一步：先解决终审阻塞项，再请求最终交付确认。',
                result.stdout,
            )

    def test_status_next_step_guides_conditional_pass_without_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                final_decision='conditional pass',
                final_delivery_ready=False,
                final_review_summary='没有阻塞项，但还需做最后收尾确认。',
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('终审结论：conditional pass', result.stdout)
            self.assertIn('可交付：否', result.stdout)
            self.assertIn('建议下一步：请先完成终审收尾项，再请求最终交付确认。', result.stdout)

    def test_status_next_step_guides_conditional_pass_delivery_ready_to_final_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                final_decision='conditional pass',
                final_delivery_ready=True,
                final_review_summary='条件通过，已满足交付条件。',
                final_approved=False,
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('终审结论：conditional pass', result.stdout)
            self.assertIn('可交付：是', result.stdout)
            self.assertIn('建议下一步：请确认最终交付。', result.stdout)

    def test_status_brief_prioritizes_revision_gate_over_final_delivery_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_final_review_project(
                Path(tmp),
                final_decision='pass',
                final_delivery_ready=True,
                final_review_summary='终审通过。',
                final_approved=False,
                revision_active=True,
                revision_awaiting_user_approval=True,
                revision_gate='awaiting_revision_result_approval',
            )

            result = run_script('novel_project_status.py', str(project), '--brief')

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('终审结论：pass', result.stdout)
            self.assertIn('建议下一步：先处理修订模式：等待你确认修订结果', result.stdout)


if __name__ == '__main__':
    unittest.main()
