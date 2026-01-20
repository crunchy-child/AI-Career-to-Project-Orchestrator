# packages/core/__init__.py
"""
Core package: 데이터 스키마 및 공통 유틸리티.
"""

from .schemas import (
    BaseKeyword,
    ResumeProfile,
    ResumeKeyword,
    JDProfile,
    JDKeyword,
    GapSummary,
    KeywordMatch,
    ProjectOutput,
    ProjectPlan,
    ProjectIdea,
    ArchitectureSpec,
    DayPlan,
)

__all__ = [
    "BaseKeyword",
    "ResumeProfile",
    "ResumeKeyword",
    "JDProfile",
    "JDKeyword",
    "GapSummary",
    "KeywordMatch",
    "ProjectOutput",
    "ProjectPlan",
    "ProjectIdea",
    "ArchitectureSpec",
    "DayPlan",
]
