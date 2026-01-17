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

AGENT_PROMPT = """You are a Resume Analysis Agent.
Your job is to analyze job descriptions and resumes to help candidates understand their fit.

When given a job description (JD), use the jd_parse_tool to extract structured information including:
- Required and preferred skills/qualifications
- Key responsibilities
- Company and role information

Provide clear, actionable insights based on the parsed information."""

TOOLS = [jd_parse_tool]


def create_resume_agent():
    """
    Create a Resume Analysis Agent using create_react_agent.

    Returns:
        CompiledGraph: A LangGraph agent that can parse JDs and analyze resumes
    """
    llm = init_chat_model("gpt-4o", temperature=0.1)

    agent = create_react_agent(llm, tools=TOOLS, prompt=AGENT_PROMPT)

    return agent
