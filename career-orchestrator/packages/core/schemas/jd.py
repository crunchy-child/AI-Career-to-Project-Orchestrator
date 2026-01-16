# packages/core/schemas/jd.py
from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .utils import norm_text, dedupe_case_insensitive


JDCategory = Literal["required", "preferred", "responsibility", "other"]


class JDKeyword(BaseModel):
    """
    JD에서 추출한 키워드 1개.
    category는 required/preferred 중심으로 쓰고, 나머지는 optional.
    """

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ..., min_length=1, description="키워드 원문 표기(예: 'CI/CD', 'K8s')"
    )
    category: JDCategory = Field(default="other")
    # JD 내 근거 문장(짧게). missing validation/설명에 유용(선택)
    evidence: Optional[str] = Field(
        default=None, description="JD에서 해당 키워드가 등장한 근거 문장(선택)"
    )
    # 중요도(선택): 나중에 required 내부에서도 가중치 세분화 가능
    importance: Optional[int] = Field(
        default=None, ge=1, le=5, description="1(낮음)~5(높음), 선택"
    )


class JDSection(BaseModel):
    """
    JD의 섹션(Responsibilities / Requirements / Preferred 등)을 구조화.
    MVP에서는 섹션 텍스트와 키워드만 있어도 충분.
    """

    model_config = ConfigDict(extra="forbid")

    section_type: JDCategory = Field(default="other")
    text: str = Field(..., min_length=1, description="섹션 본문 텍스트")
    keywords: list[str] = Field(
        default_factory=list, description="이 섹션에서 추출된 키워드(선택)"
    )


class JDProfile(BaseModel):
    """
    JDParserTool 출력.
    점수 계산을 위해 required/preferred 키워드를 명확히 저장한다.
    """

    model_config = ConfigDict(extra="forbid")

    raw_text: Optional[str] = Field(
        default=None, description="사용자가 붙여넣은 원문 JD(선택)"
    )
    role_title: Optional[str] = Field(
        default=None, description="직무 타이틀(추출 가능하면)"
    )
    company: Optional[str] = Field(default=None, description="회사명(추출 가능하면)")

    # 섹션 구조(선택)
    sections: list[JDSection] = Field(default_factory=list)

    # 핵심: 카테고리별 키워드 구조화
    keywords: list[JDKeyword] = Field(
        default_factory=list,
        description="JD 전체에서 추출한 키워드 목록(카테고리 포함)",
    )

    # 정규화 기준(선택): alias → canonical
    # 예: {'cicd': 'CI/CD', 'k8s': 'Kubernetes', 'postgres': 'PostgreSQL'}
    canonical_map: dict[str, str] = Field(
        default_factory=dict,
        description="JD 기준 표준 용어 맵(Resume 정규화에 사용)",
    )

    # --------- 편의 필드: tool이 채워도 되고, 안 채워도 됨 ---------
    required_keywords_set: list[str] = Field(
        default_factory=list,
        description="required 키워드 dedupe/정규화 버전(선택, tool이 채움)",
    )
    preferred_keywords_set: list[str] = Field(
        default_factory=list,
        description="preferred 키워드 dedupe/정규화 버전(선택, tool이 채움)",
    )

    # --------- Validators ---------
    @field_validator("sections")
    @classmethod
    def normalize_sections(cls, v: list[JDSection]) -> list[JDSection]:
        for s in v:
            s.text = norm_text(s.text)
            if s.keywords:
                s.keywords = dedupe_case_insensitive(
                    [norm_text(k) for k in s.keywords if k.strip()]
                )
        return v

    @field_validator("keywords")
    @classmethod
    def normalize_keywords(cls, v: list[JDKeyword]) -> list[JDKeyword]:
        for k in v:
            k.text = norm_text(k.text)
            if k.evidence:
                k.evidence = norm_text(k.evidence)
        return v
