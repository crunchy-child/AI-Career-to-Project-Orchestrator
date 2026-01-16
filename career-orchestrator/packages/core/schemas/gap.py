# packages/core/schemas/gap.py
from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .utils import norm_text, dedupe_case_insensitive


JDCategory = Literal["required", "preferred"]


class KeywordEvidence(BaseModel):
    """
    특정 키워드가 Resume 어디에 근거로 존재했는지 기록.
    점수 계산(Experience/Project vs Skills-only)에도 그대로 사용 가능.
    """
    model_config = ConfigDict(extra="forbid")

    keyword: str = Field(..., min_length=1)
    jd_category: JDCategory = Field(..., description="JD에서 required인지 preferred인지")
    found_in: Literal["experience_project", "skills_only", "missing"] = Field(
        ...,
        description="Resume에서 키워드가 발견된 위치",
    )
    jd_evidence: Optional[str] = Field(default=None, description="JD에서 키워드가 등장한 근거(선택)")
    resume_evidence: Optional[str] = Field(
        default=None,
        description="Resume에서 키워드가 등장한 근거(선택: bullet 일부/문장 일부)",
    )

    # 점수 계산에 사용된 값(디버깅/설명용, 선택)
    base_weight: Optional[float] = Field(default=None, description="required=0.7, preferred=0.3")
    multiplier: Optional[float] = Field(default=None, description="위치 기반 multiplier(예: req exp=1.0)")
    contribution: Optional[float] = Field(default=None, description="base_weight * multiplier")


class MatchScoreBreakdown(BaseModel):
    """
    매칭 점수 계산 세부내역(선택이지만 추천).
    README에 있는 공식을 구현/검증하기 쉬워짐.
    """
    model_config = ConfigDict(extra="forbid")

    max_possible_sum: float = Field(..., ge=0)
    covered_sum: float = Field(..., ge=0)
    required_base_sum: float = Field(default=0.0, ge=0)
    preferred_base_sum: float = Field(default=0.0, ge=0)
    required_covered_sum: float = Field(default=0.0, ge=0)
    preferred_covered_sum: float = Field(default=0.0, ge=0)


class GapSummary(BaseModel):
    """
    ResumeAnalysisAgent의 핵심 산출물.
    - 점수(0~100)
    - strong/partial/missing
    - validated_missing_keywords
    - (선택) 키워드별 근거 + 점수 breakdown
    """
    model_config = ConfigDict(extra="forbid")

    match_score: int = Field(..., ge=0, le=100)

    # 분류 결과
    strong_matches: list[str] = Field(default_factory=list, description="Resume에 강하게 존재(주로 exp/project)")
    partial_matches: list[str] = Field(default_factory=list, description="약하게 존재(예: skills-only 또는 fuzzy)")
    missing_keywords: list[str] = Field(default_factory=list, description="초기 missing(검증 전)")
    validated_missing_keywords: list[str] = Field(default_factory=list, description="검증 후 missing")

    # 요약/근거
    notes: Optional[str] = Field(default=None, description="점수/갭에 대한 짧은 설명")

    # 선택: 디버깅/설명/시각화에 유용
    breakdown: Optional[MatchScoreBreakdown] = None
    evidences: list[KeywordEvidence] = Field(default_factory=list)

    # --------- Validators ---------
    @field_validator("strong_matches", "partial_matches", "missing_keywords", "validated_missing_keywords")
    @classmethod
    def normalize_lists(cls, v: list[str]) -> list[str]:
        cleaned = [norm_text(x) for x in v if isinstance(x, str) and x.strip()]
        return dedupe_case_insensitive(cleaned)

    @field_validator("evidences")
    @classmethod
    def normalize_evidences(cls, v: list[KeywordEvidence]) -> list[KeywordEvidence]:
        for e in v:
            e.keyword = norm_text(e.keyword)
            if e.jd_evidence:
                e.jd_evidence = norm_text(e.jd_evidence)
            if e.resume_evidence:
                e.resume_evidence = norm_text(e.resume_evidence)
        return v
