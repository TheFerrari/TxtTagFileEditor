from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional, Tuple


def normalize_whitespace(text: str) -> str:
    return " ".join(text.strip().split())


def parse_tag_line(line: str) -> Tuple[str, str, bool]:
    cleaned = normalize_whitespace(line)
    if not cleaned:
        return "", "", False
    if ":" in cleaned:
        ns, tag = cleaned.split(":", 1)
        return ns.strip(), tag.strip(), True
    return "general", cleaned, False


def build_full_key(namespace: str, tag: str) -> str:
    ns = namespace or "general"
    return f"{ns}:{tag}"


def matches_rule(full_key: str, rule: str, case_insensitive: bool = False) -> bool:
    if not rule:
        return False
    compare_key = full_key
    compare_rule = rule
    if case_insensitive:
        compare_key = compare_key.lower()
        compare_rule = compare_rule.lower()
    if "*" in compare_rule:
        return fnmatch.fnmatch(compare_key, compare_rule)
    return compare_key == compare_rule


def filter_banned(full_key: str, rules: List[str], case_insensitive: bool = False) -> bool:
    return any(matches_rule(full_key, r.strip(), case_insensitive) for r in rules if r.strip())


def aggregate_counts(file_tags: Dict[str, List[Tuple[str, str]]]) -> Dict[str, Dict[str, int]]:
    counts: Dict[str, Dict[str, int]] = {}
    for tags in file_tags.values():
        for namespace, tag in tags:
            if not tag:
                continue
            counts.setdefault(namespace, {})[tag] = counts.setdefault(namespace, {}).get(tag, 0) + 1
    return counts


def filter_by_threshold(counts: Dict[str, Dict[str, int]], min_count: int) -> Dict[str, Dict[str, int]]:
    filtered: Dict[str, Dict[str, int]] = {}
    for ns, tags in counts.items():
        kept = {tag: cnt for tag, cnt in tags.items() if cnt >= min_count}
        if kept:
            filtered[ns] = kept
    return filtered
