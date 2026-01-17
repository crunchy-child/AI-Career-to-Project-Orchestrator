#!/usr/bin/env python3
"""
Test script for Resume Analysis Agent with JD and Resume parsing.

The agent autonomously decides which tools to use based on the input.

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
    """Run the agent test with both JD and Resume."""
    from packages.graph import build_graph

    # Load sample data
    jd_path = Path(__file__).parent / "data" / "samples" / "jd_1.txt"
    resume_path = Path(__file__).parent / "data" / "samples" / "resume_1.txt"

    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()
    with open(resume_path, "r", encoding="utf-8") as f:
        resume_text = f.read()

    print("=" * 60)
    print("Resume Analysis Agent Test")
    print("=" * 60)
    print("\nThe agent will autonomously decide which tools to use.")
    print("Given: JD text + Resume text")
    print("Expected: Agent parses both using appropriate tools")
    print("=" * 60)

    # Build the graph
    graph = build_graph()
    print("\n✓ Graph built successfully!")

    # Create the user message with both JD and Resume
    user_message = f"""Please analyze the following Job Description and Resume.
Parse both documents and provide a summary of the extracted information.

=== JOB DESCRIPTION ===
{jd_text}

=== RESUME ===
{resume_text}
"""

    print("\n" + "-" * 60)
    print("Invoking agent...")
    print("-" * 60)

    # Invoke the graph
    result = graph.invoke(
        {
            "messages": [("user", user_message)]
        }
    )

    print("\n" + "=" * 60)
    print("Agent Response:")
    print("=" * 60)

    # Print messages
    for msg in result.get("messages", []):
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", str(msg))
        
        # Skip empty content
        if not content:
            continue
            
        print(f"\n[{role.upper()}]")
        
        # For tool calls, show tool name
        if role == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                print(f"  → Calling tool: {tool_call.get('name', 'unknown')}")
        
        # For tool results, show abbreviated content
        if role == "tool":
            tool_name = getattr(msg, "name", "unknown")
            print(f"  ← Tool result from: {tool_name}")
            # Show truncated result
            content_str = str(content)
            if len(content_str) > 500:
                print(f"  {content_str[:500]}...")
            else:
                print(f"  {content_str}")
        elif content:
            # Show full content for non-tool messages
            print(content[:3000] if len(str(content)) > 3000 else content)

    print("\n" + "=" * 60)
    print("✓ Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
