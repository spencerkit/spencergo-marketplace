#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from chapter_progress_utils import apply_result_to_chapters
from revision_utils import load_state, save_state
from stage_execution_utils import (
    base_result_summary_fields,
    ensure_project,
    now_iso,
    read_json_file,
    validate_bundle_and_result,
)
from stage_persistence_utils import PROOFREADING_REPORT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Apply a validated subagent stage result into project state.')
    parser.add_argument('project')
    parser.add_argument('--bundle-file', required=True)
    parser.add_argument('--result-file', required=True)
    return parser.parse_args()


def stage_gate(stage: str) -> str:
    return {
        'drafting': 'waiting_draft_feedback',
        'polishing': 'waiting_polishing_feedback',
        'proofreading': 'waiting_proofreading_feedback',
    }[stage]


def delegation_blockers(validated: dict[str, object]) -> list[str]:
    result = validated['result']
    if validated['stage'] == 'proofreading' and result.get('status') == 'completed':
        return list(result.get('blockers') or [])
    return list(result.get('blockedReasons') or [])


def apply_validated_state(data: dict, validated: dict[str, object]) -> None:
    stage = validated['stage']
    package = validated['package']
    result = validated['result']

    batch = data.setdefault('batch', {})
    for key, value in base_result_summary_fields().items():
        batch.setdefault(key, value if not isinstance(value, list) else list(value))

    apply_result_to_chapters(
        batch,
        stage,
        package['requiredInputs']['chapterLabels'],
        package['targetFiles'],
        result,
    )
    blockers = delegation_blockers(validated)
    batch['lastDelegatedStage'] = stage
    batch['lastDelegatedScope'] = package.get('batchRange')
    batch['lastDelegationStatus'] = result.get('status')
    batch['lastDelegationSummary'] = result.get('summary')
    batch['lastDelegationBlockers'] = blockers
    batch['lastDelegationRisks'] = list(result.get('risks') or [])
    batch['lastDelegatedAt'] = now_iso()

    workflow = data.setdefault('workflow', {})
    review = data.setdefault('review', {})
    artifacts = data.setdefault('artifacts', {})
    workflow['status'] = 'awaiting_user_approval' if result['status'] == 'completed' else 'blocked'

    if stage == 'drafting' and result['status'] == 'completed':
        batch['draftComplete'] = True
        review['currentGate'] = stage_gate(stage)
    elif stage == 'polishing' and result['status'] == 'completed':
        batch['polishingComplete'] = True
        review['currentGate'] = stage_gate(stage)
    elif stage == 'proofreading' and result['status'] == 'completed':
        batch['proofreadingComplete'] = result.get('judgment') != 'needs revision'
        review['currentGate'] = stage_gate(stage)
        review['pendingArtifactPaths'] = [PROOFREADING_REPORT]
        review['lastPersistedStage'] = 'proofreading'
        review['lastPersistedAt'] = now_iso()
        artifacts['proofreadingReport'] = True


def main() -> None:
    args = parse_args()
    try:
        project = ensure_project(Path(args.project))
        bundle = read_json_file(Path(args.bundle_file))
        result = read_json_file(Path(args.result_file))
        validated = validate_bundle_and_result(project, bundle, result)
        data = load_state(project)
        apply_validated_state(data, validated)
        save_state(project, data)
        saved = load_state(project)
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)
    print(json.dumps(saved, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
