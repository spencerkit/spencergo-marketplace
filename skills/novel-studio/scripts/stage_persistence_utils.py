from __future__ import annotations

from datetime import datetime, timezone

PROOFREADING_REPORT = '05A_本轮校对报告.md'
WORKFLOW_STATUSES = {
    'collecting_inputs',
    'producing_artifact',
    'awaiting_user_approval',
    'brainstorming',
    'blocked',
}
STAGE_REVIEW_GATES = {
    'discovery': 'waiting_discovery_feedback',
    'story-planning': 'waiting_planning_feedback',
    'character-system': 'waiting_character_feedback',
    'drafting': 'waiting_draft_feedback',
    'polishing': 'waiting_polishing_feedback',
    'proofreading': 'waiting_proofreading_feedback',
    'final-review': 'waiting_final_review_feedback',
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def gate_for_stage(stage: str, substage: str | None = None) -> str:
    if stage == 'drafting' and substage in {'opening-design', 'opening-review'}:
        return 'waiting_opening_feedback'
    return STAGE_REVIEW_GATES[stage]


def normalize_path_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    normalized = []
    for value in values:
        if isinstance(value, str) and value.strip():
            normalized.append(value.strip())
    return normalized
