#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from revision_utils import load_state, save_state

APPROVAL_TRANSITIONS = {
    'waiting_discovery_feedback': ('discovery', 'discoveryApproved', 'story-planning'),
    'waiting_planning_feedback': ('story-planning', 'planningApproved', 'character-system'),
    'waiting_character_feedback': ('character-system', 'characterApproved', 'drafting'),
    'waiting_opening_feedback': ('drafting', 'openingApproved', 'drafting'),
    'waiting_draft_feedback': ('drafting', 'draftingApproved', 'polishing'),
    'waiting_polishing_feedback': ('polishing', 'polishingApproved', 'proofreading'),
    'waiting_proofreading_feedback': ('proofreading', 'proofreadingApproved', 'final-review'),
    'waiting_final_review_feedback': ('final-review', 'finalApproved', None),
}


def main() -> int:
    if len(sys.argv) < 3:
        print('Usage: approve_stage_gate.py <项目目录> <gate>')
        return 1

    project = Path(sys.argv[1]).expanduser()
    gate = sys.argv[2].strip()

    if not project.exists():
        print(f'ERROR: project not found: {project}', file=sys.stderr)
        return 2

    if gate not in APPROVAL_TRANSITIONS:
        print(f'ERROR: unsupported gate: {gate}', file=sys.stderr)
        return 2

    state = load_state(project)
    review = state['review']
    current_gate = review.get('currentGate')
    if current_gate != gate:
        print(
            f'ERROR: gate mismatch, expected currentGate={current_gate or "None"}, got {gate}',
            file=sys.stderr,
        )
        return 2

    stage, approval_key, next_stage = APPROVAL_TRANSITIONS[gate]
    state['approvals'][approval_key] = True

    workflow = state['workflow']
    workflow['lastCompletedStage'] = stage
    workflow['currentStage'] = next_stage
    workflow['nextStage'] = next_stage
    workflow['status'] = 'collecting_inputs'

    review['currentGate'] = None
    review['pendingArtifactPaths'] = []

    save_state(project, state)
    print(f'APPROVED: {gate}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
