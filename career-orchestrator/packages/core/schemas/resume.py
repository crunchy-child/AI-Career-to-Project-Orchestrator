from __future__ import annotations  # For Version < 3.10

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .keyword_base import BaseKeyword
from .utils import dedupe_resume_keywords


class ResumeKeyword(BaseKeyword):
    """
    Resume에서 추출한 키워드 1개.
<<<<<<< HEAD
    카테고리 구분 없이 키워드와 evidence만 저장.
    """

    pass  # BaseKeyword의 keyword_text, evidence 필드만 사용


# class ResumeBullet(BaseModel):
#     """Experience/Project 섹션의 bullet 한 줄."""
#     model_config = ConfigDict(extra="forbid")

#     text: str = Field(..., min_length=1, description="원본 bullet 문장")
#     # 나중에 키워드 추출을 해두면 점수 계산/근거 제시가 쉬움 (선택)
#     keywords: list[ResumeKeyword] = Field(default_factory=list, description="이 bullet에서 추출한 키워드(선택)")


# class ResumeEntry(BaseModel):
#     """Experience 또는 Project 항목 하나."""
#     model_config = ConfigDict(extra="forbid")

#     entry_type: Literal["experience", "project"] = Field(..., description="경력/프로젝트 구분")
#     title: Optional[str] = Field(default=None, description="직함 또는 프로젝트명")
#     org: Optional[str] = Field(default=None, description="회사/조직/팀")
#     start: Optional[str] = Field(default=None, description="시작일(문자열, MVP)")
#     end: Optional[str] = Field(default=None, description="종료일(문자열, MVP)")
#     bullets: list[ResumeBullet] = Field(default_factory=list, description="성과/업무 bullet 목록")
=======
    카테고리는 "resume"로 고정 (JD 카테고리와 구분용).
    모든 Resume 키워드는 동등하게 취급.
    """

    category: str = Field(default="resume", description="FIXED: resume")
>>>>>>> main


# class ResumeEducation(BaseModel):
#     """학력은 v2 점수에는 미포함이지만, 추후 eligibility 체크를 위해 구조만 둠."""
#     model_config = ConfigDict(extra="forbid")

#     school: Optional[str] = None
#     degree: Optional[str] = Field(default=None, description="BS/MS/PhD 등")
#     major: Optional[str] = None
#     graduation_year: Optional[str] = None
#     status: Optional[Literal["graduated", "enrolled", "leave", "expected"]] = None


class ResumeProfile(BaseModel):
    """
<<<<<<< HEAD
    ResumeParserTool 출력 + NormalizeKeywordsTool 출력(동일 스키마).
    Resume에서 추출한 기술 키워드들을 저장한다.
=======
    ResumeParserTool 출력.
    Resume에서 추출한 기술 키워드 목록을 저장.
    카테고리 구분 없이 모든 키워드를 동등하게 취급.
>>>>>>> main
    """

    model_config = ConfigDict(extra="forbid")

    # 원문(디버깅/추적용)
    raw_text: Optional[str] = Field(
        default=None, description="사용자가 붙여넣은 원문 레주메(선택)"
    )

    keywords: list[ResumeKeyword] = Field(
        default_factory=list, description="Resume에서 추출한 기술 키워드 목록"
    )

    # 학력(현재 점수에는 미포함; 추후 eligibility/필터에 활용 가능)
    # education: list[ResumeEducation] = Field(default_factory=list)

    # 정규화 상태(너희 설계에서 NormalizeKeywordsTool이 True로 바꿔서 반환)
    normalized: bool = Field(default=False, description="JD 기준 정규화 적용 여부")
    normalization_notes: list[str] = Field(
        default_factory=list, description="정규화 과정 메모(선택)"
    )
    # normalization_map_applied: dict[str, str] = Field(
    #     default_factory=dict,
    #     description="적용된 alias/표기 변환 맵 (예: {'cicd':'CI/CD'})",
    # )

    # --------- 편의 필드 ---------
    validated_keywords_set: list[ResumeKeyword] = Field(
        default_factory=list,
<<<<<<< HEAD
        description="Resume에서 추출한 키워드의 정규화/중복 제거 버전(선택, tool이 채움)",
=======
        description="정규화/중복 제거된 키워드 목록(선택, normalize_keywords_tool이 채움)",
>>>>>>> main
    )

    # --------- Validators ---------

    @field_validator("keywords")
    @classmethod
    def normalize_keywords(cls, v: list[ResumeKeyword]) -> list[ResumeKeyword]:
<<<<<<< HEAD
        return dedupe_resume_keywords(v)
=======
        """중복 제거 및 소문자 정규화."""
        return dedupe_resume_keywords(v)
>>>>>>> main
