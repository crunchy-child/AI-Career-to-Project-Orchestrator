# packages/tools/resume_parse.py
"""Resume 파싱 Tool - LLM을 사용하여 Resume 텍스트에서 키워드 추출."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from packages.core.schemas import ResumeProfile

SYSTEM_PROMPT = """You are a Resume parser.
Extract technical keywords from the given resume text. ONLY update the keywords field.

For each keyword, provide:
- keyword_text: The skill/technology name (lowercase, normalized)
- evidence: The exact phrase or sentence from the resume where this keyword appears

Focus on extracting:
- Programming languages (python, java, typescript, etc.)
- Frameworks & libraries (react, django, spring, langgraph, fastapi, etc.)
- Tools & platforms (docker, kubernetes, aws, terraform, github, etc.)
- Databases (postgresql, mongodb, redis, etc.)
- Methodologies & concepts (ci/cd, agile, tdd, machine learning, etc.)

Do NOT include:
- Soft skills (communication, leadership, teamwork)
- Generic terms (problem-solving, detail-oriented)
- Education/degree information
- Company names or job titles"""


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
