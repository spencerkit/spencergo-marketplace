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


class NarrativeIntelligenceStateTest(unittest.TestCase):
    def write_state(self, project: Path, payload: dict) -> None:
        (project / '.novel-state.json').write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )

    def load_persisted_state(self, project: Path) -> dict:
        result = run_script('load_project_state.py', str(project))
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))

    def test_load_state_adds_narrative_intelligence_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {'currentStage': 'discovery'},
                },
            )

            state = self.load_persisted_state(project)
            narrative_intelligence = state['narrativeIntelligence']

            self.assertIn('narrativeIntelligence', state)
            self.assertEqual(
                narrative_intelligence,
                {
                    'timeline': {
                        'enabled': False,
                        'lastUpdatedBatch': None,
                        'lastTouchedChapters': [],
                        'openTemporalRisks': [],
                    },
                    'cfpg': {
                        'foreshadowTriples': [],
                        'tripleCounts': {
                            'total': 0,
                            'pending': 0,
                            'fulfilled': 0,
                            'broken': 0,
                            'expired': 0,
                        },
                        'lastUpdatedBatch': None,
                    },
                    'theoryOfMind': {
                        'characterBeliefs': [],
                        'beliefConflicts': [],
                        'lastUpdatedBatch': None,
                    },
                    'consistency': {
                        'contradictionCandidates': [],
                        'evidenceChains': [],
                        'lastCheckStage': None,
                        'openCriticalIssues': [],
                    },
                    'revisionActions': [],
                    'styleRisk': {
                        'clichePatterns': [],
                        'lastCokeScore': None,
                        'noveltyAxes': [],
                        'lastClicheScanStage': None,
                    },
                },
            )

    def test_load_state_preserves_partial_narrative_intelligence_values_and_fills_missing_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / '测试小说'
            project.mkdir()
            self.write_state(
                project,
                {
                    'project': {'title': '测试小说', 'rootPath': str(project)},
                    'workflow': {'currentStage': 'discovery'},
                    'narrativeIntelligence': {
                        'timeline': {
                            'enabled': True,
                            'lastTouchedChapters': ['第3章'],
                        },
                        'cfpg': {
                            'foreshadowTriples': [{'setup': '黑箱', 'payoff': '来源揭示'}],
                            'tripleCounts': {'fulfilled': 2},
                        },
                        'theoryOfMind': {
                            'characterBeliefs': [{'character': '主角', 'belief': '盟友可靠'}],
                        },
                        'consistency': {
                            'evidenceChains': [{'claim': '黑箱存在', 'evidence': ['第1章线索']}],
                            'lastCheckStage': 'proofreading',
                        },
                        'revisionActions': [{'action': 'tighten_clue_chain'}],
                        'styleRisk': {
                            'lastCokeScore': 0.42,
                        },
                    },
                },
            )

            state = self.load_persisted_state(project)
            narrative_intelligence = state['narrativeIntelligence']

            self.assertTrue(narrative_intelligence['timeline']['enabled'])
            self.assertEqual(narrative_intelligence['timeline']['lastTouchedChapters'], ['第3章'])
            self.assertIsNone(narrative_intelligence['timeline']['lastUpdatedBatch'])
            self.assertEqual(narrative_intelligence['timeline']['openTemporalRisks'], [])

            self.assertEqual(
                narrative_intelligence['cfpg']['foreshadowTriples'],
                [{'setup': '黑箱', 'payoff': '来源揭示'}],
            )
            self.assertEqual(
                narrative_intelligence['cfpg']['tripleCounts'],
                {
                    'total': 0,
                    'pending': 0,
                    'fulfilled': 2,
                    'broken': 0,
                    'expired': 0,
                },
            )
            self.assertIsNone(narrative_intelligence['cfpg']['lastUpdatedBatch'])

            self.assertEqual(
                narrative_intelligence['theoryOfMind']['characterBeliefs'],
                [{'character': '主角', 'belief': '盟友可靠'}],
            )
            self.assertEqual(narrative_intelligence['theoryOfMind']['beliefConflicts'], [])
            self.assertIsNone(narrative_intelligence['theoryOfMind']['lastUpdatedBatch'])

            self.assertEqual(
                narrative_intelligence['consistency']['evidenceChains'],
                [{'claim': '黑箱存在', 'evidence': ['第1章线索']}],
            )
            self.assertEqual(narrative_intelligence['consistency']['contradictionCandidates'], [])
            self.assertEqual(narrative_intelligence['consistency']['lastCheckStage'], 'proofreading')
            self.assertEqual(narrative_intelligence['consistency']['openCriticalIssues'], [])

            self.assertEqual(
                narrative_intelligence['revisionActions'],
                [{'action': 'tighten_clue_chain'}],
            )
            self.assertEqual(narrative_intelligence['styleRisk']['clichePatterns'], [])
            self.assertEqual(narrative_intelligence['styleRisk']['lastCokeScore'], 0.42)
            self.assertEqual(narrative_intelligence['styleRisk']['noveltyAxes'], [])
            self.assertIsNone(narrative_intelligence['styleRisk']['lastClicheScanStage'])


if __name__ == '__main__':
    unittest.main()
