#!/usr/bin/env python3
from pathlib import Path
import argparse
import json, sys
from datetime import datetime, timezone


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_or_init(state_file: Path, project: Path):
    if state_file.exists():
        return json.loads(state_file.read_text(encoding='utf-8'))
    return {
        'project': {'title': project.name, 'rootPath': str(project)},
        'workflow': {'currentStage': None, 'currentSubstage': None, 'lastCompletedStage': None, 'nextStage': None, 'status': 'in_progress'},
        'approvals': {},
        'artifacts': {},
        'batch': {},
        'review': {},
        'revision': {},
        'blockingIssues': [],
        'notes': {},
        'updatedAt': now_iso(),
    }


def parse_value(raw):
    low = raw.lower()
    if low == 'true':
        return True
    if low == 'false':
        return False
    if low == 'null':
        return None
    return raw


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('project')
    parser.add_argument('field')
    parser.add_argument('value')
    parser.add_argument('--json', action='store_true', dest='json_mode')
    return parser.parse_args()


def main():
    args = parse_args()
    project = Path(args.project).expanduser()
    state_file = project / '.novel-state.json'
    field = args.field
    value = json.loads(args.value) if args.json_mode else parse_value(args.value)

    data = load_or_init(state_file, project)

    if '.' not in field:
        print('Field must be section.key format')
        sys.exit(2)

    section, key = field.split('.', 1)
    if section not in data:
        data[section] = {}

    if isinstance(data[section], dict):
        data[section][key] = value
    else:
        print(f'Section {section} is not a dict')
        sys.exit(2)

    data['updatedAt'] = now_iso()
    state_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
