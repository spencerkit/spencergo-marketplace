#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import PurePosixPath

CHAPTER_LABEL_RE = re.compile(r'(第[0-9零一二三四五六七八九十百千万两]+章)')
PLAN_HEADING_RE = re.compile(r'^\s*###\s+(第[0-9零一二三四五六七八九十百千万两]+章)(?:\s|$|[:：])')


def extract_chapter_labels_from_plan(plan_text: str) -> list[str]:
    labels: list[str] = []
    seen: set[str] = set()
    for line in plan_text.splitlines():
        match = PLAN_HEADING_RE.match(line)
        if not match:
            continue
        label = match.group(1)
        if label in seen:
            continue
        seen.add(label)
        labels.append(label)
    return labels


def chapter_label_from_manuscript_path(relpath: str) -> str | None:
    stem = PurePosixPath(relpath).stem
    match = CHAPTER_LABEL_RE.match(stem)
    return match.group(1) if match else None


def default_progress_fields() -> dict:
    return {
        'chapterTasks': [],
        'pendingProgressItems': [],
    }


def chapter_task(label: str, manuscript_path: str | None = None) -> dict:
    return {
        'chapterLabel': label,
        'manuscriptPath': manuscript_path,
        'phase': 'drafting',
        'phaseStatus': 'queued',
        'lastSummary': None,
        'blockers': [],
        'updatedAt': None,
    }


def normalize_progress_batch(batch: dict) -> dict:
    fields = default_progress_fields()
    for key, default_value in fields.items():
        value = batch.get(key)
        batch[key] = list(value) if isinstance(value, list) else list(default_value)
    normalized_tasks: list[dict] = []
    for item in batch['chapterTasks']:
        if not isinstance(item, dict):
            continue
        task = dict(item)
        chapter_label = task.pop('chapterLabel', None)
        if chapter_label is None and 'label' in task:
            chapter_label = task.pop('label')
        else:
            task.pop('label', None)
        if not chapter_label:
            continue
        hydrated_task = chapter_task(chapter_label, task.get('manuscriptPath'))
        hydrated_task.update(task)
        normalized_tasks.append(hydrated_task)
    batch['chapterTasks'] = normalized_tasks
    return batch


def initialize_chapter_tasks(batch: dict, plan_text: str) -> dict:
    batch['chapterTasks'] = [chapter_task(label) for label in extract_chapter_labels_from_plan(plan_text)]
    batch['pendingProgressItems'] = []
    return batch
