# packages/graph/main.py
"""LangGraph 메인 워크플로우.

StateGraph + MessagesState를 사용한 최소 사이클 구현.
START -> resume_agent -> END
"""

from __future__ import annotations

from typing import Optional

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState

from packages.agents.resume_agent import create_resume_agent
from packages.core.schemas import GapSummary, JDProfile, ProjectOutput, ResumeProfile


class ProjectState(MessagesState):
    resume_text: str
    jd_text: str
    # preferences: Optional[Preferences]

    jd_profile: Optional[JDProfile]
    resume_profile: Optional[ResumeProfile]
    gap_summary: Optional[GapSummary]

    project_output: Optional[ProjectOutput]

    error: Optional[list[str]]
    current_step: Optional[str]


def build_graph():
    """
    Build the main LangGraph workflow.

    Flow: START -> resume_agent -> END

    Returns:
        CompiledGraph: A compiled LangGraph that can be invoked with MessagesState
    """
    # Create the agent
    agent = create_resume_agent()

    # Build the graph
    builder = StateGraph(ProjectState)

    # Add nodes
    builder.add_node("resume_agent", agent)

    # Add edges
    builder.add_edge(START, "resume_agent")
    builder.add_edge("resume_agent", END)

    # Compile and return
    return builder.compile()


# Pre-built graph instance for direct import
graph = build_graph()
