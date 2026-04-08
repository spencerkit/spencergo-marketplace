#!/usr/bin/env python3
"""
Run an isolated child session to complete a novel-studio stage.

Auto-detects the current agent platform and launches a physically isolated
child session with:
- Zero chat history from the parent session
- Only the files explicitly listed in the stage input contract
- Platform-specific isolation flags

Platform detection order:
1. Parent process cmdline (/proc/PID/cmdline) — most accurate
2. Environment variables (CLAUDECODE, QWEN_CODE, OPENCODE, CODEX_SESSION_ID)
3. CLI binary scan on PATH — if multiple found, user must pick with --cli-binary

Usage:
    python3 run_isolated_dispatch.py <project_root> <stage> \
        --batch-range "第1章-第3章" \
        --target-file "manuscript/第1章.md" \
        --target-file "manuscript/第2章.md" \
        --target-file "manuscript/第3章.md" \
        --model sonnet \
        --timeout 300

    # List detected CLIs:
    python3 run_isolated_dispatch.py <project_root> <stage> --list-platforms

    # Force a specific CLI:
    python3 run_isolated_dispatch.py <project_root> <stage> --cli-binary qwen

The main agent orchestrates the full loop:
    1. run_isolated_dispatch.py → runs isolated session, writes files
    2. validate_stage_execution_result.py → validates the output
    3. apply_stage_execution_result.py → applies accepted state
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from build_stage_execution_package import build_bundle
from chapter_progress_utils import mark_dispatch_started
from revision_utils import load_state, save_state
from stage_execution_utils import (
    PROTOCOL_RETURN_FIELDS,
    PROOFREADING_REQUIRED_STAGE_FIELDS,
    build_child_prompt,
    dispatch_layout,
    ensure_outside_project,
    ensure_project,
    load_or_reconstruct_state,
    normalize_relpath,
    normalize_relpaths,
    normalize_stage,
    now_iso,
    snapshot_project,
)


# ── Platform Detection ──────────────────────────────────────────────

@dataclass
class PlatformInfo:
    name: str
    cli_binary: str
    prompt_flag: str          # flag to pass a non-interactive prompt
    extra_args: list[str]     # platform-specific isolation flags
    env_cleanup: dict[str, str]  # env vars to strip from child


PLATFORMS: dict[str, PlatformInfo] = {
    'claude_code': PlatformInfo(
        name='Claude Code',
        cli_binary='claude',
        prompt_flag='-p',
        extra_args=[
            '--output-format', 'text',
            '--dangerously-skip-permissions',
            '--permission-mode', 'bypassPermissions',
            '--disallowed-tools', 'Agent',
            '--no-session-persistence',
        ],
        env_cleanup={'CLAUDECODE': None},
    ),
    'qwen_code': PlatformInfo(
        name='Qwen Code',
        cli_binary='qwen',
        prompt_flag='-p',
        extra_args=[
            '--approval-mode', 'yolo',
        ],
        env_cleanup={'QWEN_CODE': None, 'QWEN_CODE_NO_RELAUNCH': None},
    ),
    'opencode': PlatformInfo(
        name='OpenCode',
        cli_binary='opencode',
        prompt_flag='',  # uses positional 'run' subcommand
        extra_args=[],
        env_cleanup={'OPENCODE': None},
    ),
    'codex': PlatformInfo(
        name='Codex CLI',
        cli_binary='codex',
        prompt_flag='-p',
        extra_args=[],
        env_cleanup={'CODEX_SESSION_ID': None},
    ),
}


def detect_platform() -> PlatformInfo | None:
    """Auto-detect the current agent platform.

    Strategy:
    1. Check /proc for parent process cmdline (most accurate at runtime)
    2. Environment variables (when procfs is unavailable)
    3. CLI binary on PATH (least precise — multiple may exist)
    """
    # 1. Check parent process cmdline via /proc
    parent_pid = os.getppid()
    try:
        with open(f'/proc/{parent_pid}/cmdline', 'rb') as f:
            parent_cmdline = f.read().decode('utf-8', errors='replace')
        for platform in PLATFORMS.values():
            if platform.cli_binary in parent_cmdline:
                return platform
    except (OSError, PermissionError):
        pass

    # 2. Environment variables
    if os.environ.get('CLAUDECODE') is not None:
        return PLATFORMS['claude_code']
    if os.environ.get('QWEN_CODE') is not None:
        return PLATFORMS['qwen_code']
    if os.environ.get('OPENCODE') is not None:
        return PLATFORMS['opencode']
    if os.environ.get('CODEX_SESSION_ID') is not None:
        return PLATFORMS['codex']

    # 3. Fallback: first matching CLI on PATH
    for binary_name, platform in [
        ('claude', PLATFORMS['claude_code']),
        ('qwen', PLATFORMS['qwen_code']),
        ('opencode', PLATFORMS['opencode']),
        ('codex', PLATFORMS['codex']),
    ]:
        if shutil.which(binary_name):
            return platform

    return None


def find_available_platforms() -> list[tuple[str, PlatformInfo]]:
    """Scan PATH and return all detected agent CLI binaries."""
    found = []
    for binary_name, platform in [
        ('claude', PLATFORMS['claude_code']),
        ('qwen', PLATFORMS['qwen_code']),
        ('opencode', PLATFORMS['opencode']),
        ('codex', PLATFORMS['codex']),
    ]:
        binary_path = shutil.which(binary_name)
        if binary_path:
            found.append((binary_path, platform))
    return found


CONFIG_DIR = Path.home() / '.novel-studio'
CONFIG_FILE = CONFIG_DIR / 'config.json'


def load_user_config() -> dict:
    """Load user's saved CLI preference, if any."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_user_config(cli_binary: str, platform_name: str) -> None:
    """Save user's CLI preference."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = {
        'cli_binary': cli_binary,
        'platform_name': platform_name,
        'set_at': now_iso(),
    }
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')


# ── Prompt Building ─────────────────────────────────────────────────

def build_isolated_prompt(execution_package: dict, stage: str) -> str:
    """Build a prompt that embeds all required context without chat history."""
    inputs = execution_package['requiredInputs']
    target_files = execution_package['targetFiles']
    output_contract = execution_package['outputContract']

    # Build the file context section
    file_context_lines = []

    # Common inputs for all stages
    file_context_lines.append('## 大纲')
    file_context_lines.append(inputs['outline'])
    file_context_lines.append('')
    file_context_lines.append('## 本轮章节规划')
    file_context_lines.append(inputs['batchPlan'])
    file_context_lines.append('')
    file_context_lines.append('## 风格圣经')
    file_context_lines.append(inputs['styleBible'])
    file_context_lines.append('')
    file_context_lines.append('## 总主线与卷级推进')
    file_context_lines.append(inputs['mainlineSpec'])
    file_context_lines.append('')
    file_context_lines.append('## 开篇设计')
    file_context_lines.append(inputs['openingDesign'])
    file_context_lines.append('')
    file_context_lines.append('## 底盘与切口决策')
    file_context_lines.append(inputs['trackGuide'])
    file_context_lines.append('')
    file_context_lines.append('## 平台模式')
    file_context_lines.append(inputs['platformProfile'])
    file_context_lines.append('')
    file_context_lines.append('## 账本快照')
    for relpath, text in sorted(inputs.get('ledgerSnapshot', {}).items()):
        file_context_lines.append(f'### {relpath}')
        file_context_lines.append(text)
        file_context_lines.append('')

    if inputs.get('recap'):
        file_context_lines.append('## 前情回顾')
        file_context_lines.append(inputs['recap'])
        file_context_lines.append('')

    # Character files
    for relpath, text in sorted(inputs.get('characterFiles', {}).items()):
        file_context_lines.append(f'## {relpath}')
        file_context_lines.append(text)
        file_context_lines.append('')

    # Stage-specific inputs
    if stage == 'polishing':
        if inputs.get('manuscriptFiles'):
            for relpath, text in sorted(inputs['manuscriptFiles'].items()):
                file_context_lines.append(f'## {relpath}')
                file_context_lines.append(text)
                file_context_lines.append('')

    if stage == 'proofreading':
        if inputs.get('manuscriptFiles'):
            for relpath, text in sorted(inputs['manuscriptFiles'].items()):
                file_context_lines.append(f'## {relpath}')
                file_context_lines.append(text)
                file_context_lines.append('')

    file_context = '\n'.join(file_context_lines)

    # Build stage-specific task instructions
    stage_instructions = {
        'drafting': f"""你是本项目的 drafting agent。你的任务是撰写指定章节的正文。

