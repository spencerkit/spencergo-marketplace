import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / 'skills/novel-studio/scripts'
CONSISTENCY_ARTIFACT = '05I_证据链与矛盾对照表.md'


def run_script(name, *args):
    cmd = ['python3', str(SCRIPTS / name), *args]
    return subprocess.run(cmd, text=True, capture_output=True)


class NarrativeIntelligenceReviewTest(unittest.TestCase):
    def write_state(self, project: Path, payload: dict) -> None:
        (project / '.novel-state.json').write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

    def create_review_project(
        self,
        root: Path,
        *,
        current_stage: str,
        batch: dict | None = None,
        review: dict | None = None,
        revision: dict | None = None,
        narrative_intelligence: dict | None = None,
        auto_pilot: dict | None = None,
    ) -> Path:
        project = root / '测试小说'
        project.mkdir()
        state = {
            'project': {'title': '测试小说', 'rootPath': str(project)},
            'workflow': {
                'currentStage': current_stage,
                'currentSubstage': None,
                'lastCompletedStage': 'polishing',
                'nextStage': current_stage,
                'status': 'in_progress',
            },
            'batch': {
                'active': True,
                'chapterRange': '第10章',
                'chapterCount': 1,
                'scopeConfirmed': True,
                'chapterPlanExists': True,
                'chapterPlanApproved': True,
                'draftComplete': True,
                'polishingComplete': True,
                'proofreadingComplete': False,
            },
            'review': review or {},
            'revision': revision or {},
            'narrativeIntelligence': narrative_intelligence or {},
            'autoPilot': auto_pilot or {},
            'blockingIssues': [],
            'notes': {},
        }
        if batch:
            state['batch'].update(batch)
        self.write_state(project, state)
        return project

    def test_update_narrative_intelligence_proofreading_writes_consistency_report_and_stops_autopilot_on_critical_issue(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_review_project(
                Path(tmp),
                current_stage='proofreading',
                auto_pilot={
                    'active': True,
                    'goalChapter': '第10章',
                    'goalCondition': 'proofreading_completed',
                    'awaitingManualResume': False,
                },
            )
            (project / '05G_伏笔三元组账本.md').write_text(
                '# 05G_伏笔三元组账本\n\n'
                '## 当前三元组\n'
                '- id: fp-001 | status: broken | cause: 第1章玉佩 | promise: 身世谜团 | payoff: 无\n',
                encoding='utf-8',
            )

            result = run_script(
                'update_narrative_intelligence.py',
                str(project),
                '--stage',
                'proofreading',
                '--chapter-label',
                '第10章',
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            consistency = state['narrativeIntelligence']['consistency']
            auto_pilot = state['autoPilot']

            self.assertTrue((project / CONSISTENCY_ARTIFACT).exists())
            self.assertIn('fp-001', ''.join(consistency['openCriticalIssues']))
            self.assertEqual(consistency['lastCheckStage'], 'proofreading')
            self.assertFalse(auto_pilot['active'])
            self.assertTrue(auto_pilot['awaitingManualResume'])
            self.assertIn('fp-001', auto_pilot['stopReason'])

    def test_write_final_review_merges_open_critical_issues_into_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_review_project(
                Path(tmp),
                current_stage='final-review',
                narrative_intelligence={
                    'consistency': {
                        'openCriticalIssues': ['伏笔 fp-001 已断裂：缺少 payoff 证据链'],
                    },
                },
            )

            result = run_script(
                'write_final_review.py',
                str(project),
                '--decision',
                'conditional pass',
                '--delivery-ready',
                'false',
                '--summary',
                '还有一致性问题待处理。',
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertIn(
                '伏笔 fp-001 已断裂：缺少 payoff 证据链',
                state['review']['finalBlockingIssues'],
            )
            self.assertIn(
                'Final review blocker: 伏笔 fp-001 已断裂：缺少 payoff 证据链',
                state['blockingIssues'],
            )

    def test_record_revision_feedback_prefills_scope_and_plan_from_narrative_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_review_project(
                Path(tmp),
                current_stage='proofreading',
                narrative_intelligence={
                    'consistency': {
                        'openCriticalIssues': ['第8章人物认知越界'],
                    },
                },
            )

            result = run_script(
                'record_revision_feedback.py',
                str(project),
                'plot_feedback',
                'add_on',
                '处理一致性问题',
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertIn('第8章人物认知越界', state['revision']['scopeSummary'])
            self.assertIn('先修', state['revision']['revisionPlanSummary'])
            self.assertIn('05I_证据链与矛盾对照表.md', state['revision']['affectedFiles'])

    def test_status_outputs_narrative_intelligence_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_review_project(
                Path(tmp),
                current_stage='proofreading',
                narrative_intelligence={
                    'timeline': {
                        'openTemporalRisks': ['第10章时间线存在潜在冲突'],
                    },
                    'consistency': {
                        'openCriticalIssues': ['第8章人物认知越界'],
                    },
                },
            )

            brief = run_script('novel_project_status.py', str(project), '--brief')
            self.assertEqual(brief.returncode, 0, brief.stderr)
            self.assertIn('叙事智能：1 条关键问题 / 1 条时间风险', brief.stdout)

            full = run_script('novel_project_status.py', str(project))
            self.assertEqual(full.returncode, 0, full.stderr)
            self.assertIn('[叙事智能]', full.stdout)
            self.assertIn('关键问题：1', full.stdout)
            self.assertIn('时间风险：1', full.stdout)


if __name__ == '__main__':
    unittest.main()
