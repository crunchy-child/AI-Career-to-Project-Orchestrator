# apps/api/main.py
"""
FastAPI application for Career Orchestrator.

Endpoints:
- POST /analyze: Main entry point for JD-Resume analysis
- GET /health: Health check
"""
from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Import tools
from packages.tools.jd_parse import jd_parse_tool
from packages.tools.resume_parse import resume_parse_tool

app = FastAPI(
    title="Career Orchestrator API",
    description="JD matching score (0-100) + portfolio project plans",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response schemas
class JDInputItem(BaseModel):
    """Individual JD input with category."""

    category: Literal["required", "preferred", "responsibility", "context"] = Field(
        ..., description="JD category"
    )
    text: str = Field(..., min_length=1, description="JD section text")


class AnalyzeRequest(BaseModel):
    """Request body for /analyze endpoint."""

    resume_text: str = Field(..., min_length=10, description="Resume text (paste)")
    jd_inputs: list[JDInputItem] = Field(
        ..., min_length=1, description="List of JD sections with categories"
    )


class KeywordInfo(BaseModel):
    """Keyword information."""

    keyword_text: str
    category: str
    evidence: str | None = None
    importance: int | None = None


class GapSummaryResponse(BaseModel):
    """Gap summary response."""

    match_score: float = Field(default=0.0, description="Match score (0-100)")
    keyword_matches: list[dict] = Field(default_factory=list)
    missing_keywords: list[KeywordInfo] = Field(default_factory=list)
    validated_missing_keywords: list[KeywordInfo] = Field(default_factory=list)
    notes: str = Field(default="")


class AnalyzeResponse(BaseModel):
    """Response body for /analyze endpoint."""

    gap_summary: GapSummaryResponse


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Main entry point for JD-Resume analysis.

    1. Parse Resume to extract keywords
    2. Parse JD sections to extract keywords
    3. Compute gap and score (simplified for now)

    Returns:
        AnalyzeResponse with GapSummary
    """
    try:
        # Step 1: Parse Resume
        resume_result = resume_parse_tool.invoke({"resume_text": request.resume_text})
        resume_keywords = set(
            kw.get("keyword_text", "").lower()
            for kw in resume_result.get("keywords", [])
        )

        # Step 2: Combine and parse JD sections
        jd_keywords_by_category: dict[str, list[dict]] = {
            "required": [],
            "preferred": [],
            "responsibility": [],
            "context": [],
        }

        for jd_input in request.jd_inputs:
            jd_result = jd_parse_tool.invoke({"jd_text": jd_input.text})
            for kw in jd_result.get("keywords", []):
                # Override category with user-specified category
                kw_copy = dict(kw)
                kw_copy["category"] = jd_input.category
                jd_keywords_by_category[jd_input.category].append(kw_copy)

        # Step 3: Compute gap (simplified)
        all_jd_keywords = []
        missing_keywords = []

        for category, keywords in jd_keywords_by_category.items():
            for kw in keywords:
                keyword_text = kw.get("keyword_text", "").lower()
                all_jd_keywords.append(kw)
                if keyword_text and keyword_text not in resume_keywords:
                    missing_keywords.append(
                        KeywordInfo(
                            keyword_text=keyword_text,
                            category=category,
                            evidence=kw.get("evidence"),
                            importance=kw.get("importance"),
                        )
                    )

        # Step 4: Calculate score (simplified)
        total_required = len(jd_keywords_by_category["required"])
        total_preferred = len(jd_keywords_by_category["preferred"])

        matched_required = sum(
            1
            for kw in jd_keywords_by_category["required"]
            if kw.get("keyword_text", "").lower() in resume_keywords
        )
        matched_preferred = sum(
            1
            for kw in jd_keywords_by_category["preferred"]
            if kw.get("keyword_text", "").lower() in resume_keywords
        )

        # Weighted score calculation
        required_weight = 0.7
        preferred_weight = 0.3

        required_score = (
            (matched_required / total_required * required_weight)
            if total_required > 0
            else required_weight
        )
        preferred_score = (
            (matched_preferred / total_preferred * preferred_weight)
            if total_preferred > 0
            else preferred_weight
        )

        match_score = round((required_score + preferred_score) * 100, 1)

        # Build response
        gap_summary = GapSummaryResponse(
            match_score=match_score,
            keyword_matches=[],  # Simplified for now
            missing_keywords=missing_keywords,
            validated_missing_keywords=missing_keywords,  # Simplified for now
            notes=f"Found {len(resume_keywords)} resume keywords. Missing {len(missing_keywords)} JD keywords.",
        )

        return AnalyzeResponse(gap_summary=gap_summary)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
