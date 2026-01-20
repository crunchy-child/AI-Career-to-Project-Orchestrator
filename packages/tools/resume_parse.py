# packages/tools/resume_parse.py
"""Resume 파싱 Tool - LLM을 사용하여 Resume 텍스트에서 키워드 추출."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from packages.core.schemas import ResumeProfile

SYSTEM_PROMPT = """You are a Resume parser that extracts **technical keywords** from resumes.

## 🎯 GOAL: Extract ONLY concrete technical keywords

Be **CONSERVATIVE** - only extract keywords that are clearly technical skills.
The user will review missing keywords later and can remove ones they already know.

## What to Extract

✅ **INCLUDE** (Technical Keywords Only):
- Programming languages: python, java, c++, javascript, typescript, go, rust, sql
- Frameworks: react, fastapi, django, flask, spring, langchain, langgraph
- Libraries: pandas, numpy, scikit-learn, tensorflow, pytorch
- Tools: git, docker, kubernetes, jenkins, terraform
- Cloud: aws, gcp, azure, s3, ec2, lambda
- Databases: postgresql, mongodb, redis, mysql, elasticsearch
- Specific technologies: kafka, spark, airflow, grafana, prometheus

## ⛔ EXCLUDE (Do NOT extract)

❌ Soft skills: leadership, collaboration, teamwork, communication
❌ Generic terms: responsible for, worked on, developed, implemented
❌ Education: bachelor's, master's, PhD, GPA, university names
❌ Job titles: software engineer, data scientist, manager
❌ Company names
❌ Operating systems: windows, macos, linux (too generic)
❌ Vague concepts: machine learning, data science, web development (too broad - extract specific tools instead)

## Output Format

For each keyword:
- **keyword_text**: lowercase, exact technology name (e.g., "python", "react", "postgresql")
- **evidence**: The exact sentence or line from the resume where it appears

### Example

Input: "Developed REST APIs using FastAPI and PostgreSQL"
Output:
- {"keyword_text": "fastapi", "evidence": "Developed REST APIs using FastAPI and PostgreSQL"}
- {"keyword_text": "postgresql", "evidence": "Developed REST APIs using FastAPI and PostgreSQL"}

Note: "REST APIs" is excluded (concept, not a tool). "Developed" is excluded (verb).

## Sections to Check

1. **Skills/Technical Skills** - Extract each listed technology
2. **Experience** - Extract specific tools/frameworks mentioned
3. **Projects** - Extract technologies used

## Output

Populate `keywords` field with extracted technical keywords only."""


@tool
def resume_parse_tool(resume_text: str) -> dict:
    """
    Parse a Resume text and extract technical keywords.

    Args:
        resume_text: The raw resume text to parse

    Returns:
        ResumeProfile as a dictionary containing extracted technical keywords
    """
    llm = init_chat_model("gpt-4o-mini", temperature=0.0)
    structured_llm = llm.with_structured_output(ResumeProfile)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Parse this Resume:\n\n{resume_text}"},
    ]

    result: ResumeProfile = structured_llm.invoke(messages)
    # Store raw text for reference
    result.raw_text = resume_text

    return result.model_dump()
