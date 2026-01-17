# packages/tools/jd_parse.py
"""JD 파싱 Tool - LLM을 사용하여 JD 텍스트에서 키워드 추출."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from packages.core.schemas import JDProfile

SYSTEM_PROMPT = """You are a Job Description (JD) parser.
Extract structured information from the given JD text.

For keywords, categorize them as:
- "required": Must-have skills/qualifications explicitly stated as required
- "preferred": Nice-to-have skills/qualifications stated as preferred/bonus
- "responsibility": Key job responsibilities or duties
- "other": Other relevant keywords

For each keyword, also provide:
- keyword_text: The skill/technology/qualification name (lowercase, normalized)
- category: One of required/preferred/responsibility/other
- evidence: The exact phrase or sentence from the JD where this keyword appears
- importance: 1-5 scale (5 being most important) for required/preferred keywords

Focus on technical skills, tools, frameworks, languages, and key qualifications.
Do NOT include:
- Soft skills or generic requirements
- Education/degree requirements (e.g., PhD, Master's, Bachelor's, CS degree)
- Work authorization or visa requirements"""


@tool
def jd_parse_tool(jd_text: str) -> dict:
    """
    Parse a Job Description text and extract structured information.

    Args:
        jd_text: The raw job description text to parse

    Returns:
        JDProfile as a dictionary containing role_title, company, and extracted keywords
    """
    llm = init_chat_model("gpt-4o")
    structured_llm = llm.with_structured_output(JDProfile)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Parse this Job Description:\n\n{jd_text}"},
    ]

    result: JDProfile = structured_llm.invoke(messages)
    # Store raw text for reference
    result.raw_text = jd_text

    return result.model_dump()