硬性规则：
1. 你只能基于上方列出的文件工作，不得依赖任何未列出的上下文或假设。
2. 你只能写入以下文件，不得修改任何其他文件：
{chr(10).join('   - ' + f for f in target_files)}
3. 你必须写出真正的小说正文，不是情节摘要、不是大纲、不是说明文字。
4. 严格遵守风格圣经中的设定。
5. 按照章节规划中的要求逐章写作。
6. 完成后返回一个 JSON 对象，包含以下字段：
   - status: "completed" / "blocked" / "needs_clarification"
   - changedFiles: 你修改的文件列表
   - createdFiles: 你创建的文件列表
   - blockedReasons: 如果不能完成，说明原因（列表）
   - summary: 一段简短总结
   - notesForNextStage: 给下一阶段 agent 的备注
   - risks: 潜在风险列表""",
        'polishing': f"""你是本项目的 polishing agent。你的任务是精修已有章节。

硬性规则：
1. 你只能基于上方列出的文件工作，不得依赖任何未列出的上下文或假设。
2. 你只能修改以下文件：
{chr(10).join('   - ' + f for f in target_files)}
3. 不得静默改变上游规划假设或人物设定。
4. 聚焦以下优化方向：
   {inputs.get('polishingFocus', '提升语言流畅度，消除 AI 味，增强人物口吻区分')}
