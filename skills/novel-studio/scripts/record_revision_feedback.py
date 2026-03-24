#!/usr/bin/env python3
from pathlib import Path
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


def main():
    if len(sys.argv) < 5:
        print('Usage: record_revision_feedback.py <项目目录> <feedbackType> <overrideMode:add_on|override> <feedbackSummary>')
        sys.exit(1)

    project = Path(sys.argv[1]).expanduser()
    state_file = project / '.novel-state.json'
    feedback_type = sys.argv[2]
    override_mode = sys.argv[3]
    summary = ' '.join(sys.argv[4:])

    data = load_or_init(state_file, project)
    data.setdefault('revision', {})
    data['revision'].update({
        'active': True,
        'feedbackType': feedback_type,
        'feedbackSummary': summary,
        'affectedStages': data['revision'].get('affectedStages', []),
        'affectedFiles': data['revision'].get('affectedFiles', []),
        'overrideMode': override_mode,
        'currentRevisionGate': 'awaiting_revision_scope_confirmation',
        'awaitingUserApproval': True,
    })
    data['updatedAt'] = now_iso()
    state_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
