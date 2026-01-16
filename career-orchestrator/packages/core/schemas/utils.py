# packages/core/schemas/utils.py
"""공통 유틸리티 함수들 - schema 파일들에서 공유 사용."""

from __future__ import annotations


def norm_text(s: str) -> str:
    """
    텍스트 최소 정규화(공백 정리).
    키워드 표준화는 normalize_keywords_tool에서 더 강하게 처리.
    """
    return " ".join(s.strip().split())


def dedupe_case_insensitive(items: list[str]) -> list[str]:
    """
    대소문자 구분 없이 중복 제거.
    원본 표기를 유지하면서 중복만 제거.
    """
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        key = x.lower()
        if key not in seen:
            seen.add(key)
            out.append(x)  # 원본 표기 유지
    return out
