# packages/tools/jd_parse.py
"""JD 파싱 Tool - LLM을 사용하여 JD 텍스트에서 키워드 추출."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from packages.core.schemas import JDProfile

SYSTEM_PROMPT = """You are a Job Description (JD) parser that extracts technical keywords AGGRESSIVELY.

## ⚠️ CRITICAL: Extract ALL Technical Keywords

**Be AGGRESSIVE and INCLUSIVE when extracting technical keywords.**
- Extract EVERY technical term, tool, framework, language, platform mentioned
- When in doubt, INCLUDE the keyword
- Extract keywords from ALL sections: Requirements, Preferred Qualifications, Responsibilities, Company Tech Stack, etc.
- We can filter later, but we CANNOT recover missed keywords

## Keyword Categories

Categorize each keyword as:
- **"required"**: Must-have skills/qualifications explicitly stated as required, mandatory, essential
- **"preferred"**: Nice-to-have skills stated as preferred, bonus, plus, nice-to-have
- **"responsibility"**: Technologies/tools mentioned in job responsibilities or duties
- **"context"**: Other relevant technical keywords from company tech stack, team description, etc.

## What to Extract (TECHNICAL keywords only!)

✅ INCLUDE ALL:
- Programming languages (python, java, c++, sql, typescript, go, rust, javascript)
- Frameworks & libraries (react, fastapi, django, flask, langchain, langgraph, pandas, numpy)
- ML/AI models & algorithms (linear regression, random forest, xgboost, neural network, transformers)
- Tools & IDEs (git, docker, kubernetes, jenkins, vs code, intellij, jupyter)
- Cloud platforms (aws, gcp, azure, github, databricks, snowflake)
- Databases (postgresql, mongodb, redis, elasticsearch, mysql)
- Methodologies (ci/cd, agile, scrum, microservices, tdd, devops)
- Protocols & standards (rest, graphql, json-rpc, http, https, tcp/ip)
- Specific technologies mentioned (kafka, spark, hadoop, terraform, ansible)

## ⛔ STRICTLY EXCLUDE (DO NOT EXTRACT!)

**NEVER extract these - they are NOT technical keywords:**

❌ SOFT SKILLS (NEVER extract):
- leadership, collaboration, teamwork, communication
- problem solving, detail-oriented, self-motivated
- time management, interpersonal skills, work ethic

❌ EDUCATION/QUALIFICATIONS (NEVER extract):
- PhD, Master's, Bachelor's, degree, diploma
- CS degree, Computer Science degree, Engineering degree
- GPA, graduation, university, college

❌ WORK AUTHORIZATION (NEVER extract):
- work authorization, visa, green card, H1B, sponsorship
- must be authorized to work, eligible to work

❌ GENERIC TERMS:
- responsible for, worked on, managed, developed
- years of experience (extract the number as context, not as keyword)
- company names, job titles (unless they're technical roles like "ML Engineer")

❌ VAGUE CONCEPTS:
- vague concepts are too broad - extract specific tools instead
- Example: machine learning, data science, web development

❌ OEPRATING SYSTEMS:
- windows, macos, linux, etc.

## Output Format

For each keyword:
- **keyword_text**: lowercase, normalized (e.g., "python", "c++", "scikit-learn")
- **category**: required/preferred/responsibility/context
- **evidence**: The exact sentence/phrase from JD where it appears
- **importance**: (Optional, 1-5 scale) For required/preferred keywords only

### Example

JD: "Required: 3+ years Python, FastAPI. Preferred: Docker, Kubernetes. Responsibilities: Build ML models using XGBoost."

Extract:
- {"keyword_text": "python", "category": "required", "evidence": "Required: 3+ years Python", "importance": 5}
- {"keyword_text": "fastapi", "category": "required", "evidence": "Required: 3+ years Python, FastAPI", "importance": 5}
- {"keyword_text": "docker", "category": "preferred", "evidence": "Preferred: Docker, Kubernetes", "importance": 3}
- {"keyword_text": "kubernetes", "category": "preferred", "evidence": "Preferred: Docker, Kubernetes", "importance": 3}
- {"keyword_text": "xgboost", "category": "responsibility", "evidence": "Build ML models using XGBoost"}

## Final Reminder

**EXTRACT ALL TECHNICAL KEYWORDS AGGRESSIVELY. EXCLUDE SOFT SKILLS, EDUCATION, AND WORK AUTHORIZATION.**"""


@tool
def jd_parse_tool(jd_text: dict) -> dict:
    """
    Parse a Job Description dictionary and extract structured information.

    Args:
        jd_text: The dictionary containing job description raw texts by section, in the shape of dictionary.

    Returns:
        JDProfile as a dictionary containing role_title, company, and extracted keywords
    """
    llm = init_chat_model("gpt-4o-mini", temperature=0.0)
    structured_llm = llm.with_structured_output(JDProfile)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Parse this Job Description:\n\n{jd_text}"},
    ]

    result: JDProfile = structured_llm.invoke(messages)
    # Store raw text for reference
    result.raw_text = jd_text

    return result.model_dump()
