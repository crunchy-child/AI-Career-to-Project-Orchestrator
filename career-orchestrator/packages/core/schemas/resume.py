# packages/core/schemas/resume.py
from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .utils import norm_text, dedupe_case_insensitive


class ResumeBullet(BaseModel):
    """Experience/Project 섹션의 bullet 한 줄."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., min_length=1, description="원본 bullet 문장")
    # 나중에 키워드 추출을 해두면 점수 계산/근거 제시가 쉬움 (선택)
    keywords: list[str] = Field(
        default_factory=list, description="이 bullet에서 추출한 키워드(선택)"
    )


class ResumeEntry(BaseModel):
    """Experience 또는 Project 항목 하나."""

    model_config = ConfigDict(extra="forbid")

    entry_type: Literal["experience", "project"] = Field(
        ..., description="경력/프로젝트 구분"
    )
    title: Optional[str] = Field(default=None, description="직함 또는 프로젝트명")
    org: Optional[str] = Field(default=None, description="회사/조직/팀")
    start: Optional[str] = Field(default=None, description="시작일(문자열, MVP)")
    end: Optional[str] = Field(default=None, description="종료일(문자열, MVP)")
    bullets: list[ResumeBullet] = Field(
        default_factory=list, description="성과/업무 bullet 목록"
    )


class ResumeEducation(BaseModel):
    """학력은 v2 점수에는 미포함이지만, 추후 eligibility 체크를 위해 구조만 둠."""

    model_config = ConfigDict(extra="forbid")

    school: Optional[str] = None
    degree: Optional[str] = Field(default=None, description="BS/MS/PhD 등")
    major: Optional[str] = None
    graduation_year: Optional[str] = None
    status: Optional[Literal["graduated", "enrolled", "leave", "expected"]] = None


class ResumeProfile(BaseModel):
    """
    ResumeParserTool 출력 + NormalizeKeywordsTool 출력(동일 스키마).
    점수 계산을 위해 Skills 섹션과 Experience/Project 섹션을 분리해서 보관한다.
    """

    model_config = ConfigDict(extra="forbid")

    # 원문(디버깅/추적용). 길면 저장 안 해도 되지만 MVP에서는 있으면 편함.
    raw_text: Optional[str] = Field(
        default=None, description="사용자가 붙여넣은 원문 레주메(선택)"
    )

    # Skills 섹션에서 추출한 스킬들 (정규화 도구 적용 대상)
    skills: list[str] = Field(
        default_factory=list,
        description="Skills 섹션에서 추출된 스킬/키워드(정규화 가능)",
    )

    # Experience/Project 항목들
    experience: list[ResumeEntry] = Field(
        default_factory=list,
        description="Experience + Project 섹션 항목들",
    )

    # 학력(현재 점수에는 미포함; 추후 eligibility/필터에 활용 가능)
    education: list[ResumeEducation] = Field(default_factory=list)

    # 정규화 상태(너희 설계에서 NormalizeKeywordsTool이 True로 바꿔서 반환)
    normalized: bool = Field(default=False, description="JD 기준 정규화 적용 여부")
    normalization_notes: list[str] = Field(
        default_factory=list, description="정규화 과정 메모(선택)"
    )
    normalization_map_applied: dict[str, str] = Field(
        default_factory=dict,
        description="적용된 alias/표기 변환 맵 (예: {'cicd':'CI/CD'})",
    )

    # --------- 편의 메서드성 필드: 점수 계산을 쉽게 하기 위한 인덱스(선택) ---------
    # Tool에서 채워도 되고, 안 채워도 됨. (MVP면 tool에서 계산 추천)
    skills_set: list[str] = Field(
        default_factory=list,
        description="skills의 정규화/중복 제거 버전(선택, tool이 채움)",
    )
    expproj_keywords_set: list[str] = Field(
        default_factory=list,
        description="Experience/Project에서 모은 키워드 집합(선택, tool이 채움)",
    )

    # --------- Validators ---------
    @field_validator("skills")
    @classmethod
    def normalize_skills_basic(cls, v: list[str]) -> list[str]:
        cleaned = [norm_text(x) for x in v if isinstance(x, str) and x.strip()]
        return dedupe_case_insensitive(cleaned)

    @field_validator("entries")
    @classmethod
    def normalize_entry_text(cls, v: list[ResumeEntry]) -> list[ResumeEntry]:
        # bullet 텍스트 최소 정리
        for e in v:
            for b in e.bullets:
                b.text = norm_text(b.text)
                if b.keywords:
                    b.keywords = dedupe_case_insensitive(
                        [norm_text(k) for k in b.keywords if k.strip()]
                    )
        return v
