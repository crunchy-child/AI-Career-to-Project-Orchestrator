# packages/core/schemas/gap.py
from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

from .resume import ResumeKeyword
from .jd import JDKeyword

JDCategory = Literal["required", "preferred"]


class KeywordMatch(BaseModel):
    """
    키워드 매칭 결과.
    """
    model_config = ConfigDict(extra="forbid")
    
    keyword_pair: tuple[ResumeKeyword, JDKeyword] = Field(..., description="매칭된 키워드 쌍")
    match_type: Literal["strong", "partial", "missing"] = Field(..., description="매칭 유형")


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
    keyword_matches: list[KeywordMatch] = Field(default_factory=list, description="매칭된 키워드 목록")
    missing_keywords: list[JDKeyword] = Field(default_factory=list, description="missing keywords")
    validated_missing_keywords: list[JDKeyword] = Field(default_factory=list, description="검증 후 missing")

    # 요약/근거
    notes: Optional[str] = Field(default=None, description="점수/갭에 대한 짧은 설명")

    # --------- Validators ---------
    # @field_validator("keyword_matches", "missing_keywords", "validated_missing_keywords")
    # @classmethod
    # def normalize_lists(cls, v: list[BaseKeyword]) -> list[BaseKeyword]:
    #     # keyword_text 정규화
    #     for keyword in v:
    #         if isinstance(keyword.keyword_text, str) and keyword.keyword_text.strip():
    #             keyword.keyword_text = norm_text(keyword.keyword_text).lower()
        
    #     # 중복 제거 (keyword_text 기준)
    #     seen: set[str] = set()
    #     out: list[BaseKeyword] = []
    #     for keyword in v:
    #         if not keyword.keyword_text:
    #             continue
    #         key = keyword.keyword_text.lower()
    #         if key not in seen:
    #             seen.add(key)
    #             out.append(keyword)
    #     return out
