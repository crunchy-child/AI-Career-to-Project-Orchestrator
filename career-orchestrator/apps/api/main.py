# apps/api/main.py
"""
FastAPI application for Career Orchestrator.

Endpoints:
- POST /run (or /analyze): Main entry point for JD-Resume analysis
- GET /health: Health check
"""
from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Import schemas and tools
from packages.core.schemas import GapSummary, JDProfile, ResumeProfile, ProjectOutput
from packages.tools import (
    jd_parse_tool,
    resume_parse_tool,
    normalize_keywords_tool,
    gap_compute_tool,
    score_tool,
    LLMClient,
    get_default_llm_client,
)

app = FastAPI(
    title="Career Orchestrator API",
    description="JD matching score (0-100) + 2 portfolio project plans",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Preferences(BaseModel):
    """User preferences for project planning."""

    stack_pref: Optional[list[str]] = Field(
        default=None, description="Preferred tech stack"
    )
    constraints: Optional[list[str]] = Field(
        default=None, description="Constraints (e.g., '1 week', 'solo')"
    )
    role: Optional[str] = Field(default=None, description="Target role")


class AnalyzeRequest(BaseModel):
    """Request body for /run endpoint."""

    resume_text: str = Field(..., min_length=10, description="Resume text (paste)")
    jd_text: str = Field(..., min_length=10, description="Job description text (paste)")
    preferences: Optional[Preferences] = Field(
        default=None, description="Optional preferences"
    )


class AnalyzeResponse(BaseModel):
    """Response body for /run endpoint."""

    gap_summary: GapSummary
    # project_output: ProjectOutput  # TODO: Add after implementing Project Planner Agent


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/run", response_model=AnalyzeResponse)
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Main entry point for JD-Resume analysis.

    1. Parse JD and Resume
    2. Normalize keywords
    3. Compute gap and score
    4. (TODO) Generate project plans

    Returns:
        AnalyzeResponse with GapSummary (and ProjectOutput when implemented)
    """
    try:
        # Get LLM client
        llm_client = get_default_llm_client()

        # Step 1: Parse JD
        jd_profile = jd_parse_tool(request.jd_text, llm_client=llm_client)

        # Step 2: Parse Resume
        resume_profile = resume_parse_tool(request.resume_text, llm_client=llm_client)

        # Step 3: Normalize keywords
        normalized_resume = normalize_keywords_tool(
            resume_profile, jd_profile, llm_client=llm_client
        )

        # Step 4: Compute gap
        gap_summary = gap_compute_tool(jd_profile, normalized_resume)

        # Step 5: Calculate score
        gap_summary = score_tool(gap_summary)

        # TODO: Step 6-8: Project planning (after implementing Project Planner Agent)
        # project_output = ...

        return AnalyzeResponse(
            gap_summary=gap_summary,
            # project_output=project_output,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
