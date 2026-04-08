#!/usr/bin/env python3
"""Initialize a new novel project in the current working directory.

Usage:
    init_novel_project.py <小说名称>
    init_novel_project.py <小说名称> --root /path/to/parent

Default: creates ./[小说名称]/ in the current directory.
"""
from pathlib import Path
import sys

DEFAULT_ROOT = Path.cwd()

TEMPLATE_FILES = [
    '00_选题报告.md',
    '01_想法.md',
    '02_大纲.md',
    '03_人物小传.md',
    '04_章节骨架.md',
]

TEMPLATE_TEXT = {
    '00_选题报告.md': '# 00_选题报告\n\n',
    '01_想法.md': '# 01_想法\n\n',
    '02_大纲.md': '# 02_大纲\n\n',
    '03_人物小传.md': '# 03_人物小传\n\n',
    '04_章节骨架.md': '# 04_章节骨架\n\n',
}


def main():
    args = sys.argv[1:]
    if not args:
        print('Usage: init_novel_project.py <小说名称> [--root /path/to/novels]')
        sys.exit(1)

    title = None
    root = DEFAULT_ROOT

    i = 0
    while i < len(args):
        if args[i] == '--root' and i + 1 < len(args):
            root = Path(args[i + 1]).expanduser()
            i += 2
        elif title is None:
            title = args[i].strip()
            i += 1
        else:
            i += 1

    if not title:
        print('Error: missing <小说名称>')
        sys.exit(1)

    project = root / title
    project.mkdir(parents=True, exist_ok=True)
    (project / 'characters').mkdir(exist_ok=True)
    (project / 'manuscript').mkdir(exist_ok=True)

    created = []
    for name in TEMPLATE_FILES:
        path = project / name
        if not path.exists():
            path.write_text(TEMPLATE_TEXT[name], encoding='utf-8')
            created.append(name)

    print(f'Project: {project}')
    print('Created files:')
    for name in created:
        print(f'- {name}')
    print('Directories:')
    print('- characters/')
    print('- manuscript/')


if __name__ == '__main__':
    main()
