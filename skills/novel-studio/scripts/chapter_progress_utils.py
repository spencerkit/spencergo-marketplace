#!/usr/bin/env python3
from __future__ import annotations

import re
from datetime import datetime, timezone
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


def resolve_dispatch_chapter_labels(stage: str, batch_plan_text: str, target_files: list[str]) -> list[str]:
    approved_labels = extract_chapter_labels_from_plan(batch_plan_text)
    if not approved_labels:
        raise ValueError('approved chapter plan does not contain any chapter headings')

    if stage == 'proofreading':
        return approved_labels

    if stage not in {'drafting', 'polishing'}:
        raise ValueError(f'unsupported stage for chapter label resolution: {stage}')
    if not target_files:
        raise ValueError(f'{stage} requires target files to resolve chapter labels')

    chapter_labels: list[str] = []
    seen: set[str] = set()
    for relpath in target_files:
        chapter_label = chapter_label_from_manuscript_path(relpath)
        if not chapter_label:
            raise ValueError(f'cannot resolve chapter label from target file: {relpath}')
        if chapter_label not in approved_labels:
            raise ValueError(f'target file chapter label is not in approved plan: {chapter_label} ({relpath})')
        if chapter_label in seen:
            raise ValueError(f'ambiguous target files map to the same chapter label: {chapter_label}')
        seen.add(chapter_label)
        chapter_labels.append(chapter_label)
    return chapter_labels


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


def human_summary(chapter_label: str, phase: str, phase_status: str, blockers: list[str] | None = None) -> str:
    blockers = list(blockers or [])
    if phase == 'blocked' or phase_status == 'blocked':
        if blockers:
            return f'{chapter_label}阻塞：{blockers[0]}'
        return f'{chapter_label}阻塞'

    summaries = {
        ('drafting', 'in_progress'): f'{chapter_label}初稿中',
        ('drafting', 'awaiting_user_review'): f'{chapter_label}初稿待审核',
        ('polishing', 'in_progress'): f'{chapter_label}润色中',
        ('proofreading', 'in_progress'): f'{chapter_label}校对中',
        ('proofreading', 'awaiting_user_review'): f'{chapter_label}审核中',
        ('proofreading', 'completed'): f'{chapter_label}已完成',
    }
    try:
        return summaries[(phase, phase_status)]
    except KeyError as exc:
        raise ValueError(f'unsupported summary state: {phase}/{phase_status}') from exc


def ensure_chapter_task(batch: dict, chapter_label: str) -> dict:
    normalize_progress_batch(batch)
    for task in batch['chapterTasks']:
        if task.get('chapterLabel') == chapter_label:
            return task
    task = chapter_task(chapter_label)
    batch['chapterTasks'].append(task)
    return task


def append_progress_event(
    batch: dict,
    chapter_label: str,
    phase: str,
    phase_status: str,
    summary: str,
    blockers: list[str] | None = None,
) -> dict:
    normalize_progress_batch(batch)
    event = {
        'chapterLabel': chapter_label,
        'phase': phase,
        'phaseStatus': phase_status,
        'summary': summary,
        'blockers': list(blockers or []),
    }
    batch['pendingProgressItems'].append(event)
    return event


def mark_dispatch_started(batch: dict, phase: str, chapter_labels: list[str], target_files: list[str]) -> dict:
    normalize_progress_batch(batch)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    manuscript_paths_by_label: dict[str, str] = {}
    if phase in {'drafting', 'polishing'}:
        if len(chapter_labels) != len(target_files):
            raise ValueError(f'{phase} dispatch target files must align 1:1 with chapter labels')
        for chapter_label, relpath in zip(chapter_labels, target_files):
            derived_label = chapter_label_from_manuscript_path(relpath)
            if derived_label and derived_label != chapter_label:
                raise ValueError(
                    f'target file chapter label mismatch for {relpath}: expected {chapter_label}, got {derived_label}'
                )
            manuscript_paths_by_label[chapter_label] = relpath

    for chapter_label in chapter_labels:
        task = ensure_chapter_task(batch, chapter_label)
        summary = human_summary(chapter_label, phase, 'in_progress')
        task['phase'] = phase
        task['phaseStatus'] = 'in_progress'
        if chapter_label in manuscript_paths_by_label:
            task['manuscriptPath'] = manuscript_paths_by_label[chapter_label]
        task['lastSummary'] = summary
        task['blockers'] = []
        task['updatedAt'] = timestamp
        append_progress_event(batch, chapter_label, phase, 'in_progress', summary)

    return batch
