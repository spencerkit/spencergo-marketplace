#!/usr/bin/env python3
from pathlib import Path
import sys


def exists_nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.read_text(encoding='utf-8').strip() != ''


def contains_all(path: Path, needles):
    if not path.exists() or not path.is_file():
        return False
    text = path.read_text(encoding='utf-8')
    return all(n in text for n in needles)


def count_md(dirpath: Path) -> int:
    return len(list(dirpath.glob('*.md'))) if dirpath.is_dir() else 0


def check_discovery(project: Path, errors):
    f00a = project / '00A_热点扫描.md'
    f00b = project / '00B_用户偏好.md'
    f00 = project / '00_选题报告.md'
    if not exists_nonempty(f00a):
        errors.append('00A_热点扫描.md is missing or empty')
    if not exists_nonempty(f00b):
        errors.append('00B_用户偏好.md is missing or empty')
    if not exists_nonempty(f00):
        errors.append('00_选题报告.md is missing or empty')
    else:
        needed = ['最终推荐题材', '最终标题', '一句话核心钩子', '项目方向结论', '风险提醒']
        missing = [x for x in needed if not contains_all(f00, [x])]
        if missing:
            errors.append('00_选题报告.md missing required sections: ' + ', '.join(missing))


def check_planning(project: Path, errors):
    f01 = project / '01_想法.md'
    f02 = project / '02_大纲.md'
    if not exists_nonempty(f01):
        errors.append('01_想法.md is missing or empty')
    if not exists_nonempty(f02):
        errors.append('02_大纲.md is missing or empty')
    else:
        needed = ['剧情', '冲突']
        missing = [x for x in needed if not contains_all(f02, [x])]
        if missing:
            errors.append('02_大纲.md may be incomplete; missing markers: ' + ', '.join(missing))


def check_character(project: Path, errors):
    f03 = project / '03_人物小传.md'
    chars = project / 'characters'
    if not exists_nonempty(f03) and count_md(chars) == 0:
        errors.append('No character package found (03_人物小传.md or characters/*.md)')


def check_drafting(project: Path, errors):
    plan = project / '05_本轮章节规划.md'
    manu = project / 'manuscript'
    if not exists_nonempty(plan):
        errors.append('05_本轮章节规划.md is missing or empty')
    else:
        needed = ['本轮范围', '本轮写作重点', '逐章规划', '本章目标', '出场人物', '高潮点', '吸引点']
        missing = [x for x in needed if not contains_all(plan, [x])]
        if missing:
            errors.append('05_本轮章节规划.md missing required sections: ' + ', '.join(missing))
    if count_md(manu) == 0:
        errors.append('No manuscript files found in manuscript/')


def check_polishing(project: Path, errors):
    manu = project / 'manuscript'
    if count_md(manu) == 0:
        errors.append('No manuscript files found in manuscript/')


def check_proofreading(project: Path, errors):
    recap = project / '05_前情回顾.md'
    if not exists_nonempty(recap):
        errors.append('05_前情回顾.md is missing or empty')
    else:
        needed = ['当前已推进到的位置', '最近一轮发生的关键事件', '当前未回收的伏笔 / 悬念', '下一轮写作必须记住的点']
        missing = [x for x in needed if not contains_all(recap, [x])]
        if missing:
            errors.append('05_前情回顾.md missing required sections: ' + ', '.join(missing))


def check(project: Path, stage: str):
    errors = []
    stage = stage.lower()
    if stage == 'discovery':
        check_discovery(project, errors)
    elif stage == 'story-planning':
        check_planning(project, errors)
    elif stage == 'character-system':
        check_character(project, errors)
    elif stage == 'drafting':
        check_drafting(project, errors)
    elif stage == 'polishing':
        check_polishing(project, errors)
    elif stage == 'proofreading':
        check_proofreading(project, errors)
    elif stage == 'final-review':
        # final review depends on recap and manuscript presence for now
        check_proofreading(project, errors)
    else:
        errors.append(f'Unknown stage: {stage}')
    return errors


def main():
    if len(sys.argv) < 3:
        print('Usage: check_stage_complete.py <项目目录> <stage>')
        sys.exit(1)

    project = Path(sys.argv[1]).expanduser()
    stage = sys.argv[2]

    if not project.exists():
        print(f'ERROR: project not found: {project}')
        sys.exit(2)

    errors = check(project, stage)
    print(f'Project: {project}')
    print(f'Stage: {stage}')
    if errors:
        print('COMPLETE: NO')
        print('Reasons:')
        for e in errors:
            print(f'- {e}')
        sys.exit(2)
    else:
        print('COMPLETE: YES')
        sys.exit(0)


if __name__ == '__main__':
    main()
