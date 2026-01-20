# packages/core/schemas/utils.py
"""공통 유틸리티 함수들 - schema 파일들에서 공유 사용."""

from __future__ import annotations

from typing import TypeVar

from .keyword_base import BaseKeyword


def norm_text(s: str) -> str:
    """
    텍스트 최소 정규화(공백 정리).
    키워드 표준화는 normalize_keywords_tool에서 더 강하게 처리.
    """
    return " ".join(s.strip().split())


TKeyword = TypeVar("TKeyword", bound=BaseKeyword)


def _dedupe_keywords_by_priority(
    items: list[TKeyword],
    category_priority: dict[str, int],
) -> list[TKeyword]:
    """
    대소문자 구분 없이 중복 제거하고 소문자로 저장.
    동일 키워드 충돌 시 category_priority가 높은 항목을 유지.
    """
    chosen: dict[str, TKeyword] = {}
    for item in items:
        if not isinstance(item.keyword_text, str):
            continue
        normalized = norm_text(item.keyword_text).lower()
        if not normalized:
            continue
        item.keyword_text = normalized
        existing = chosen.get(normalized)
        if existing is None:
            chosen[normalized] = item
            continue
        current_rank = category_priority.get(item.category, -1)
        existing_rank = category_priority.get(existing.category, -1)
        if current_rank > existing_rank:
            chosen[normalized] = item
    return list(chosen.values())


def dedupe_resume_keywords(items: list[TKeyword]) -> list[TKeyword]:
    """
    대소문자 구분 없이 중복 제거.
    소문자로 저장. 먼저 나온 키워드를 유지.
    카테고리 구분 없이 단순 중복 제거만 수행.
    """
    chosen: dict[str, TKeyword] = {}
    for item in items:
        if not isinstance(item.keyword_text, str):
            continue
        normalized = norm_text(item.keyword_text).lower()
        if not normalized:
            continue
        item.keyword_text = normalized
        if normalized not in chosen:
            chosen[normalized] = item
    return list(chosen.values())


def dedupe_jd_keywords(items: list[TKeyword]) -> list[TKeyword]:
    """
    대소문자 구분 없이 중복 제거.
    소문자로 저장.
    """
    # 동일 키워드 충돌 시 context < preferred < responsibility < required 순으로 버림
    return _dedupe_keywords_by_priority(
        items,
        {"context": 0, "preferred": 1, "responsibility": 2, "required": 3},
    )


def dedupe_case_insensitive(items: list[str]) -> list[str]:
    """
    문자열 리스트를 대소문자 구분 없이 중복 제거.
    소문자로 반환.
    """
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        key = x.lower()
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out