5. 完成后返回一个 JSON 对象，包含以下字段：
   - status: "completed" / "blocked" / "needs_clarification"
   - changedFiles: 你修改的文件列表
   - createdFiles: 你创建的文件列表
   - blockedReasons: 如果不能完成，说明原因（列表）
   - summary: 一段简短总结
   - notesForNextStage: 给下一阶段 agent 的备注
   - risks: 潜在风险列表""",
        'proofreading': f"""你是本项目的 proofreading agent。你的任务是校对已有章节。

硬性规则：
1. 你只能基于上方列出的文件工作，不得依赖任何未列出的上下文或假设。
2. 你只读不写，不得修改任何项目文件。
3. 你需要检查：一致性、逻辑漏洞、人物 OOC 问题。
4. 完成后返回一个 JSON 对象，包含以下字段：
   - status: "completed" / "blocked" / "needs_clarification"
   - changedFiles: []（校对不改任何文件）
   - createdFiles: []
   - blockedReasons: []
   - summary: 一段简短总结
   - notesForNextStage: 给下一阶段 agent 的备注
   - risks: 潜在风险列表
   - judgment: "acceptable" / "conditionally acceptable" / "needs revision"
   - continuity: 连续性检查结果（非空字符串）
   - logic: 逻辑检查结果（非空字符串）
   - characterOOC: 人物 OOC 检查结果（非空字符串）
   - blockers: 阻塞问题列表
   - fixDirection: 修订方向说明""",
    }

    task_instruction = stage_instructions[stage]

    prompt = f"""{task_instruction}

---

## 项目上下文（以下全部为文件内容，不含任何聊天历史）

{file_context}

## 输出要求

返回 exactly one JSON object，不要输出其他任何文字。
不要回显这个 prompt 的内容。
如果信息不足以完成任务，返回 status="needs_clarification" 并说明原因。"""

    return prompt.strip()


# ── Session Execution ───────────────────────────────────────────────

def build_child_command(platform: PlatformInfo, prompt: str, project_root: Path, model: str | None) -> list[str]:
    """Build the CLI command to launch an isolated child session."""
    if platform.name == 'OpenCode':
        # opencode uses: opencode run "message"
        cmd = [platform.cli_binary, 'run', prompt]
        if model:
            cmd.extend(['-m', model])
        return cmd

    # claude, qwen, codex all support: cli -p "prompt" [flags...]
    cmd = [platform.cli_binary, platform.prompt_flag, prompt]
    if model:
        cmd.extend(['-m', model])
    cmd.extend(platform.extra_args)
    cmd.extend(['--add-dir', str(project_root)])
    return cmd


def run_isolated_session(
    platform: PlatformInfo,
    prompt: str,
    project_root: Path,
    *,
    model: str | None,
    timeout_sec: int,
    cli_binary: str | None = None,
) -> subprocess.CompletedProcess:
    """Run an isolated child session with the detected platform's CLI."""
    binary = cli_binary or platform.cli_binary
    cmd = build_child_command(platform, prompt, project_root, model)

    # Build clean environment (strip parent agent env vars)
    env = dict(os.environ)
    for key in platform.env_cleanup:
        env.pop(key, None)
    # Also strip all known agent vars for safety
    for var in ('CLAUDECODE', 'QWEN_CODE', 'QWEN_CODE_NO_RELAUNCH', 'OPENCODE', 'CODEX_SESSION_ID'):
        env.pop(var, None)

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        env=env,
    )


