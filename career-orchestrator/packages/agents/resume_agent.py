# packages/agents/resume_agent.py
"""
Resume Analysis Agent.

JD/Resume 파싱, 정규화, 갭 분석, 점수 계산.
Uses create_react_agent with jd_parse_tool.
"""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from packages.tools.jd_parse import jd_parse_tool
from packages.tools.resume_parse import resume_parse_tool

AGENT_PROMPT = """You are a Resume Analysis Agent.
Your job is to analyze job descriptions and resumes to help candidates understand their fit.

You have access to the following tools:

1. jd_parse_tool: Use this to parse a Job Description (JD) and extract:
   - Required and preferred skills/qualifications
   - Key responsibilities
   - Company and role information

2. resume_parse_tool: Use this to parse a Resume and extract:
   - Technical skills from the Skills section
   - Skills demonstrated in Experience/Project sections

When given both a JD and a Resume:
1. First, parse the JD using jd_parse_tool
2. Then, parse the Resume using resume_parse_tool
3. Provide a summary of both parsed results

Always use the appropriate tool for each document type."""

TOOLS = [jd_parse_tool, resume_parse_tool]


def create_resume_agent():
    """
    Create a Resume Analysis Agent using create_react_agent.

    Returns:
        CompiledGraph: A LangGraph agent that can parse JDs and analyze resumes
    """
    llm = init_chat_model("gpt-4o-mini", temperature=0.1)

    agent = create_react_agent(llm, tools=TOOLS, prompt=AGENT_PROMPT)

    return agent
