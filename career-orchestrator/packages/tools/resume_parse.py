# packages/tools/resume_parse.py
"""Resume 파싱 Tool - LLM을 사용하여 Resume 텍스트에서 키워드 추출."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from packages.core.schemas import ResumeProfile

SYSTEM_PROMPT = """You are a Resume parser.
Extract structured information from the given resume text and ONLY update keywords Field.

For keywords, categorize them as:
- "skills": Technical skills listed in Skills/Technologies section
- "entries": Skills demonstrated in Experience/Project sections (with actual usage evidence)

For each keyword, provide:
- keyword_text: The skill/technology name (lowercase, normalized)
- category: One of "skills" or "entries"
- evidence: The exact phrase or sentence from the resume where this keyword appears

IMPORTANT distinctions:
- "skills" category: Keywords that appear in a Skills section or list (no project/work context)
- "entries" category: Keywords that appear in Experience/Project bullets with actual usage evidence

IMPORTANT notes:
- Do NOT fill in any Fields other than `keywords`

Focus on:
- Programming languages (python, java, typescript, etc.)
- Frameworks & libraries (react, django, spring, etc.)
- Tools & platforms (docker, kubernetes, aws, terraform, etc.)
- Databases (postgresql, mongodb, redis, etc.)
- Methodologies (ci/cd, agile, tdd, etc.)

Do NOT include:
- Soft skills (communication, leadership, teamwork)
- Generic terms (problem-solving, detail-oriented)
- Education/degree information"""


@tool
def resume_parse_tool(resume_text: str) -> dict:
    """
    Parse a Resume text and extract structured information.

    Args:
        resume_text: The raw resume text to parse

    Returns:
        ResumeProfile as a dictionary containing extracted keywords categorized by skills/entries
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