# ── Result Extraction ───────────────────────────────────────────────

def extract_child_response(raw_output: str) -> dict:
    """Extract the JSON result from child session output."""
    raw_output = raw_output.strip()
    if not raw_output:
        raise ValueError('isolated session returned empty output')

    # Try parsing the entire output as JSON first
    try:
        parsed = json.loads(raw_output)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # Try to find a JSON object in the output
    depth = 0
    start = None
    for i, ch in enumerate(raw_output):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                candidate = raw_output[start:i + 1]
                try:
                    parsed = json.loads(candidate)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    pass
                start = None

    raise ValueError(
        f'isolated session did not return valid JSON. '
        f'First 500 chars: {raw_output[:500]}'
    )


def check_output_files(project: Path, target_files: list[str], baseline: dict) -> tuple[list[str], list[str]]:
    """Check which target files were actually written."""
    changed = []
    created = []
    for relpath in target_files:
        full_path = project / relpath
        if not full_path.exists():
            continue
        if relpath not in baseline:
            created.append(relpath)
        else:
            current_hash = __import__('hashlib').sha256(full_path.read_bytes()).hexdigest()
            if current_hash != baseline[relpath]['sha256']:
                changed.append(relpath)
    return changed, created


def build_result_from_response(
    child_json: dict,
    target_files: list[str],
    changed: list[str],
    created: list[str],
) -> dict:
    """Ensure the child response has all required protocol fields."""
    result = dict(child_json)

    # Normalize changedFiles/createdFiles from actual filesystem state
    if 'changedFiles' not in result or not isinstance(result.get('changedFiles'), list):
        result['changedFiles'] = changed
    if 'createdFiles' not in result or not isinstance(result.get('createdFiles'), list):
        result['createdFiles'] = created

    # Ensure all required fields exist
    for field in PROTOCOL_RETURN_FIELDS:
        if field not in result:
            if field == 'status':
                result['status'] = 'completed' if (changed or created) else 'blocked'
            elif field == 'blockedReasons':
                result['blockedReasons'] = []
            elif field in ('changedFiles', 'createdFiles', 'risks'):
                result[field] = []
            elif field == 'summary':
                result['summary'] = 'isolated dispatch completed'
            elif field == 'notesForNextStage':
                result['notesForNextStage'] = ''

    return result


# ── Main Dispatch ───────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Run an isolated child session for a novel-studio stage dispatch.'
    )
    parser.add_argument('project')
    parser.add_argument('stage')
    parser.add_argument('--batch-range')
    parser.add_argument('--target-file', action='append', default=[])
    parser.add_argument('--overwrite', default=None)
    parser.add_argument('--polishing-focus')
    parser.add_argument('--model', default=None, help='Model for the isolated session (platform-specific)')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds (default: 300)')
    parser.add_argument('--cli-binary', default=None, help='Override auto-detected CLI binary path')
    parser.add_argument('--list-platforms', action='store_true', help='List detected agent CLIs and exit')
    return parser.parse_args()


