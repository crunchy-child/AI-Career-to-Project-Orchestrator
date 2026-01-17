#!/usr/bin/env python3
"""
Test script for the minimal LangGraph cycle.

Usage:
    cd career-orchestrator
    python test_graph.py

Make sure to set OPENAI_API_KEY in your environment or .env file.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify API key is set
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError(
        "OPENAI_API_KEY is not set. Please set it in .env or environment."
    )


def main():
    """Run the minimal LangGraph cycle test."""
    # Import here to avoid import errors before env is loaded
    from packages.graph import build_graph

    # Load sample JD
    jd_path = Path(__file__).parent / "data" / "samples" / "jd_1.txt"
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    # Truncate JD for demo (first 500 chars for faster testing)
    jd_snippet = jd_text[:1500] + "..."

    print("=" * 60)
    print("Building LangGraph workflow...")
    print("=" * 60)

    # Build the graph
    graph = build_graph()

    print("\nGraph built successfully!")
    print("\n" + "=" * 60)
    print("Invoking graph with sample JD...")
    print("=" * 60)

    # Invoke the graph
    result = graph.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Please parse this Job Description and extract the key requirements:\n\n{jd_snippet}",
                )
            ]
        }
    )

    print("\n" + "=" * 60)
    print("Result:")
    print("=" * 60)

    # Print messages
    for msg in result.get("messages", []):
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", str(msg))
        print(f"\n[{role}]")
        if content:
            print(content[:2000] if len(str(content)) > 2000 else content)

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

    # print(result.get("messages"))


if __name__ == "__main__":
    main()
