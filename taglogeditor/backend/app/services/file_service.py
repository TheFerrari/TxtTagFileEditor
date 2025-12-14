from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from ..utils.tag_processing import (
    aggregate_counts,
    build_full_key,
    filter_banned,
    filter_by_threshold,
    normalize_whitespace,
    parse_tag_line,
)

TAG_FILE_EXTENSION = ".txt"


def iter_tag_files(root_path: Path) -> Iterable[Path]:
    for dirpath, _, filenames in os.walk(root_path):
        for name in filenames:
            if name.lower().endswith(TAG_FILE_EXTENSION):
                yield Path(dirpath) / name


def load_tags_from_file(path: Path) -> List[Tuple[str, str, bool, str]]:
    tags: List[Tuple[str, str, bool, str]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            namespace, tag, has_ns = parse_tag_line(line)
            tags.append((namespace, tag, has_ns, line.rstrip("\n\r")))
    return tags


def scan_directory(root_path: Path, min_count: int, banned_rules: List[str], case_insensitive: bool):
    file_tags: Dict[str, List[Tuple[str, str]]] = {}
    files_found: List[str] = []

    for path in iter_tag_files(root_path):
        tags_in_file: List[Tuple[str, str]] = []
        for namespace, tag, _, _ in load_tags_from_file(path):
            if not tag:
                continue
            full_key = build_full_key(namespace, tag)
            if filter_banned(full_key, banned_rules, case_insensitive):
                continue
            tags_in_file.append((namespace, tag))
        file_tags[str(path)] = tags_in_file
        files_found.append(str(path))

    counts = aggregate_counts(file_tags)
    filtered_counts = filter_by_threshold(counts, min_count)
    return {
        "files_found": files_found,
        "total_files": len(files_found),
        "counts": filtered_counts,
    }


def make_backup_dir(root_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = root_path / ".taglogeditor_backups" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def should_remove(full_key: str, selected: Dict[str, List[str]], banned: List[str], case_insensitive: bool) -> bool:
    ns, tag = full_key.split(":", 1)
    selected_set = {build_full_key(ns_key, tag_item) for ns_key, tags in selected.items() for tag_item in tags}
    if full_key in selected_set:
        return True
    return filter_banned(full_key, banned, case_insensitive)


def process_file(
    path: Path,
    selected: Dict[str, List[str]],
    banned: List[str],
    case_insensitive: bool,
    sort_lines: bool,
) -> Tuple[bool, int, List[str], List[str]]:
    original_lines: List[str] = []
    kept_lines: List[str] = []
    removed_count = 0

    for namespace, tag, has_ns, raw_line in load_tags_from_file(path):
        if not tag:
            continue
        full_key = build_full_key(namespace, tag)
        original_line = raw_line.rstrip()
        original_lines.append(original_line)
        if should_remove(full_key, selected, banned, case_insensitive):
            removed_count += 1
            continue
        cleaned = normalize_whitespace(tag)
        if has_ns and namespace:
            line_out = f"{namespace}:{cleaned}"
        else:
            line_out = cleaned
        if line_out:
            kept_lines.append(line_out)

    # remove empty lines and trailing whitespace already cleaned
    kept_lines = [ln for ln in kept_lines if ln.strip()]
    if sort_lines:
        kept_lines = sorted(kept_lines)

    changed = kept_lines != original_lines
    return changed, removed_count, original_lines, kept_lines


def write_file(path: Path, lines: List[str]):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for line in lines:
            handle.write(line.rstrip() + "\n")


def preview_changes(
    root_path: Path,
    selected: Dict[str, List[str]],
    banned: List[str],
    case_insensitive: bool,
    sort_lines: bool,
    preview_limit: int = 5,
):
    changes = []
    files_modified = 0
    tags_removed = 0

    for path in iter_tag_files(root_path):
        changed, removed_count, original_lines, kept_lines = process_file(
            path, selected, banned, case_insensitive, sort_lines
        )
        if changed:
            files_modified += 1
            tags_removed += removed_count
            if len(changes) < preview_limit:
                changes.append(
                    {
                        "file": str(path),
                        "before": original_lines,
                        "after": kept_lines,
                        "removed": removed_count,
                    }
                )

    return {
        "files_modified": files_modified,
        "tags_removed": tags_removed,
        "previews": changes,
    }


def apply_changes(
    root_path: Path,
    selected: Dict[str, List[str]],
    banned: List[str],
    case_insensitive: bool,
    sort_lines: bool,
):
    backup_dir = make_backup_dir(root_path)
    files_modified = 0
    tags_removed = 0

    for path in iter_tag_files(root_path):
        changed, removed_count, original_lines, kept_lines = process_file(
            path, selected, banned, case_insensitive, sort_lines
        )
        if not changed:
            continue
        files_modified += 1
        tags_removed += removed_count

        # backup
        relative_path = path.relative_to(root_path)
        dest = backup_dir / relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)

        # write changes
        write_file(path, kept_lines)

    return {
        "backup_path": str(backup_dir),
        "files_modified": files_modified,
        "tags_removed": tags_removed,
    }