def run_isolated_dispatch(args: argparse.Namespace) -> dict:
    """Main dispatch logic."""
    project = ensure_project(Path(args.project))
    stage = normalize_stage(args.stage)
    state = load_or_reconstruct_state(project)

    # --list-platforms: just show what's available and exit
    if args.list_platforms:
        available = find_available_platforms()
        if not available:
            print('No known agent CLIs found on PATH.')
            print('Install one of: claude, qwen, opencode, codex')
        else:
            print('Detected agent CLIs on PATH:')
            for i, (path, platform) in enumerate(available, 1):
                print(f'  {i}. {platform.name:12s} → {path}')
            print()
            print('To select one, pass --cli-binary <path>')
        return {'action': 'list_platforms', 'available': [
            {'name': p.name, 'path': path, 'cli_binary': p.cli_binary}
            for path, p in available
        ]}

    # Resolve platform / CLI
    platform: PlatformInfo
    if args.cli_binary:
        # 1. User explicitly specified — use it and save preference
        if not shutil.which(args.cli_binary) and not Path(args.cli_binary).exists():
            raise RuntimeError(f'CLI binary not found: {args.cli_binary}')
        platform = PlatformInfo(
            name=f'custom ({args.cli_binary})',
            cli_binary=args.cli_binary,
            prompt_flag='-p',
            extra_args=[],
            env_cleanup={},
        )
        save_user_config(args.cli_binary, platform.name)
    else:
        # 2. Check saved user config
        user_config = load_user_config()
        saved_cli = user_config.get('cli_binary')
        if saved_cli and (shutil.which(saved_cli) or Path(saved_cli).exists()):
            # Saved config is still valid
            platform = detect_platform() or PLATFORMS['claude_code']  # default, will be overridden
            platform = PlatformInfo(
                name=user_config.get('platform_name', saved_cli),
                cli_binary=saved_cli,
                prompt_flag='-p',
                extra_args=[],
                env_cleanup={},
            )
        else:
            # 3. Auto-detect: parent cmdline → env vars → PATH
            platform = detect_platform()
            if platform is None:
                # Nothing auto-detected — check what's available
                available = find_available_platforms()
                if len(available) == 1:
                    _, platform = available[0]
                    save_user_config(platform.cli_binary, platform.name)
                elif len(available) > 1:
                    # Multiple found — tell user to pick
                    lines = ['Multiple agent CLIs found. Specify which to use with --cli-binary:']
                    for path, p in available:
                        lines.append(f'  --cli-binary {p.cli_binary}   ({p.name} at {path})')
                    lines.append('')
                    lines.append('Your choice will be remembered for future dispatches.')
                    lines.append('Or run with --list-platforms to see all options.')
                    raise RuntimeError('\n'.join(lines))
                else:
                    raise RuntimeError(
                        'No known agent CLI found on PATH.\n'
                        'Install one of: claude (Claude Code), qwen (Qwen Code), '
                        'opencode (OpenCode), codex (Codex CLI).'
                    )

    # Build the execution bundle (reuse existing logic)
    bundle = build_bundle(args)
    execution_package = bundle['executionPackage']

    # Record dispatch in state
    chapter_labels = execution_package['requiredInputs']['chapterLabels']
    target_files = execution_package['targetFiles']
    mark_dispatch_started(
        state['batch'],
        stage,
        chapter_labels,
        target_files,
    )
    save_state(project, state)

    # Build isolated prompt
    prompt = build_isolated_prompt(execution_package, stage)

    # Snapshot baseline
    baseline = snapshot_project(project)

    # Run the isolated session
    result = run_isolated_session(
        platform,
        prompt,
        project,
        model=args.model,
        timeout_sec=args.timeout,
        cli_binary=args.cli_binary,
    )

    # Handle timeout or crash
    if result.returncode != 0:
        stderr_excerpt = result.stderr[:500] if result.stderr else 'no stderr'
        stdout_excerpt = result.stdout[:500] if result.stdout else 'no stdout'
        raise RuntimeError(
            f'isolated session failed (exit code {result.returncode}) [{platform.name}].\n'
            f'stderr: {stderr_excerpt}\n'
            f'stdout: {stdout_excerpt}'
        )

    # Extract JSON result
    child_response = extract_child_response(result.stdout)

    # Check actual filesystem changes
    changed, created = check_output_files(project, target_files, baseline)

    # Build final result
    final_result = build_result_from_response(
        child_response,
        target_files,
        changed,
        created,
    )

    return {
        'result': final_result,
        'targetFiles': target_files,
        'changedFiles': changed,
        'createdFiles': created,
        'stage': stage,
        'platform': platform.name,
        'batchRange': execution_package.get('batchRange'),
        'executionPackage': execution_package,
        'timestamp': now_iso(),
    }


def main() -> None:
    args = parse_args()
    try:
        payload = run_isolated_dispatch(args)
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
