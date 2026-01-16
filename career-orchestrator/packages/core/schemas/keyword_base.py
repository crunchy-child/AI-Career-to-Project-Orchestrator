from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseKeyword(BaseModel):
    """공통 키워드 스키마."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ..., min_length=1, description="키워드 원문 표기(예: 'CI/CD', 'K8s')"
    )
    evidence: Optional[str] = Field(
        default=None, description="키워드가 등장한 근거 문장(선택)"
    )
