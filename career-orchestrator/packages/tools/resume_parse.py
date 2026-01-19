# packages/tools/resume_parse.py
"""Resume 파싱 Tool - LLM을 사용하여 Resume 텍스트에서 키워드 추출."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from packages.core.schemas import ResumeProfile

SYSTEM_PROMPT = """You are a Resume parser that extracts technical keywords from resumes.

## ⚠️ CRITICAL: DO NOT MISS ANY TECHNICAL KEYWORDS

**Missing a keyword is MUCH WORSE than extracting too many.**
- Be AGGRESSIVE and INCLUSIVE
- When in doubt, INCLUDE the keyword
- We can filter later, but we CANNOT recover missed keywords

## MANDATORY: Extract from ALL Sections

### SKILLS/TECHNICAL SKILLS Section (MOST IMPORTANT!)
**Extract EVERY SINGLE ITEM listed, including:**
- Languages line: If "Python, Java, C++, SQL" → extract ALL FOUR separately
- Libraries line: If "Pandas, NumPy, Scikit-learn" → extract ALL THREE separately
- Tools line: If "Git, Docker, VS Code" → extract ALL THREE separately
- Frameworks line: Extract EVERY item listed

### PROJECTS Section
- Extract ALL technologies, tools, frameworks, libraries mentioned
- Extract specific tools and platforms (e.g., "Google ADK", "Otter-Grader")

### EXPERIENCE Section
- Extract ALL technical terms from job descriptions

## Output Format

For each keyword:
- **keyword_text**: lowercase (e.g., "python", "c++", "scikit-learn")
- **evidence**: The sentence/line where it appears

### Example

Skills: "Languages: Python, Java, C++, SQL"
→ Extract ALL FOUR:
  - {"keyword_text": "python", "evidence": "Languages: Python, Java, C++, SQL"}
  - {"keyword_text": "java", "evidence": "Languages: Python, Java, C++, SQL"}
  - {"keyword_text": "c++", "evidence": "Languages: Python, Java, C++, SQL"}
  - {"keyword_text": "sql", "evidence": "Languages: Python, Java, C++, SQL"}

## What to Extract

✅ INCLUDE:
- Programming languages (python, java, c++, sql, typescript, go, rust)
- Frameworks & libraries (react, fastapi, django, langchain, langgraph, pandas, numpy, scikit-learn)
- ML/AI terms (linear regression, random forest, xgboost, neural network, shap)
- Tools & IDEs (git, docker, kubernetes, vs code, intellij, jupyter, jupyterhub)
- Cloud platforms (aws, gcp, azure, github)
- Databases (postgresql, mongodb, redis, elasticsearch)
- Methodologies (ci/cd, agile, microservices, tdd)
- Specific tools (otter-grader, google adk, json-rpc)
- Data/ML concepts (feature engineering, hyperparameter tuning, eda, cross-validation)

## ⛔ EXCLUDE (NOT technical keywords)

❌ SOFT SKILLS: leadership, collaboration, teamwork, communication, problem solving
❌ OPERATING SYSTEMS: windows, macos, linux
❌ GENERIC TERMS: responsible for, worked on, bachelor's, master's, GPA
❌ COMPANY/JOB TITLES

## Output

Only populate `keywords` field. Leave `category` empty (it will be set automatically).

**IMPORTANT: Do NOT skip any item in the Skills section lists!**"""


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
