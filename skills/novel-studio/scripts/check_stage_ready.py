#!/usr/bin/env python3
from pathlib import Path
import sys, json

from check_stage_complete import check as check_stage_complete
from load_project_state import reconstruct
from revision_utils import normalize_state


def exists_nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.read_text(encoding='utf-8').strip() != ''


def count_md(dirpath: Path) -> int:
    return len(list(dirpath.glob('*.md'))) if dirpath.is_dir() else 0


def load_state(project: Path):
    state_file = project / '.novel-state.json'
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding='utf-8')), None
        except Exception:
            return None, f'.novel-state.json is not valid JSON: {state_file}'
    return normalize_state(reconstruct(project), project), None


def state_gate_errors(state, stage):
    errs = []
    if not state:
        return errs
    review = state.get('review', {})
    batch = state.get('batch', {})
    approvals = state.get('approvals', {})
    revision = state.get('revision', {})

    gate = review.get('currentGate')
    if gate and stage in ['drafting', 'polishing', 'proofreading', 'final-review']:
        errs.append(f'Current review gate is still open: {gate}')

    revision_gate = revision.get('currentRevisionGate') or revision.get('currentGate')
    if revision_gate and stage == 'final-review':
        errs.append(f'Current revision gate is still open: {revision_gate}')

    if stage == 'story-planning' and not approvals.get('discoveryApproved', False):
        errs.append('Discovery stage not explicitly approved yet')
    if stage == 'character-system' and not approvals.get('planningApproved', False):
        errs.append('Story planning stage not explicitly approved yet')
    if stage == 'drafting' and not approvals.get('characterApproved', False):
        errs.append('Character system stage not explicitly approved yet')
    if stage == 'polishing' and not batch.get('draftComplete', False):
        errs.append('Current batch draft is not marked complete yet')
    if stage == 'proofreading' and not batch.get('polishingComplete', False):
        errs.append('Current batch polishing is not marked complete yet')
    if stage == 'final-review' and not batch.get('proofreadingComplete', False):
        errs.append('Current batch proofreading is not marked complete yet')
    if stage == 'drafting' and batch.get('active') and not batch.get('scopeConfirmed', False):
        errs.append('Current batch scope is not confirmed yet')
    if stage == 'drafting' and batch.get('active') and not batch.get('chapterPlanApproved', False):
        errs.append('Current batch chapter plan is not approved yet')
    return errs


def file_gate_errors(project: Path, stage: str):
    errors = []
    stage = stage.lower()
    f00 = project / '00_选题报告.md'
    f01 = project / '01_想法.md'
    f02 = project / '02_大纲.md'
    f03 = project / '03_人物小传.md'
    chars = project / 'characters'
    manu = project / 'manuscript'

    if stage == 'discovery':
        pass
    elif stage == 'story-planning':
        if not exists_nonempty(f00):
            errors.append('00_选题报告.md is missing or empty')
    elif stage == 'character-system':
        if not exists_nonempty(f02):
            errors.append('02_大纲.md is missing or empty')
    elif stage == 'drafting':
        if not exists_nonempty(f02):
            errors.append('02_大纲.md is missing or empty')
        if count_md(chars) == 0 and not exists_nonempty(f03):
            errors.append('No usable character package found')
    elif stage == 'polishing':
        if count_md(manu) == 0:
            errors.append('No manuscript files found in manuscript/')
    elif stage == 'proofreading':
        if count_md(manu) == 0:
            errors.append('No manuscript files found in manuscript/')
    elif stage == 'final-review':
        if count_md(manu) == 0:
            errors.append('No manuscript files found in manuscript/')
        recap = project / '05_前情回顾.md'
        if not exists_nonempty(recap):
            errors.append('05_前情回顾.md is missing or empty')
    else:
        errors.append(f'Unknown stage: {stage}')
    return errors


def main():
    if len(sys.argv) < 3:
        print('Usage: check_stage_ready.py <项目目录> <stage>')
        sys.exit(1)

    project = Path(sys.argv[1]).expanduser()
    stage = sys.argv[2].lower()

    if not project.exists():
        print(f'ERROR: project not found: {project}')
        sys.exit(2)

    state, state_error = load_state(project)
    errors = []
    if stage == 'final-review':
        if state_error:
            errors.append(state_error)
        report = project / '07_终审报告.md'
        if exists_nonempty(report):
            errors.append('Stage is already completed: final-review (07_终审报告.md already exists)')
        proofreading_errors = check_stage_complete(project, 'proofreading')
        errors.extend(proofreading_errors)
    errors.extend(file_gate_errors(project, stage))
    errors.extend(state_gate_errors(state, stage))

    print(f'Project: {project}')
    print(f'Stage: {stage}')
    if errors:
        print('READY: NO')
        print('Reasons:')
        for e in errors:
            print(f'- {e}')
        sys.exit(2)
    else:
        print('READY: YES')
        sys.exit(0)


if __name__ == '__main__':
    main()
