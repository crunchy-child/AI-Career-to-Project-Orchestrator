# packages/core/schemas/project.py
from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .utils import norm_text
from .keyword_base import BaseKeyword


class DayPlan(BaseModel):
    """D1~D7 하루 단위 계획."""
    model_config = ConfigDict(extra="forbid")

    day: int = Field(..., ge=1, le=7)
    goals: list[str] = Field(default_factory=list, description="그 날의 목표")
    tasks: list[str] = Field(default_factory=list, description="구체 태스크")
    deliverables: list[str] = Field(default_factory=list, description="산출물(코드/문서/데모 등)")


class ArchitectureSpec(BaseModel):
    """프로젝트 구조 설명(텍스트 + optional Mermaid)."""
    model_config = ConfigDict(extra="forbid")

    summary: Optional[str] = Field(default=None, description="아키텍처 한줄 요약")
    components: list[str] = Field(default_factory=list, description="구성요소 나열(서비스/DB/에이전트/툴 등)")
    data_flow: Optional[str] = Field(default=None, description="데이터 플로우 텍스트 설명")
    mermaid: Optional[str] = Field(default=None, description="Mermaid 다이어그램(선택)")


class ProjectIdea(BaseModel):
    """프로젝트 아이디어(1개)."""
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    one_liner: str = Field(..., min_length=1, description="한 줄 설명")
    reasoning: str = Field(..., min_length=1, description="왜 이 프로젝트가 missing keyword를 증명하는지")

    # keyword coverage
    covers_keywords: list[BaseKeyword] = Field(default_factory=list, description="이 프로젝트로 증명 가능한 키워드")

    # constraints & stack
    constraints: list[str] = Field(default_factory=list, description="예: 비용 0, 1주일, 팀 2명")
    tech_stack: list[str] = Field(default_factory=list, description="예: FastAPI, LangGraph, Next.js 등")


class ProjectPlan(BaseModel):
    """아이디어 + 구조 + 7일 계획까지 포함한 완성된 프로젝트 1안."""
    model_config = ConfigDict(extra="forbid")

    idea: ProjectIdea
    architecture: ArchitectureSpec = Field(default_factory=ArchitectureSpec)
    weekly_plan: list[DayPlan] = Field(default_factory=list, max_length=7, description="D1~D7 계획")

    downside: list[str] = Field(default_factory=list)
    workaround: list[str] = Field(default_factory=list)


class ProjectOutput(BaseModel):
    """
    ProjectPlannerAgent 최종 산출물.
    - 프로젝트는 항상 2안 고정
    """
    model_config = ConfigDict(extra="forbid")

    project_ideas: list[ProjectPlan] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="항상 정확히 2개의 프로젝트 안을 반환",
    )

    notes: Optional[str] = Field(default=None, description="두 안의 차이/추천 기준 등 간단 메모")

    @field_validator("project_ideas")
    @classmethod
    def ensure_two_distinct_projects(cls, v: list[ProjectPlan]) -> list[ProjectPlan]:
        # 제목이 완전히 같은 두 안이 들어오면 퀄리티가 낮으니 방지(완벽 검증은 아님)
        if len(v) == 2:
            t0 = norm_text(v[0].idea.title).lower()
            t1 = norm_text(v[1].idea.title).lower()
            if t0 == t1:
                raise ValueError("project_ideas must contain two distinct project titles")
        return v
