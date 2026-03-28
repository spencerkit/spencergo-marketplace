import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / 'skills/research-studio/scripts'
EXAMPLES = ROOT / 'skills/research-studio/examples'
ASSETS = ROOT / 'skills/research-studio/assets'


class ResearchStudioRenderReportTest(unittest.TestCase):
    def load_script_module(self, name: str):
        scripts_path = str(SCRIPTS)
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        return importlib.import_module(name)

    def sample_payload(self, layout_type: str = 'market') -> dict:
        return {
            'title': 'AI Coding Market Scan',
            'subtitle': f'2026-03-28 · {layout_type}',
            'layout_type': layout_type,
            'executive_summary': 'Summary',
            'research_question': 'Question',
            'core_conclusion': 'Conclusion',
            'conclusion_badges': [{'label': '多来源支持', 'level': 'ok'}],
            'key_evidence': [
                {
                    'title': 'Evidence 1',
                    'body': 'Body',
                    'source': 'Source',
                    'status': '已有明确来源',
                }
            ],
            'dimensions': [
                {
                    'title': 'Demand',
                    'body': 'Strong',
                    'source': 'Source',
                    'status': '多来源支持',
                }
            ],
            'charts': [
                {
                    'type': 'bar',
                    'title': 'Demand',
                    'data': {'labels': ['A'], 'values': [1]},
                }
            ],
            'uncertainty': 'Unknowns',
            'gaps': ['Gap 1'],
            'risk_block': 'Risk',
            'action_block': 'Action',
            'recommendations': 'Next',
            'sources': [
                {
                    'name': 'Official',
                    'detail': 'Details',
                    'type': '官方',
                    'status': '已有明确来源',
                }
            ],
            'takeaways': [
                {'label': '核心判断', 'value': 'Go'},
                {'label': '优先方向', 'value': 'API'},
                {'label': '最大风险', 'value': 'Noise'},
            ],
            'metrics': [{'label': 'Market', 'value': '$1B'}],
            'decision_panel': 'Proceed carefully',
            'footer_note': 'Research Studio SVG Report',
        }

    def test_render_svg_report_outputs_svg_root_for_market_layout(self):
        module = self.load_script_module('render_report')

        svg = module.render_svg_report(self.sample_payload('market'))

        self.assertTrue(svg.startswith('<svg'))
        self.assertIn('Research Studio · Market Layout', svg)
        self.assertIn('AI Coding Market Scan', svg)

    def test_render_svg_report_switches_layout_copy_for_project(self):
        module = self.load_script_module('render_report')

        svg = module.render_svg_report(self.sample_payload('project'))

        self.assertIn('Research Studio · Project Layout', svg)

    def test_render_markdown_report_outputs_headings_and_sources(self):
        module = self.load_script_module('render_report')

        markdown = module.render_markdown_report(self.sample_payload('platform'))

        self.assertTrue(markdown.startswith('# AI Coding Market Scan'))
        self.assertIn('## 执行摘要', markdown)
        self.assertIn('## 来源说明', markdown)

    def test_cli_writes_svg_and_markdown_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_json = Path(tmpdir) / 'report.json'
            input_json.write_text(json.dumps(self.sample_payload()), encoding='utf-8')
            svg_output = Path(tmpdir) / 'report.svg'
            markdown_output = Path(tmpdir) / 'report.md'

            result = subprocess.run(
                [
                    'python3',
                    str(SCRIPTS / 'render_report.py'),
                    str(input_json),
                    str(svg_output),
                    '--markdown-output',
                    str(markdown_output),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(svg_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_market_layout_places_metrics_before_decision_panel(self):
        module = self.load_script_module('render_report')

        sections = module.build_section_plan(self.sample_payload('market'))
        keys = [section.key for section in sections]

        self.assertLess(keys.index('metrics'), keys.index('decision_panel'))

    def test_project_layout_places_risk_action_before_evidence(self):
        module = self.load_script_module('render_report')

        sections = module.build_section_plan(self.sample_payload('project'))
        keys = [section.key for section in sections]

        self.assertLess(keys.index('risk_action'), keys.index('key_evidence'))

    def test_wrap_text_splits_long_paragraph_into_multiple_lines(self):
        module = self.load_script_module('render_report')

        lines = module.wrap_text('This is a long sentence that should wrap', max_chars=12)

        self.assertGreater(len(lines), 1)

    def test_paragraph_block_height_grows_with_more_lines(self):
        module = self.load_script_module('render_report')

        short = module.measure_paragraph_block('short text', width=320)
        long = module.measure_paragraph_block('long text ' * 20, width=320)

        self.assertGreater(long.height, short.height)

    def test_svg_report_renders_bar_chart_markup(self):
        module = self.load_script_module('render_report')

        svg = module.render_svg_report(self.sample_payload())

        self.assertIn('Demand', svg)
        self.assertIn('A', svg)

    def test_unknown_chart_type_falls_back_to_text_placeholder(self):
        module = self.load_script_module('render_report')
        payload = self.sample_payload()
        payload['charts'] = [{'type': 'unknown', 'title': 'X', 'data': {}}]

        svg = module.render_svg_report(payload)

        self.assertIn('暂无可视化内容', svg)

    def test_markdown_report_contains_core_sections_in_order(self):
        module = self.load_script_module('render_report')

        markdown = module.render_markdown_report(self.sample_payload())

        self.assertLess(markdown.index('## 研究问题'), markdown.index('## 核心结论'))
        self.assertLess(markdown.index('## 核心依据'), markdown.index('## 多维度分析'))
        self.assertIn('## 不确定性与待补充', markdown)

    def test_build_png_export_command_targets_svg_input(self):
        module = self.load_script_module('render_report')

        svg_path = Path('/tmp/report.svg')
        png_path = Path('/tmp/report.png')
        command = module.build_png_export_command(svg_path, png_path)

        self.assertEqual(command[0], 'resvg')
        self.assertIn(str(svg_path), command)
        self.assertIn(str(png_path), command)

    def test_sample_payload_smoke_render(self):
        module = self.load_script_module('render_report')

        payload = json.loads((EXAMPLES / 'sample-report.json').read_text(encoding='utf-8'))

        self.assertTrue(module.render_svg_report(payload).startswith('<svg'))
        self.assertTrue(module.render_markdown_report(payload).startswith('# '))

    def test_svg_report_uses_mobile_width_and_renders_core_sections(self):
        module = self.load_script_module('render_report')

        svg = module.render_svg_report(self.sample_payload('market'))

        self.assertIn('width="750"', svg)
        self.assertIn('执行摘要', svg)
        self.assertIn('研究问题', svg)
        self.assertIn('核心结论', svg)
        self.assertIn('来源说明', svg)
        self.assertIn('Proceed carefully', svg)

    def test_platform_layout_renders_risk_block_before_uncertainty(self):
        module = self.load_script_module('render_report')

        svg = module.render_svg_report(self.sample_payload('platform'))

        self.assertLess(svg.index('关键风险'), svg.index('不确定性与待补充'))

    def test_markdown_report_includes_recommendations_and_risk_action_blocks(self):
        module = self.load_script_module('render_report')

        markdown = module.render_markdown_report(self.sample_payload('project'))

        self.assertIn('## 关键风险', markdown)
        self.assertIn('## 下一步动作', markdown)
        self.assertIn('## 理性建议', markdown)

    def test_main_can_request_png_export(self):
        module = self.load_script_module('render_report')

        with tempfile.TemporaryDirectory() as tmpdir:
            input_json = Path(tmpdir) / 'report.json'
            input_json.write_text(json.dumps(self.sample_payload()), encoding='utf-8')
            svg_output = Path(tmpdir) / 'report.svg'
            markdown_output = Path(tmpdir) / 'report.md'
            png_output = Path(tmpdir) / 'report.png'

            with mock.patch.object(module, 'export_png') as export_png:
                module.main([
                    str(input_json),
                    str(svg_output),
                    '--markdown-output',
                    str(markdown_output),
                    '--png-output',
                    str(png_output),
                ])

            export_png.assert_called_once_with(svg_output, png_output)

    def test_svg_template_assets_use_mobile_width(self):
        market_svg = (ASSETS / 'report-template-market.svg').read_text(encoding='utf-8')
        project_svg = (ASSETS / 'report-template-project.svg').read_text(encoding='utf-8')
        platform_svg = (ASSETS / 'report-template-platform.svg').read_text(encoding='utf-8')

        self.assertIn('width="750"', market_svg)
        self.assertIn('width="750"', project_svg)
        self.assertIn('width="750"', platform_svg)


if __name__ == '__main__':
    unittest.main()
