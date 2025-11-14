#!/usr/bin/env python3
"""
REAL TEST: Spawn actual Claude agents in parallel

This tests how many TRUE Claude agents can run simultaneously.
"""

import asyncio
import time
import json


# Test data: regions to discover platforms for
REGIONS_TO_TEST = [
    ("Romania", "Romanian"),
    ("Poland", "Polish"),
    ("Thailand", "Thai"),
    ("Indonesia", "Indonesian"),
    ("Czech Republic", "Czech"),
]


def create_quick_platform_discovery_prompt(country: str, language: str) -> str:
    """Creates a streamlined prompt for quick platform discovery"""
    return f"""
You are a Platform Discovery Agent researching {country}.

QUICK MISSION: Find the TOP 3 platforms locals in {country} use for software reviews/discussions.

Primary language: {language}

## Tasks:

1. Use WebSearch to find 3 key platforms in {country}
2. Search in both {language} and English
3. Focus on: software review sites, tech forums, or business directories

## Output Format:

Return ONLY this JSON (no other text):

```json
{{
  "country": "{country}",
  "platforms": [
    {{"name": "Platform 1", "url": "https://...", "type": "review_site|forum|directory"}},
    {{"name": "Platform 2", "url": "https://...", "type": "review_site|forum|directory"}},
    {{"name": "Platform 3", "url": "https://...", "type": "review_site|forum|directory"}}
  ]
}}
```

Find top 3 platforms quickly!
"""


async def main():
    """
    Test spawning multiple Claude agents in parallel

    We'll test with 1, 2, 3, and 5 agents to see the limits
    """

    print("\n" + "="*100)
    print("REAL TEST: Spawning TRUE Claude Agents in Parallel")
    print("="*100 + "\n")

    print("We'll test different concurrency levels:")
    print("  - 1 agent  (baseline)")
    print("  - 2 agents (parallel)")
    print("  - 3 agents (parallel)")
    print("  - 5 agents (parallel)")
    print()

    # Show what we're about to do
    print("Test regions:")
    for i, (country, language) in enumerate(REGIONS_TO_TEST[:5], 1):
        print(f"  {i}. {country} ({language})")

    print("\n" + "="*100)
    print("Ready to spawn agents!")
    print("="*100)
    print()
    print("NOTE: To actually run this test, Claude will need to use the Task tool")
    print("      to spawn multiple general-purpose agents in parallel.")
    print()
    print("The test would look like:")
    print()
    print("  # Spawn 5 agents in parallel")
    print("  tasks = [")
    print("    Task(subagent_type='general-purpose', prompt=prompt1),")
    print("    Task(subagent_type='general-purpose', prompt=prompt2),")
    print("    Task(subagent_type='general-purpose', prompt=prompt3),")
    print("    Task(subagent_type='general-purpose', prompt=prompt4),")
    print("    Task(subagent_type='general-purpose', prompt=prompt5),")
    print("  ]")
    print("  results = await asyncio.gather(*tasks)")
    print()
    print("="*100)
    print()

    # Show sample prompts
    print("Sample prompts that would be sent:")
    print("-" * 100)
    for i, (country, language) in enumerate(REGIONS_TO_TEST[:2], 1):
        prompt = create_quick_platform_discovery_prompt(country, language)
        print(f"\nAgent {i} - {country}:")
        print(prompt[:400] + "...\n")

    print("="*100)
    print("Ready for Claude to execute the parallel spawn test!")
    print("="*100)


if __name__ == "__main__":
    asyncio.run(main())
