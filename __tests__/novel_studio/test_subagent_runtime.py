import hashlib
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


class NovelStudioSubagentRuntimeTest(unittest.TestCase):
    def load_script_module(self, name: str):
        scripts_path = str(SCRIPTS)
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        return importlib.import_module(name)

    def snapshot_files(self, project: Path) -> dict[str, dict[str, object]]:
        snapshot = {}
        for path in sorted(project.rglob('*')):
            if path.is_file():
                relpath = path.relative_to(project).as_posix()
                snapshot[relpath] = {
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'size': path.stat().st_size,
                }
        return snapshot

    def create_runtime_project(
        self,
        root: Path,
        *,
        current_stage: str,
        approvals: dict | None = None,
        batch: dict | None = None,
        manuscript_files: dict[str, str] | None = None,
    ) -> Path:
        project = root / '测试小说'
        project.mkdir()
        (project / '00A_热点扫描.md').write_text('# scan\n', encoding='utf-8')
        (project / '00B_用户偏好.md').write_text('# intake\n', encoding='utf-8')
        (project / '00_选题报告.md').write_text('# topic\n', encoding='utf-8')
        (project / '00C_底盘与切口决策.md').write_text(
            '# 底盘与切口\n\n'
            '## 主赛道\n- 规则异变都市\n\n'
            '## 辅助风味\n- 悬疑调查\n\n'
            '## 平台模式\n- 起点模式\n',
            encoding='utf-8',
        )
        (project / '01_想法.md').write_text('# idea\n', encoding='utf-8')
        (project / '01A_风格圣经.md').write_text(
            '# 风格圣经\n\n'
            '## 平台模式\n- 起点模式\n\n'
            '## 叙述基调\n- 冷峻、克制、信息前推\n',
            encoding='utf-8',
        )
        (project / '01B_总主线与卷级推进.md').write_text(
            '# 总主线\n\n'
            '主角为了查清失序区事故真相，必须不断深入更高风险区域，而越接近真相越失去正常生活。\n',
            encoding='utf-8',
        )
        (project / '02_大纲.md').write_text('# outline\n\n主线推进', encoding='utf-8')
        (project / '03_人物小传.md').write_text('# roles\n\n主角：林川', encoding='utf-8')
        (project / '04A_开篇设计.md').write_text(
            '# 开篇设计\n\n'
            '## 前三章任务\n- 第1章点火\n- 第2章显规\n- 第3章留钩\n',
            encoding='utf-8',
        )
        (project / '05_本轮章节规划.md').write_text(
            '## 本轮范围\n- 第1章\n\n'
            '## 本轮写作重点\n- 开篇立钩子\n\n'
            '## 逐章规划\n'
            '### 第1章\n'
            '- 本章目标：建立主角处境\n'
            '- 出场人物：林川\n'
            '- 高潮点：结尾反转\n'
            '- 吸引点：隐藏实力\n',
            encoding='utf-8',
        )
        (project / '05_前情回顾.md').write_text(
            '## 当前已推进到的位置\n- 开篇\n\n'
            '## 最近一轮发生的关键事件\n- 无\n\n'
            '## 当前未回收的伏笔 / 悬念\n- 黑箱来历\n\n'
            '## 下一轮写作必须记住的点\n- 主角表面隐忍\n',
            encoding='utf-8',
        )
        (project / '05B_世界规则账本.md').write_text(
            '# 世界规则账本\n\n- 失序区只在夜间扩张\n',
            encoding='utf-8',
        )
        (project / '05C_伏笔回收台账.md').write_text(
            '# 伏笔回收台账\n\n- 黑箱来源：未回收\n',
            encoding='utf-8',
        )
        (project / '05D_关系状态表.md').write_text(
            '# 关系状态表\n\n- 林川 / 顾遥：互相试探\n',
            encoding='utf-8',
        )
        (project / '05E_能力与资源变化表.md').write_text(
            '# 能力与资源变化表\n\n- 黑箱权限：一级\n',
            encoding='utf-8',
        )
        characters = project / 'characters'
        characters.mkdir()
        (characters / '林川.md').write_text('# 林川\n\n性格：隐忍', encoding='utf-8')

        manuscript = project / 'manuscript'
        manuscript.mkdir()
        for relpath, content in (manuscript_files or {}).items():
            path = project / relpath
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')

        state = {
            'project': {'title': '测试小说', 'rootPath': str(project)},
            'workflow': {
                'currentStage': current_stage,
                'currentSubstage': None,
                'lastCompletedStage': 'character-system',
                'nextStage': current_stage,
                'status': 'in_progress',
            },
            'approvals': {
                'characterApproved': True,
                'planningApproved': True,
                'discoveryApproved': True,
                'openingApproved': True,
                'draftingApproved': False,
                'polishingApproved': False,
                'proofreadingApproved': False,
                'finalApproved': False,
            },
            'artifacts': {},
            'batch': {
                'active': True,
                'chapterRange': '第1章',
                'chapterCount': 1,
                'scopeConfirmed': True,
                'chapterPlanExists': True,
                'chapterPlanApproved': True,
                'draftComplete': False,
                'polishingComplete': False,
                'proofreadingComplete': False,
                'recapUpdated': False,
                'awaitingNextBatchDecision': False,
                'focus': None,
                'attractionPoints': ['隐藏实力'],
                'climaxTarget': '结尾反转',
            },
            'review': {
                'currentGate': None,
            },
            'revision': {
                'active': False,
                'currentRevisionGate': None,
                'awaitingUserApproval': False,
            },
            'blockingIssues': [],
            'notes': {
                'platformProfile': '起点模式',
                'primaryTrack': '规则异变都市',
                'secondaryFlavor': '悬疑调查',
                'styleBibleVersion': 'v1',
            },
        }
        if approvals:
            state['approvals'].update(approvals)
        if batch:
            state['batch'].update(batch)
        (project / '.novel-state.json').write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        return project

    def write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    def canonical_json(self, payload: object) -> str:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

    def digest_payload(self, payload: object) -> str:
        return hashlib.sha256(self.canonical_json(payload).encode('utf-8')).hexdigest()

    def refresh_bundle_digests(self, bundle: dict) -> None:
        validation = bundle['validationContext']
        validation['executionPackageDigest'] = self.digest_payload(bundle['executionPackage'])
        validation['baselineFilesDigest'] = self.digest_payload(validation['baselineFiles'])
        validation['bundleFingerprint'] = self.digest_payload(
            {
                'projectRoot': validation.get('projectRoot'),
                'stage': validation.get('stage'),
                'batchRange': validation.get('batchRange'),
                'executionPackageDigest': validation.get('executionPackageDigest'),
                'baselineFilesDigest': validation.get('baselineFilesDigest'),
            }
        )

    def set_proofreading_bundle_report_contract(self, bundle: dict) -> None:
        bundle['executionPackage']['targetFiles'] = ['05A_本轮校对报告.md']
        bundle['executionPackage']['overwriteFlag'] = True
        bundle['executionPackage']['outputContract']['mustWriteFiles'] = ['05A_本轮校对报告.md']
        bundle['executionPackage']['mustNotModify'] = sorted(
            path
            for path in bundle['validationContext']['baselineFiles'].keys()
            if path != '05A_本轮校对报告.md'
        )

    def needs_clarification_result(self, *, summary: str = '需要补充上下文') -> dict:
        return {
            'status': 'needs_clarification',
            'changedFiles': [],
            'createdFiles': [],
            'blockedReasons': [],
            'summary': summary,
            'notesForNextStage': '',
            'risks': [],
        }

    def write_proofreading_report(self, project: Path, content: str | None = None) -> None:
        (project / '05A_本轮校对报告.md').write_text(
            content or '# 05A_本轮校对报告\n\n- judgment: acceptable\n- summary: 已完成校对\n',
            encoding='utf-8',
        )

    def completed_proofreading_result(self, *, summary: str = '已完成校对') -> dict:
        return {
            'status': 'completed',
            'changedFiles': [],
            'createdFiles': ['05A_本轮校对报告.md'],
            'blockedReasons': [],
            'summary': summary,
            'notesForNextStage': '',
            'risks': [],
            'judgment': 'acceptable',
            'continuity': '通过',
            'logic': '通过',
            'characterOOC': '无',
            'blockers': [],
            'fixDirection': '无需处理',
        }

    def test_build_drafting_package_includes_required_inputs_and_validation_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_runtime_project(Path(tmp), current_stage='drafting')
            result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            bundle = json.loads(result.stdout)
            package = bundle['executionPackage']
            self.assertEqual(package['taskType'], 'drafting')
            self.assertEqual(package['targetFiles'], ['manuscript/第1章_开端.md'])
            self.assertIn('outline', package['requiredInputs'])
            self.assertIn('batchPlan', package['requiredInputs'])
            self.assertIn('characterFiles', package['requiredInputs'])
            self.assertIn('styleBible', package['requiredInputs'])
            self.assertIn('mainlineSpec', package['requiredInputs'])
            self.assertIn('platformProfile', package['requiredInputs'])
            self.assertIn('trackGuide', package['requiredInputs'])
            self.assertIn('ledgerSnapshot', package['requiredInputs'])
            self.assertIn('baselineFiles', bundle['validationContext'])
            self.assertIn('02_大纲.md', bundle['validationContext']['baselineFiles'])

    def test_build_drafting_package_includes_required_chapter_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_runtime_project(Path(tmp), current_stage='drafting')
            result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            bundle = json.loads(result.stdout)
            self.assertEqual(
                bundle['executionPackage']['requiredInputs']['chapterLabels'],
                ['第1章'],
            )

    def test_build_package_rejects_drafting_without_opening_gate_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_runtime_project(
                Path(tmp),
                current_stage='drafting',
                approvals={'openingApproved': False},
            )
            result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Opening gate not explicitly approved yet', result.stderr + result.stdout)

    def test_build_polishing_package_requires_polishing_focus(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_runtime_project(
                Path(tmp),
                current_stage='polishing',
                batch={'draftComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'polishing',
                '--batch-range',
                '第1章',
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('polishingFocus', result.stderr + result.stdout)

    def test_build_proofreading_package_forces_report_only_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_runtime_project(
                Path(tmp),
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            bundle = json.loads(result.stdout)
            package = bundle['executionPackage']
            self.assertEqual(package['targetFiles'], ['05A_本轮校对报告.md'])
            self.assertTrue(package['overwriteFlag'])
            self.assertNotIn('05A_本轮校对报告.md', package['mustNotModify'])
            self.assertIn('manuscript/第1章_开端.md', package['mustNotModify'])

    def test_build_proofreading_package_targets_formal_report_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
                batch={'draftComplete': True, 'polishingComplete': True},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)
            bundle = json.loads(bundle_result.stdout)
            self.assertEqual(bundle['executionPackage']['targetFiles'], ['05A_本轮校对报告.md'])

    def test_proofreading_completed_result_must_write_formal_report_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
                batch={'draftComplete': True, 'polishingComplete': True},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)
            bundle = json.loads(bundle_result.stdout)
            self.assertEqual(bundle['executionPackage']['targetFiles'], ['05A_本轮校对报告.md'])

    def test_validate_rejects_blocked_result_with_file_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.write_json(bundle_file, bundle)

            (project / 'manuscript' / '第1章_开端.md').write_text('# 第一章\n\n正文', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'blocked',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': ['需要更多上下文'],
                    'summary': '未完成',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('non-completed status', validate.stderr + validate.stdout)

    def test_validate_rejects_reported_diff_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.write_json(bundle_file, bundle)

            (project / 'manuscript' / '第1章_开端.md').write_text('# 第一章\n\n正文', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': [],
                    'summary': '已完成',
                    'notesForNextStage': '进入润色',
                    'risks': [],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('diff mismatch', validate.stderr + validate.stdout)

    def test_validate_rejects_drafting_overwrite_when_flag_is_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='drafting',
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n旧正文'},
            )
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            relpath = 'manuscript/第1章_开端.md'
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                relpath,
                '--overwrite',
                'true',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)
            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['overwriteFlag'] = False
            self.refresh_bundle_digests(bundle)
            self.write_json(bundle_file, bundle)
            (project / relpath).write_text('# 第一章\n\n新正文', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [relpath],
                    'createdFiles': [],
                    'blockedReasons': [],
                    'summary': '覆盖了现有章节',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('overwrite flag is false', validate.stderr + validate.stdout)


    def test_validate_rejects_drafting_completed_without_touching_must_write_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            relpath = 'manuscript/第1章_开端.md'
            project = self.create_runtime_project(
                root,
                current_stage='drafting',
                manuscript_files={relpath: '# 第一章\n\n旧正文'},
            )
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            baseline = self.snapshot_files(project)

            bundle = {
                'executionPackage': {
                    'taskType': 'drafting',
                    'projectRoot': str(project),
                    'stage': 'drafting',
                    'batchRange': '第1章',
                    'targetFiles': [relpath],
                    'overwriteFlag': True,
                    'requiredInputs': {
                        'batchRange': '第1章',
                        'outline': (project / '02_大纲.md').read_text(encoding='utf-8'),
                        'batchPlan': (project / '05_本轮章节规划.md').read_text(encoding='utf-8'),
                        'chapterLabels': ['第1章'],
                        'characterFiles': {
                            '03_人物小传.md': (project / '03_人物小传.md').read_text(encoding='utf-8'),
                        },
                        'styleBible': (project / '01A_风格圣经.md').read_text(encoding='utf-8'),
                        'mainlineSpec': (project / '01B_总主线与卷级推进.md').read_text(encoding='utf-8'),
                        'openingDesign': (project / '04A_开篇设计.md').read_text(encoding='utf-8'),
                        'platformProfile': '起点模式',
                        'trackGuide': (project / '00C_底盘与切口决策.md').read_text(encoding='utf-8'),
                        'ledgerSnapshot': {
                            '05B_世界规则账本.md': (project / '05B_世界规则账本.md').read_text(encoding='utf-8'),
                            '05C_伏笔回收台账.md': (project / '05C_伏笔回收台账.md').read_text(encoding='utf-8'),
                            '05D_关系状态表.md': (project / '05D_关系状态表.md').read_text(encoding='utf-8'),
                            '05E_能力与资源变化表.md': (project / '05E_能力与资源变化表.md').read_text(encoding='utf-8'),
                        },
                        'recap': None,
                    },
                    'mustNotModify': [path for path in baseline.keys() if path != relpath],
                    'outputContract': {
                        'requiredReturnFields': [
                            'status',
                            'changedFiles',
                            'createdFiles',
                            'blockedReasons',
                            'summary',
                            'notesForNextStage',
                            'risks',
                        ],
                        'mustWriteFiles': [relpath],
                    },
                    'acceptanceHints': ['只写批准的 manuscript 文件', '不要修改规划和状态文件'],
                },
                'validationContext': {
                    'projectRoot': str(project),
                    'stage': 'drafting',
                    'batchRange': '第1章',
                    'baselineFiles': baseline,
                    'executionPackageDigest': '',
                    'baselineFilesDigest': '',
                    'bundleFingerprint': '',
                },
            }
            self.refresh_bundle_digests(bundle)
            self.write_json(bundle_file, bundle)
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': [],
                    'summary': '宣称完成但没有落笔',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('completed result did not touch required output files', validate.stderr + validate.stdout)

    def test_validate_rejects_polishing_completed_without_touching_must_write_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            relpath = 'manuscript/第1章_开端.md'
            project = self.create_runtime_project(
                root,
                current_stage='polishing',
                batch={'draftComplete': True},
                manuscript_files={relpath: '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'polishing',
                '--batch-range',
                '第1章',
                '--polishing-focus',
                '压缩开篇节奏',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, json.loads(bundle_result.stdout))
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': [],
                    'summary': '宣称完成但未修改章节',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('completed result did not touch required output files', validate.stderr + validate.stdout)

    def test_validate_rejects_non_string_risks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, json.loads(bundle_result.stdout))
            self.write_json(
                result_file,
                {
                    'status': 'needs_clarification',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': [],
                    'summary': '需要补充上下文',
                    'notesForNextStage': '',
                    'risks': ['风险A', 2],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('risks items must be strings', validate.stderr + validate.stdout)

    def test_validate_rejects_non_string_proofreading_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            self.refresh_bundle_digests(bundle)
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['05A_本轮校对报告.md'],
                    'blockedReasons': [],
                    'summary': '已完成校对',
                    'notesForNextStage': '',
                    'risks': [],
                    'judgment': 'acceptable',
                    'continuity': '通过',
                    'logic': '通过',
                    'characterOOC': '无',
                    'blockers': ['小问题', 3],
                    'fixDirection': '无需处理',
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('proofreading blockers items must be strings', validate.stderr + validate.stdout)

    def test_validate_rejects_bundle_internal_stage_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)
            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['taskType'] = 'polishing'
            bundle['validationContext']['stage'] = 'proofreading'
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(
                result_file,
                {
                    'status': 'needs_clarification',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': ['等待更多上下文'],
                    'summary': '未执行',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('bundle stage metadata mismatch', validate.stderr + validate.stdout)

    def test_validate_rejects_proofreading_file_modification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.write_json(bundle_file, bundle)

            (project / 'manuscript' / '第1章_开端.md').write_text('# 第一章\n\n改动后的正文', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': ['manuscript/第1章_开端.md'],
                    'createdFiles': [],
                    'blockedReasons': [],
                    'summary': '已完成校对',
                    'notesForNextStage': '建议回到润色',
                    'risks': [],
                    'judgment': 'needs revision',
                    'continuity': '存在小断点',
                    'logic': '基本成立',
                    'characterOOC': '无明显 OOC',
                    'blockers': ['结尾信息缺口'],
                    'fixDirection': '补强结尾收束',
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('forbidden files were modified', validate.stderr + validate.stdout)

    def test_validate_rejects_tampered_required_return_fields_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['outputContract']['requiredReturnFields'] = ['status']
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('outputContract.requiredReturnFields', validate.stderr + validate.stdout)

    def test_validate_rejects_tampered_proofreading_required_stage_fields_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            bundle['executionPackage']['outputContract']['requiredStageFields'] = ['judgment']
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            self.write_json(result_file, self.completed_proofreading_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('outputContract.requiredStageFields', validate.stderr + validate.stdout)

    def test_validate_rejects_output_contract_must_write_files_mismatch_target_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['outputContract']['mustWriteFiles'] = []
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            (project / 'manuscript' / '第1章_开端.md').write_text('# 第一章\n\n正文', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['manuscript/第1章_开端.md'],
                    'blockedReasons': [],
                    'summary': '已完成第1章初稿',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('outputContract.mustWriteFiles', validate.stderr + validate.stdout)

    def test_validate_rejects_drafting_bundle_without_target_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['targetFiles'] = []
            bundle['executionPackage']['mustNotModify'] = sorted(
                set(bundle['executionPackage']['mustNotModify'] + ['manuscript/第1章_开端.md'])
            )
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('drafting targetFiles', validate.stderr + validate.stdout)

    def test_validate_rejects_drafting_bundle_with_non_manuscript_target_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['targetFiles'] = ['notes/第1章.md']
            bundle['executionPackage']['mustNotModify'] = [
                path
                for path in bundle['executionPackage']['mustNotModify']
                if path != 'notes/第1章.md'
            ]
            bundle['executionPackage']['outputContract']['mustWriteFiles'] = ['notes/第1章.md']
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('drafting targetFiles must stay under manuscript/', validate.stderr + validate.stdout)

    def test_validate_rejects_proofreading_bundle_with_noncanonical_target_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            bundle['executionPackage']['targetFiles'] = ['manuscript/第1章_开端.md']
            bundle['executionPackage']['outputContract']['mustWriteFiles'] = ['manuscript/第1章_开端.md']
            bundle['executionPackage']['mustNotModify'] = []
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            self.write_json(result_file, self.completed_proofreading_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn(
                'proofreading targetFiles must be exactly [05A_本轮校对报告.md]',
                validate.stderr + validate.stdout,
            )

    def test_validate_rejects_proofreading_bundle_with_overwrite_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            bundle['executionPackage']['overwriteFlag'] = False
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            self.write_json(result_file, self.completed_proofreading_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('proofreading overwriteFlag must be true', validate.stderr + validate.stdout)

    def test_validate_rejects_drafting_bundle_with_missing_outline_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            del bundle['executionPackage']['requiredInputs']['outline']
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('requiredInputs.outline', validate.stderr + validate.stdout)

    def test_validate_rejects_drafting_bundle_with_missing_style_bible_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            del bundle['executionPackage']['requiredInputs']['styleBible']
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('requiredInputs.styleBible', validate.stderr + validate.stdout)

    def test_validate_rejects_polishing_bundle_without_polishing_focus_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                Path(tmp),
                current_stage='polishing',
                batch={'draftComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'polishing',
                '--batch-range',
                '第1章',
                '--polishing-focus',
                '压缩开篇节奏',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            del bundle['executionPackage']['requiredInputs']['polishingFocus']
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('requiredInputs.polishingFocus', validate.stderr + validate.stdout)

    def test_validate_rejects_proofreading_bundle_without_manuscript_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            del bundle['executionPackage']['requiredInputs']['manuscriptFiles']
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            self.write_json(result_file, self.completed_proofreading_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('requiredInputs.manuscriptFiles', validate.stderr + validate.stdout)

    def test_validate_rejects_validation_context_batch_range_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['validationContext']['batchRange'] = '第2章'
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('bundle stage metadata mismatch', validate.stderr + validate.stdout)

    def test_validate_rejects_validation_context_project_root_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['validationContext']['projectRoot'] = str(root / '别的项目')
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('project root mismatch between validation context and project', validate.stderr + validate.stdout)

    def test_validate_rejects_baseline_snapshot_with_short_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            first_relpath = next(iter(bundle['validationContext']['baselineFiles']))
            bundle['validationContext']['baselineFiles'][first_relpath]['sha256'] = 'abc123'
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('.sha256 must be a 64-character lowercase hex string', validate.stderr + validate.stdout)

    def test_validate_rejects_baseline_snapshot_with_boolean_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            first_relpath = next(iter(bundle['validationContext']['baselineFiles']))
            bundle['validationContext']['baselineFiles'][first_relpath]['size'] = True
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('.size must be a non-negative integer', validate.stderr + validate.stdout)

    def test_validate_rejects_drafting_bundle_with_must_not_modify_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['mustNotModify'] = [
                path
                for path in bundle['executionPackage']['mustNotModify']
                if path != '02_大纲.md'
            ]
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('mustNotModify must exactly match baselineFiles minus targetFiles', validate.stderr + validate.stdout)

    def test_validate_rejects_drafting_bundle_with_tampered_outline_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['requiredInputs']['outline'] = '# 被篡改的大纲\n\n假的内容'
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('requiredInputs.outline must match baseline snapshot for 02_大纲.md', validate.stderr + validate.stdout)

    def test_validate_rejects_polishing_bundle_with_target_file_outside_baseline_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='polishing',
                batch={'draftComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'polishing',
                '--batch-range',
                '第1章',
                '--polishing-focus',
                '压缩开篇节奏',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['targetFiles'] = ['manuscript/第2章_新增.md']
            bundle['executionPackage']['requiredInputs']['manuscriptFiles'] = {
                'manuscript/第2章_新增.md': '# 第二章\n\n伪造输入'
            }
            bundle['executionPackage']['outputContract']['mustWriteFiles'] = ['manuscript/第2章_新增.md']
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('polishing targetFiles must refer to existing baseline files', validate.stderr + validate.stdout)

    def test_validate_rejects_proofreading_bundle_with_nonbaseline_manuscript_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            bundle['executionPackage']['requiredInputs']['manuscriptFiles'] = {
                'manuscript/第9章_伪造.md': '# 第九章\n\n伪造内容'
            }
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            self.write_json(result_file, self.completed_proofreading_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn(
                'requiredInputs.manuscriptFiles.manuscript/第9章_伪造.md must reference an existing baseline file',
                validate.stderr + validate.stdout,
            )

    def test_validate_rejects_tampered_acceptance_hints_even_with_refreshed_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['acceptanceHints'] = ['被篡改的提示']
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('acceptanceHints must match canonical stage hints', validate.stderr + validate.stdout)

    def test_build_drafting_package_rejects_duplicate_target_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_runtime_project(Path(tmp), current_stage='drafting')
            result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('targetFiles contains duplicate entries', result.stderr + result.stdout)

    def test_validate_rejects_duplicate_must_not_modify_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            duplicate_path = bundle['executionPackage']['mustNotModify'][0]
            bundle['executionPackage']['mustNotModify'].append(duplicate_path)
            self.refresh_bundle_digests(bundle)
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('mustNotModify contains duplicate entries', validate.stderr + validate.stdout)

    def test_validate_rejects_duplicate_changed_files_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.write_json(bundle_file, bundle)
            (project / 'manuscript' / '第1章_开端.md').write_text('# 第一章\n\n正文', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': ['manuscript/第1章_开端.md', 'manuscript/第1章_开端.md'],
                    'createdFiles': [],
                    'blockedReasons': [],
                    'summary': '已完成',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('changedFiles contains duplicate entries', validate.stderr + validate.stdout)

    def test_validate_rejects_stale_execution_package_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['executionPackage']['acceptanceHints'].append('额外篡改提示')
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('validationContext.executionPackageDigest mismatch', validate.stderr + validate.stdout)

    def test_validate_rejects_stale_baseline_files_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            first_relpath = next(iter(bundle['validationContext']['baselineFiles']))
            bundle['validationContext']['baselineFiles'][first_relpath]['sha256'] = '0' * 64
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('validationContext.baselineFilesDigest mismatch', validate.stderr + validate.stdout)

    def test_validate_rejects_stale_bundle_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle = json.loads(bundle_result.stdout)
            bundle['validationContext']['bundleFingerprint'] = 'f' * 64
            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, bundle)
            self.write_json(result_file, self.needs_clarification_result())

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('validationContext.bundleFingerprint mismatch', validate.stderr + validate.stdout)


    def test_validate_rejects_blocked_result_without_blocked_reasons(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, json.loads(bundle_result.stdout))
            self.write_json(
                result_file,
                {
                    'status': 'blocked',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': [],
                    'summary': '未执行',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('blocked status requires non-empty blockedReasons', validate.stderr + validate.stdout)

    def test_validate_rejects_needs_clarification_without_blocked_reasons(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            self.write_json(bundle_file, json.loads(bundle_result.stdout))
            self.write_json(
                result_file,
                {
                    'status': 'needs_clarification',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': [],
                    'summary': '缺少必要上下文',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('needs_clarification status requires non-empty blockedReasons', validate.stderr + validate.stdout)

    def test_validate_rejects_completed_result_with_blocked_reasons(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            self.refresh_bundle_digests(bundle)
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            result = self.completed_proofreading_result()
            result['blockedReasons'] = ['还有阻塞']
            self.write_json(result_file, result)

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('completed status must not include blockedReasons', validate.stderr + validate.stdout)


    def test_validate_rejects_proofreading_acceptable_with_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            self.refresh_bundle_digests(bundle)
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            result = self.completed_proofreading_result()
            result['blockers'] = ['仍有连续性问题']
            result['fixDirection'] = '补一轮连续性修正'
            self.write_json(result_file, result)

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('proofreading blockers must be empty when judgment is acceptable', validate.stderr + validate.stdout)

    def test_validate_rejects_proofreading_conditionally_acceptable_with_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            self.refresh_bundle_digests(bundle)
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            result = self.completed_proofreading_result()
            result['judgment'] = 'conditionally acceptable'
            result['risks'] = ['结尾收束略弱，建议下一轮补强']
            result['blockers'] = ['仍有关键信息缺口']
            result['fixDirection'] = '补强结尾收束并复查逻辑'
            self.write_json(result_file, result)

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn(
                'proofreading blockers must be empty when judgment is conditionally acceptable',
                validate.stderr + validate.stdout,
            )

    def test_validate_rejects_proofreading_conditionally_acceptable_without_risks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            self.refresh_bundle_digests(bundle)
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            result = self.completed_proofreading_result()
            result['judgment'] = 'conditionally acceptable'
            result['risks'] = []
            result['blockers'] = []
            result['fixDirection'] = '下一轮可继续压缩尾段并复查节奏'
            self.write_json(result_file, result)

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn(
                'proofreading risks must be non-empty when judgment is conditionally acceptable',
                validate.stderr + validate.stdout,
            )

    def test_validate_accepts_proofreading_conditionally_acceptable_with_risks_and_no_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            self.refresh_bundle_digests(bundle)
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            result = self.completed_proofreading_result(summary='附条件通过')
            result['judgment'] = 'conditionally acceptable'
            result['risks'] = ['尾段节奏仍可继续收紧']
            result['blockers'] = []
            result['fixDirection'] = '下一轮补强尾段节奏并复查结尾钩子'
            self.write_json(result_file, result)

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertEqual(validate.returncode, 0, validate.stderr)
            payload = json.loads(validate.stdout)
            self.assertEqual(payload['result']['judgment'], 'conditionally acceptable')
            self.assertEqual(payload['result']['risks'], ['尾段节奏仍可继续收紧'])
            self.assertEqual(payload['result']['blockers'], [])

    def test_validate_rejects_proofreading_completed_with_empty_continuity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            self.refresh_bundle_digests(bundle)
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            result = self.completed_proofreading_result()
            result['continuity'] = ''
            self.write_json(result_file, result)

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('proofreading continuity must be a non-empty string', validate.stderr + validate.stdout)

    def test_validate_rejects_proofreading_needs_revision_without_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                batch={'draftComplete': True, 'polishingComplete': True},
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.set_proofreading_bundle_report_contract(bundle)
            self.refresh_bundle_digests(bundle)
            self.write_json(bundle_file, bundle)
            self.write_proofreading_report(project)
            result = self.completed_proofreading_result()
            result['judgment'] = 'needs revision'
            result['blockers'] = []
            result['fixDirection'] = '回到润色阶段处理结尾信息缺口'
            self.write_json(result_file, result)

            validate = run_script(
                'validate_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(validate.returncode, 0)
            self.assertIn('proofreading blockers must be non-empty when judgment is needs revision', validate.stderr + validate.stdout)

    def test_apply_persists_lightweight_summary_and_status_shows_draft_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'bundle.json'
            result_file = root / 'result.json'
            bundle = json.loads(bundle_result.stdout)
            self.write_json(bundle_file, bundle)

            (project / 'manuscript' / '第1章_开端.md').write_text('# 第一章\n\n正文', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['manuscript/第1章_开端.md'],
                    'blockedReasons': [],
                    'summary': '已完成第1章初稿',
                    'notesForNextStage': '进入润色',
                    'risks': ['开篇节奏还可再压缩'],
                },
            )

            apply_result = run_script(
                'apply_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertEqual(apply_result.returncode, 0, apply_result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertTrue(state['batch']['draftComplete'])
            self.assertEqual(state['batch']['lastDelegatedStage'], 'drafting')
            self.assertEqual(state['batch']['lastDelegationStatus'], 'completed')
            self.assertEqual(state['batch']['lastDelegationSummary'], '已完成第1章初稿')
            self.assertEqual(state['review']['currentGate'], 'waiting_draft_feedback')
            state_text = json.dumps(state, ensure_ascii=False)
            self.assertNotIn('executionPackage', state_text)
            self.assertNotIn('validationContext', state_text)
            self.assertNotIn('sessionId', state_text)

            status = run_script('novel_project_status.py', str(project), '--brief')
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertIn('当前卡点：等待你确认本轮初稿结果', status.stdout)
            self.assertIn('最近委派：drafting / completed / 第1章', status.stdout)

    def test_apply_stage_execution_result_moves_chapter_to_review_and_queues_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            relpath = 'manuscript/第1章_开端.md'
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_file = root / 'bundle.json'
            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                relpath,
                '--bundle-file',
                str(bundle_file),
                '--dispatch-dir',
                str(root / 'dispatch'),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            result_file = root / 'result.json'

            (project / relpath).write_text('# 第一章\n\n正文', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': [relpath],
                    'blockedReasons': [],
                    'summary': '已完成第1章初稿',
                    'notesForNextStage': '进入润色',
                    'risks': [],
                },
            )

            apply_result = run_script(
                'apply_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertEqual(apply_result.returncode, 0, apply_result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            task = state['batch']['chapterTasks'][0]
            summaries = [item['summary'] for item in state['batch']['pendingProgressItems']]
            self.assertEqual(task['chapterLabel'], '第1章')
            self.assertEqual(task['phase'], 'drafting')
            self.assertEqual(task['phaseStatus'], 'awaiting_user_review')
            self.assertEqual(task['manuscriptPath'], relpath)
            self.assertEqual(task['blockers'], [])
            self.assertEqual(task['lastSummary'], '第1章初稿待审核')
            self.assertEqual(summaries, ['第1章初稿待审核'])
            self.assertNotIn('第1章初稿中', summaries)

    def test_apply_stage_execution_result_marks_blocked_chapter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            relpath = 'manuscript/第1章_开端.md'
            project = self.create_runtime_project(
                root,
                current_stage='polishing',
                batch={'draftComplete': True},
                manuscript_files={relpath: '# 第一章\n\n正文'},
            )
            bundle_file = root / 'bundle.json'
            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'polishing',
                '--batch-range',
                '第1章',
                '--polishing-focus',
                '压缩开篇节奏',
                '--bundle-file',
                str(bundle_file),
                '--dispatch-dir',
                str(root / 'dispatch'),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            result_file = root / 'result.json'
            self.write_json(
                result_file,
                {
                    'status': 'blocked',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': ['人物口吻漂移'],
                    'summary': '润色被阻塞',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            apply_result = run_script(
                'apply_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertEqual(apply_result.returncode, 0, apply_result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            task = state['batch']['chapterTasks'][0]
            summaries = [item['summary'] for item in state['batch']['pendingProgressItems']]
            self.assertEqual(task['chapterLabel'], '第1章')
            self.assertEqual(task['phase'], 'polishing')
            self.assertEqual(task['phaseStatus'], 'blocked')
            self.assertEqual(task['manuscriptPath'], relpath)
            self.assertEqual(task['blockers'], ['人物口吻漂移'])
            self.assertEqual(task['lastSummary'], '第1章阻塞：人物口吻漂移')
            self.assertEqual(summaries, ['第1章阻塞：人物口吻漂移'])
            self.assertNotIn('第1章润色中', summaries)

    def test_apply_stage_execution_result_preserves_proofreading_revision_blockers_in_chapter_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
                batch={'draftComplete': True, 'polishingComplete': True},
            )
            bundle_file = root / 'proofreading-bundle.json'
            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
                '--bundle-file',
                str(bundle_file),
                '--dispatch-dir',
                str(root / 'dispatch'),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            result_file = root / 'proofreading-result.json'
            self.write_proofreading_report(
                project,
                '# 05A_本轮校对报告\n\n- judgment: needs revision\n- summary: 需要回修\n',
            )
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['05A_本轮校对报告.md'],
                    'blockedReasons': [],
                    'summary': '本轮校对完成，但需要回修',
                    'notesForNextStage': '等待审核后回修',
                    'risks': [],
                    'judgment': 'needs revision',
                    'continuity': '存在断点',
                    'logic': '存在漏洞',
                    'characterOOC': '轻微',
                    'blockers': ['结尾信息缺口'],
                    'fixDirection': '补足关键解释并重写结尾段落',
                },
            )

            apply_result = run_script(
                'apply_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertEqual(apply_result.returncode, 0, apply_result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            task = state['batch']['chapterTasks'][0]
            summaries = [item['summary'] for item in state['batch']['pendingProgressItems']]
            self.assertEqual(task['chapterLabel'], '第1章')
            self.assertEqual(task['phase'], 'proofreading')
            self.assertEqual(task['phaseStatus'], 'blocked')
            self.assertEqual(task['blockers'], ['结尾信息缺口'])
            self.assertEqual(task['lastSummary'], '第1章阻塞：结尾信息缺口')
            self.assertEqual(summaries, ['第1章阻塞：结尾信息缺口'])
            self.assertNotIn('第1章校对中', summaries)

    def test_finalize_proofreading_dispatch_persists_report_and_pending_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(
                root,
                current_stage='proofreading',
                manuscript_files={'manuscript/第1章_开端.md': '# 第一章\n\n正文'},
                batch={'draftComplete': True, 'polishingComplete': True},
            )
            bundle_result = run_script(
                'build_stage_execution_package.py',
                str(project),
                'proofreading',
                '--batch-range',
                '第1章',
            )
            self.assertEqual(bundle_result.returncode, 0, bundle_result.stderr)

            bundle_file = root / 'proofreading-bundle.json'
            result_file = root / 'proofreading-result.json'
            bundle = json.loads(bundle_result.stdout)
            self.write_json(bundle_file, bundle)

            (project / '05A_本轮校对报告.md').write_text(
                '# 05A_本轮校对报告\n\n- judgment: acceptable\n- summary: 通过\n',
                encoding='utf-8',
            )
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['05A_本轮校对报告.md'],
                    'blockedReasons': [],
                    'summary': '本轮校对完成，可进入终审',
                    'notesForNextStage': '进入 final-review',
                    'risks': [],
                    'judgment': 'acceptable',
                    'continuity': '通过',
                    'logic': '通过',
                    'characterOOC': '无',
                    'blockers': [],
                    'fixDirection': '无需处理',
                },
            )

            result = run_script(
                'apply_stage_execution_result.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['review']['currentGate'], 'waiting_proofreading_feedback')
            self.assertEqual(state['review']['pendingArtifactPaths'], ['05A_本轮校对报告.md'])

    def test_status_shows_opening_gate_when_drafting_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_runtime_project(
                Path(tmp),
                current_stage='drafting',
                approvals={'openingApproved': False},
            )
            status = run_script('novel_project_status.py', str(project), '--brief')
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertIn('建议下一步：请先完成并确认 Opening Gate，再进入本轮章节规划与正文。', status.stdout)

    def test_update_project_state_supports_json_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self.create_runtime_project(Path(tmp), current_stage='drafting')
            result = run_script(
                'update_project_state.py',
                str(project),
                'batch.lastDelegationRisks',
                '["风险A","风险B"]',
                '--json',
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(state['batch']['lastDelegationRisks'], ['风险A', '风险B'])

    def test_prepare_dispatch_writes_bundle_and_renders_child_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_file = root / 'bundle.json'
            prompt_file = root / 'prompt.txt'
            manifest_file = root / 'manifest.json'
            result = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--bundle-file',
                str(bundle_file),
                '--prompt-file',
                str(prompt_file),
                '--manifest-file',
                str(manifest_file),
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            payload = json.loads(result.stdout)
            self.assertEqual(payload['dispatchDir'], str(root))
            self.assertEqual(payload['bundleFile'], str(bundle_file))
            self.assertEqual(payload['promptFile'], str(prompt_file))
            self.assertEqual(payload['manifestFile'], str(manifest_file))
            self.assertEqual(payload['rawFile'], str(root / 'child-response.txt'))
            self.assertEqual(payload['resultFile'], str(root / 'result.json'))
            self.assertEqual(payload['validatedFile'], str(root / 'validated.json'))
            self.assertEqual(payload['executionPackage']['stage'], 'drafting')
            self.assertIn('Return exactly one JSON object and nothing else.', payload['childPrompt'])
            self.assertIn('"targetFiles": [', payload['childPrompt'])
            self.assertNotIn('validationContext', payload['childPrompt'])
            self.assertTrue(bundle_file.exists())
            self.assertTrue(prompt_file.exists())
            self.assertTrue(manifest_file.exists())

            bundle = json.loads(bundle_file.read_text(encoding='utf-8'))
            manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
            self.assertIn('validationContext', bundle)
            self.assertEqual(prompt_file.read_text(encoding='utf-8'), payload['childPrompt'])
            self.assertEqual(manifest['bundleFile'], str(bundle_file))
            self.assertEqual(manifest['promptFile'], str(prompt_file))
            self.assertEqual(manifest['executionPackageDigest'], bundle['validationContext']['executionPackageDigest'])

    def test_prepare_dispatch_marks_target_chapter_in_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            result = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--dispatch-dir',
                str(root / 'dispatch'),
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            task = state['batch']['chapterTasks'][0]
            self.assertEqual(task['chapterLabel'], '第1章')
            self.assertEqual(task['phase'], 'drafting')
            self.assertEqual(task['phaseStatus'], 'in_progress')
            self.assertIn(
                '第1章初稿中',
                [item['summary'] for item in state['batch']['pendingProgressItems']],
            )

    def test_prepare_dispatch_reuses_in_progress_state_without_duplicate_pending_progress_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            dispatch_dir = root / 'dispatch'

            for _ in range(2):
                result = run_script(
                    'prepare_stage_subagent_dispatch.py',
                    str(project),
                    'drafting',
                    '--batch-range',
                    '第1章',
                    '--target-file',
                    'manuscript/第1章_开端.md',
                    '--dispatch-dir',
                    str(dispatch_dir),
                )
                self.assertEqual(result.returncode, 0, result.stderr)

            state = json.loads((project / '.novel-state.json').read_text(encoding='utf-8'))
            self.assertEqual(
                [item['summary'] for item in state['batch']['pendingProgressItems']],
                ['第1章初稿中'],
            )

    def test_prepare_dispatch_keeps_bundle_baseline_compatible_with_finalize_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_file = root / 'bundle.json'
            manifest_file = root / 'manifest.json'
            result_file = root / 'result.json'
            validated_file = root / 'validated.json'

            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--bundle-file',
                str(bundle_file),
                '--manifest-file',
                str(manifest_file),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            (project / 'manuscript' / '第1章_开端.md').write_text('# 第一章\n\n正文', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['manuscript/第1章_开端.md'],
                    'blockedReasons': [],
                    'summary': '已完成第1章初稿',
                    'notesForNextStage': '进入润色',
                    'risks': [],
                },
            )

            finalize = run_script(
                'finalize_stage_subagent_dispatch.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--manifest-file',
                str(manifest_file),
                '--result-file',
                str(result_file),
                '--validated-file',
                str(validated_file),
            )
            self.assertEqual(finalize.returncode, 0, finalize.stderr)

    def test_prepare_dispatch_supports_dispatch_dir_standard_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            dispatch_dir = root / 'dispatch-artifacts'
            result = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--dispatch-dir',
                str(dispatch_dir),
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            payload = json.loads(result.stdout)
            self.assertEqual(payload['dispatchDir'], str(dispatch_dir))
            self.assertEqual(payload['bundleFile'], str(dispatch_dir / 'bundle.json'))
            self.assertEqual(payload['promptFile'], str(dispatch_dir / 'prompt.txt'))
            self.assertEqual(payload['manifestFile'], str(dispatch_dir / 'manifest.json'))
            self.assertEqual(payload['rawFile'], str(dispatch_dir / 'child-response.txt'))
            self.assertEqual(payload['resultFile'], str(dispatch_dir / 'result.json'))
            self.assertEqual(payload['validatedFile'], str(dispatch_dir / 'validated.json'))
            self.assertTrue((dispatch_dir / 'bundle.json').exists())
            self.assertTrue((dispatch_dir / 'prompt.txt').exists())
            self.assertTrue((dispatch_dir / 'manifest.json').exists())
            self.assertFalse((dispatch_dir / 'child-response.txt').exists())
            self.assertFalse((dispatch_dir / 'result.json').exists())
            self.assertFalse((dispatch_dir / 'validated.json').exists())

    def test_prepare_dispatch_infers_dispatch_dir_from_explicit_artifact_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            artifact_dir = root / 'shared-artifacts'
            bundle_file = artifact_dir / 'custom-bundle.json'
            prompt_file = artifact_dir / 'custom-prompt.txt'
            manifest_file = artifact_dir / 'custom-manifest.json'
            result = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--bundle-file',
                str(bundle_file),
                '--prompt-file',
                str(prompt_file),
                '--manifest-file',
                str(manifest_file),
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            payload = json.loads(result.stdout)
            self.assertEqual(payload['dispatchDir'], str(artifact_dir))
            self.assertEqual(payload['bundleFile'], str(bundle_file))
            self.assertEqual(payload['promptFile'], str(prompt_file))
            self.assertEqual(payload['manifestFile'], str(manifest_file))
            self.assertEqual(payload['rawFile'], str(artifact_dir / 'child-response.txt'))
            self.assertEqual(payload['resultFile'], str(artifact_dir / 'result.json'))
            self.assertEqual(payload['validatedFile'], str(artifact_dir / 'validated.json'))
            self.assertTrue(bundle_file.exists())
            self.assertTrue(prompt_file.exists())
            self.assertTrue(manifest_file.exists())

    def test_prepare_dispatch_rejects_artifacts_inside_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            result = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--bundle-file',
                str(project / 'bundle.json'),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('must stay outside project root', result.stderr + result.stdout)

    def test_prepare_dispatch_rejects_dispatch_dir_inside_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            result = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--dispatch-dir',
                str(project / 'dispatch-artifacts'),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('must stay outside project root', result.stderr + result.stdout)

    def test_prepare_dispatch_rejects_manifest_inside_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            result = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--manifest-file',
                str(project / 'manifest.json'),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('must stay outside project root', result.stderr + result.stdout)

    def test_python_dispatch_runtime_helper_prepares_records_and_finalizes(self):
        runtime = self.load_script_module('subagent_dispatch_runtime')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            dispatch_dir = root / 'dispatch-helper'

            payload = runtime.prepare_dispatch(
                str(project),
                'drafting',
                batch_range='第1章',
                target_files=['manuscript/第1章_开端.md'],
                dispatch_dir=str(dispatch_dir),
            )
            self.assertEqual(payload['dispatchDir'], str(dispatch_dir))
            self.assertIn('Return exactly one JSON object and nothing else.', payload['childPrompt'])
            self.assertNotIn('validationContext', payload['childPrompt'])
            self.assertTrue((dispatch_dir / 'prompt.txt').exists())

            (project / 'manuscript' / '第1章_开端.md').write_text('# 第一章\n\n正文', encoding='utf-8')
            runtime.record_child_output(
                str(project),
                json.dumps(
                    {
                        'status': 'completed',
                        'changedFiles': [],
                        'createdFiles': ['manuscript/第1章_开端.md'],
                        'blockedReasons': [],
                        'summary': 'helper 已完成第1章初稿',
                        'notesForNextStage': '进入润色',
                        'risks': [],
                    },
                    ensure_ascii=False,
                ),
                dispatch_dir=str(dispatch_dir),
            )
            self.assertTrue((dispatch_dir / 'child-response.txt').exists())

            applied = runtime.finalize_dispatch(
                str(project),
                dispatch_dir=str(dispatch_dir),
            )
            self.assertEqual(applied['validated']['stage'], 'drafting')
            self.assertEqual(applied['savedState']['batch']['lastDelegationSummary'], 'helper 已完成第1章初稿')
            self.assertTrue((dispatch_dir / 'result.json').exists())
            self.assertTrue((dispatch_dir / 'validated.json').exists())

    def test_extract_dispatch_result_reads_raw_text_and_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            raw_file = root / 'child.txt'
            result_file = root / 'result.json'
            raw_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'changedFiles': [],
                        'createdFiles': ['manuscript/第1章_开端.md'],
                        'blockedReasons': [],
                        'summary': '已完成第1章初稿',
                        'notesForNextStage': '进入润色',
                        'risks': [],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            extract = run_script(
                'extract_stage_subagent_result.py',
                '--raw-file',
                str(raw_file),
                '--project-root',
                str(project),
                '--result-file',
                str(result_file),
            )
            self.assertEqual(extract.returncode, 0, extract.stderr)
            payload = json.loads(extract.stdout)
            self.assertEqual(payload['status'], 'completed')
            self.assertTrue(result_file.exists())
            self.assertEqual(
                json.loads(result_file.read_text(encoding='utf-8')),
                payload,
            )

    def test_extract_dispatch_result_supports_dispatch_dir_standard_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            dispatch_dir = root / 'dispatch'
            dispatch_dir.mkdir()
            raw_file = dispatch_dir / 'child-response.txt'
            result_file = dispatch_dir / 'result.json'
            raw_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'changedFiles': [],
                        'createdFiles': ['manuscript/第1章_开端.md'],
                        'blockedReasons': [],
                        'summary': '已完成第1章初稿',
                        'notesForNextStage': '进入润色',
                        'risks': [],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

            extract = run_script(
                'extract_stage_subagent_result.py',
                '--dispatch-dir',
                str(dispatch_dir),
                '--project-root',
                str(project),
            )
            self.assertEqual(extract.returncode, 0, extract.stderr)
            payload = json.loads(extract.stdout)
            self.assertEqual(payload['status'], 'completed')
            self.assertTrue(result_file.exists())
            self.assertEqual(json.loads(result_file.read_text(encoding='utf-8')), payload)

    def test_extract_dispatch_result_prefers_explicit_paths_over_dispatch_dir_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            dispatch_dir = root / 'dispatch'
            dispatch_dir.mkdir()
            raw_file = root / 'custom-child.txt'
            result_file = root / 'custom-result.json'
            raw_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'changedFiles': [],
                        'createdFiles': ['manuscript/第1章_开端.md'],
                        'blockedReasons': [],
                        'summary': '显式路径优先',
                        'notesForNextStage': '进入润色',
                        'risks': [],
                    },
                    ensure_ascii=False,
                ),
                encoding='utf-8',
            )

            extract = run_script(
                'extract_stage_subagent_result.py',
                '--dispatch-dir',
                str(dispatch_dir),
                '--raw-file',
                str(raw_file),
                '--result-file',
                str(result_file),
                '--project-root',
                str(project),
            )
            self.assertEqual(extract.returncode, 0, extract.stderr)
            payload = json.loads(extract.stdout)
            self.assertEqual(payload['summary'], '显式路径优先')
            self.assertTrue(result_file.exists())
            self.assertFalse((dispatch_dir / 'result.json').exists())

    def test_extract_dispatch_result_requires_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_file = root / 'child.txt'
            raw_file.write_text('{}', encoding='utf-8')

            extract = run_script(
                'extract_stage_subagent_result.py',
                '--raw-file',
                str(raw_file),
            )
            self.assertNotEqual(extract.returncode, 0)
            self.assertIn('--project-root', extract.stderr + extract.stdout)

    def test_extract_dispatch_result_rejects_result_file_inside_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            raw_file = root / 'child.txt'
            raw_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'changedFiles': [],
                        'createdFiles': ['manuscript/第1章_开端.md'],
                        'blockedReasons': [],
                        'summary': '已完成第1章初稿',
                        'notesForNextStage': '进入润色',
                        'risks': [],
                    },
                    ensure_ascii=False,
                ),
                encoding='utf-8',
            )

            extract = run_script(
                'extract_stage_subagent_result.py',
                '--raw-file',
                str(raw_file),
                '--result-file',
                str(project / 'result.json'),
                '--project-root',
                str(project),
            )
            self.assertNotEqual(extract.returncode, 0)
            self.assertIn('must stay outside project root', extract.stderr + extract.stdout)

    def test_extract_dispatch_result_rejects_non_object_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_file = root / 'child.txt'
            raw_file.write_text('child says done', encoding='utf-8')
            project = self.create_runtime_project(root, current_stage='drafting')

            extract = run_script(
                'extract_stage_subagent_result.py',
                '--raw-file',
                str(raw_file),
                '--project-root',
                str(project),
            )
            self.assertNotEqual(extract.returncode, 0)
            self.assertIn('exactly one JSON object', extract.stderr + extract.stdout)

    def test_finalize_dispatch_validates_and_applies_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_file = root / 'bundle.json'
            manifest_file = root / 'manifest.json'
            result_file = root / 'result.json'
            validated_file = root / 'validated.json'

            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--bundle-file',
                str(bundle_file),
                '--manifest-file',
                str(manifest_file),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            (project / 'manuscript' / '第1章_开端.md').write_text('# 第一章\n\n正文', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['manuscript/第1章_开端.md'],
                    'blockedReasons': [],
                    'summary': '已完成第1章初稿',
                    'notesForNextStage': '进入润色',
                    'risks': ['开篇节奏还可再压缩'],
                },
            )

            finalize = run_script(
                'finalize_stage_subagent_dispatch.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--manifest-file',
                str(manifest_file),
                '--result-file',
                str(result_file),
                '--validated-file',
                str(validated_file),
            )
            self.assertEqual(finalize.returncode, 0, finalize.stderr)

            payload = json.loads(finalize.stdout)
            self.assertEqual(payload['validated']['stage'], 'drafting')
            self.assertEqual(payload['savedState']['batch']['lastDelegatedStage'], 'drafting')
            self.assertEqual(payload['savedState']['batch']['lastDelegationSummary'], '已完成第1章初稿')
            self.assertTrue(validated_file.exists())
            validated = json.loads(validated_file.read_text(encoding='utf-8'))
            self.assertEqual(validated['stage'], 'drafting')

    def test_finalize_dispatch_supports_dispatch_dir_standard_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            dispatch_dir = root / 'dispatch'

            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--dispatch-dir',
                str(dispatch_dir),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            (project / 'manuscript' / '第1章_开端.md').write_text('# 第一章\n\n正文', encoding='utf-8')
            self.write_json(
                dispatch_dir / 'result.json',
                {
                    'status': 'completed',
                    'changedFiles': [],
                    'createdFiles': ['manuscript/第1章_开端.md'],
                    'blockedReasons': [],
                    'summary': '已完成第1章初稿',
                    'notesForNextStage': '进入润色',
                    'risks': [],
                },
            )

            finalize = run_script(
                'finalize_stage_subagent_dispatch.py',
                str(project),
                '--dispatch-dir',
                str(dispatch_dir),
            )
            self.assertEqual(finalize.returncode, 0, finalize.stderr)

            payload = json.loads(finalize.stdout)
            self.assertEqual(payload['validated']['stage'], 'drafting')
            self.assertEqual(payload['savedState']['batch']['lastDelegationSummary'], '已完成第1章初稿')
            self.assertTrue((dispatch_dir / 'validated.json').exists())

    def test_finalize_dispatch_rejects_stale_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_file = root / 'bundle.json'
            manifest_file = root / 'manifest.json'
            result_file = root / 'result.json'

            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--bundle-file',
                str(bundle_file),
                '--manifest-file',
                str(manifest_file),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            bundle_file.write_text(bundle_file.read_text(encoding='utf-8') + '\n', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'needs_clarification',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': [],
                    'summary': '未执行',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            finalize = run_script(
                'finalize_stage_subagent_dispatch.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--manifest-file',
                str(manifest_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(finalize.returncode, 0)
            self.assertIn('bundle manifest mismatch', finalize.stderr + finalize.stdout)


    def test_finalize_dispatch_rejects_stale_prompt_file_against_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_file = root / 'bundle.json'
            prompt_file = root / 'prompt.txt'
            manifest_file = root / 'manifest.json'
            result_file = root / 'result.json'

            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--bundle-file',
                str(bundle_file),
                '--prompt-file',
                str(prompt_file),
                '--manifest-file',
                str(manifest_file),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            prompt_file.write_text(prompt_file.read_text(encoding='utf-8') + '\n# tampered\n', encoding='utf-8')
            self.write_json(
                result_file,
                {
                    'status': 'needs_clarification',
                    'changedFiles': [],
                    'createdFiles': [],
                    'blockedReasons': ['缺少必要上下文'],
                    'summary': '未执行',
                    'notesForNextStage': '',
                    'risks': [],
                },
            )

            finalize = run_script(
                'finalize_stage_subagent_dispatch.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--manifest-file',
                str(manifest_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(finalize.returncode, 0)
            self.assertIn('bundle manifest mismatch: promptSha256', finalize.stderr + finalize.stdout)

    def test_finalize_dispatch_rejects_artifacts_inside_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.create_runtime_project(root, current_stage='drafting')
            bundle_file = root / 'bundle.json'
            result_file = project / 'result.json'
            result_file.write_text(
                json.dumps(
                    {
                        'status': 'completed',
                        'changedFiles': [],
                        'createdFiles': ['manuscript/第1章_开端.md'],
                        'blockedReasons': [],
                        'summary': '已完成第1章初稿',
                        'notesForNextStage': '进入润色',
                        'risks': [],
                    },
                    ensure_ascii=False,
                ),
                encoding='utf-8',
            )
            prepare = run_script(
                'prepare_stage_subagent_dispatch.py',
                str(project),
                'drafting',
                '--batch-range',
                '第1章',
                '--target-file',
                'manuscript/第1章_开端.md',
                '--bundle-file',
                str(bundle_file),
            )
            self.assertEqual(prepare.returncode, 0, prepare.stderr)

            finalize = run_script(
                'finalize_stage_subagent_dispatch.py',
                str(project),
                '--bundle-file',
                str(bundle_file),
                '--result-file',
                str(result_file),
            )
            self.assertNotEqual(finalize.returncode, 0)
            self.assertIn('must stay outside project root', finalize.stderr + finalize.stdout)
