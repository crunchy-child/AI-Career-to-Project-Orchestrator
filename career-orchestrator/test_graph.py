#!/usr/bin/env python3
"""
Test script for Resume Analysis Agent with JD and Resume parsing.

The agent autonomously decides which tools to use based on the input.

Usage:
    cd career-orchestrator
    python test_graph.py              # Run full agent test
    python test_graph.py --resume     # Test resume_parse_tool only
    python test_graph.py --jd         # Test jd_parse_tool only

Make sure to set OPENAI_API_KEY in your environment or .env file.
"""

from __future__ import annotations

import json
import os
import sys
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
    result = graph.invoke({"messages": [("user", user_message)]})

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


def test_resume_parse():
    """Test resume_parse_tool directly without the full graph."""
    from packages.tools.resume_parse import resume_parse_tool

    # Load sample resume
    resume_path = Path(__file__).parent / "data" / "samples" / "resume_1.txt"
    with open(resume_path, "r", encoding="utf-8") as f:
        resume_text = f.read()

    print("=" * 60)
    print("Resume Parse Tool Test")
    print("=" * 60)
    print(f"\nLoaded resume from: {resume_path.name}")
    print(f"Resume length: {len(resume_text)} characters")
    print("=" * 60)

    print("\nParsing resume...")
    result = resume_parse_tool.invoke({"resume_text": resume_text})

    print("\n" + "=" * 60)
    print("Parsed ResumeProfile:")
    print("=" * 60)

    # Pretty print the result
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Summary
    keywords = result.get("keywords", [])
    skills_count = sum(1 for k in keywords if k.get("category") == "skills")
    entries_count = sum(1 for k in keywords if k.get("category") == "entries")

    print("\n" + "-" * 60)
    print("Summary:")
    print(f"  Total keywords: {len(keywords)}")
    print(f"  Skills section: {skills_count}")
    print(f"  Entries (Experience/Project): {entries_count}")
    print("-" * 60)

    print("\n✓ Resume parse test completed!")


def test_jd_parse():
    """Test jd_parse_tool directly without the full graph."""
    from packages.tools.jd_parse import jd_parse_tool

    # Load sample JD
    jd_path = Path(__file__).parent / "data" / "samples" / "jd_1.txt"
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    print("=" * 60)
    print("JD Parse Tool Test")
    print("=" * 60)
    print(f"\nLoaded JD from: {jd_path.name}")
    print(f"JD length: {len(jd_text)} characters")
    print("=" * 60)

    print("\nParsing JD...")
    result = jd_parse_tool.invoke({"jd_text": jd_text})

    print("\n" + "=" * 60)
    print("Parsed JDProfile:")
    print("=" * 60)

    # Pretty print the result
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Summary
    keywords = result.get("keywords", [])
    required_count = sum(1 for k in keywords if k.get("category") == "required")
    preferred_count = sum(1 for k in keywords if k.get("category") == "preferred")

    print("\n" + "-" * 60)
    print("Summary:")
    print(f"  Role: {result.get('role_title', 'N/A')}")
    print(f"  Company: {result.get('company', 'N/A')}")
    print(f"  Total keywords: {len(keywords)}")
    print(f"  Required: {required_count}")
    print(f"  Preferred: {preferred_count}")
    print("-" * 60)

    print("\n✓ JD parse test completed!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("--resume", "-r"):
            test_resume_parse()
        elif arg in ("--jd", "-j"):
            test_jd_parse()
        else:
            print(f"Unknown argument: {arg}")
            print("Usage:")
            print("  python test_graph.py              # Full agent test")
            print("  python test_graph.py --resume     # Resume parse only")
            print("  python test_graph.py --jd         # JD parse only")
            sys.exit(1)
    else:
        main()
