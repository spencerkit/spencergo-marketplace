#!/usr/bin/env python3
from pathlib import Path
import json, sys


def exists_nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.read_text(encoding='utf-8').strip() != ''


def count_md(dirpath: Path) -> int:
    return len(list(dirpath.glob('*.md'))) if dirpath.is_dir() else 0


def reconstruct(project: Path):
    state = {
        'project': {
            'title': project.name,
            'rootPath': str(project),
        },
        'workflow': {
            'currentStage': 'discovery',
            'currentSubstage': None,
            'lastCompletedStage': None,
            'nextStage': 'discovery',
            'status': 'reconstructed',
        },
        'approvals': {
            'discoveryApproved': False,
            'planningApproved': False,
            'characterApproved': False,
            'draftingApproved': False,
            'polishingApproved': False,
            'proofreadingApproved': False,
            'finalApproved': False,
            'titleConfirmed': False,
            'workingTitleApproved': False,
        },
        'artifacts': {
            'hotSearchScan': exists_nonempty(project / '00A_热点扫描.md'),
            'userPreference': exists_nonempty(project / '00B_用户偏好.md'),
            'topicReport': exists_nonempty(project / '00_选题报告.md'),
            'ideaDoc': exists_nonempty(project / '01_想法.md'),
            'outlineDoc': exists_nonempty(project / '02_大纲.md'),
            'characterSummary': exists_nonempty(project / '03_人物小传.md'),
            'chapterSkeleton': exists_nonempty(project / '04_章节骨架.md'),
            'recapDoc': exists_nonempty(project / '05_前情回顾.md'),
            'characterFiles': count_md(project / 'characters') > 0,
            'manuscriptFiles': count_md(project / 'manuscript') > 0,
            'feishuSynced': False,
        },
        'batch': {
            'active': False,
            'chapterRange': None,
            'chapterCount': None,
            'scopeConfirmed': False,
            'chapterPlanExists': exists_nonempty(project / '05_本轮章节规划.md'),
            'chapterPlanApproved': False,
            'draftComplete': False,
            'polishingComplete': False,
            'proofreadingComplete': False,
            'recapUpdated': exists_nonempty(project / '05_前情回顾.md'),
            'awaitingNextBatchDecision': False,
            'focus': None,
            'attractionPoints': [],
            'climaxTarget': None,
        },
        'review': {
            'currentGate': None,
            'lastUserFeedbackSummary': None,
            'lastRevisionFocus': None,
            'lastRejectedReason': None,
        },
        'blockingIssues': [],
        'notes': {},
    }

    a = state['artifacts']
    if a['topicReport']:
        state['workflow']['lastCompletedStage'] = 'discovery'
        state['workflow']['currentStage'] = 'story-planning'
        state['workflow']['nextStage'] = 'story-planning'
    if a['outlineDoc']:
        state['workflow']['lastCompletedStage'] = 'story-planning'
        state['workflow']['currentStage'] = 'character-system'
        state['workflow']['nextStage'] = 'character-system'
    if a['characterFiles'] or a['characterSummary']:
        state['workflow']['lastCompletedStage'] = 'character-system'
        state['workflow']['currentStage'] = 'drafting'
        state['workflow']['nextStage'] = 'drafting'
    if a['manuscriptFiles']:
        state['workflow']['lastCompletedStage'] = 'drafting'
        state['workflow']['currentStage'] = 'polishing'
        state['workflow']['nextStage'] = 'polishing'
        state['batch']['active'] = True
        state['batch']['draftComplete'] = True
    return state


def main():
    if len(sys.argv) < 2:
        print('Usage: load_project_state.py <项目目录>')
        sys.exit(1)

    project = Path(sys.argv[1]).expanduser()
    state_file = project / '.novel-state.json'
    if state_file.exists():
        data = json.loads(state_file.read_text(encoding='utf-8'))
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    data = reconstruct(project)
    state_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
