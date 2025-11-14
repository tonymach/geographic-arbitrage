#!/usr/bin/env python3
"""
Test: How many Claude agents can we run simultaneously?

This tests parallel agent spawning with different concurrency levels.
"""

import asyncio
import time
from datetime import datetime


def create_platform_discovery_prompt(region: str, country: str, language: str) -> str:
    """Creates prompt for Claude platform discovery agent"""
    return f"""
You are a Platform Discovery Agent researching {country}.

Your mission: Quickly discover the TOP 3-5 platforms locals in {country} use for:
1. Software reviews and comparisons
2. Tech forums and discussions

Primary language: {language}

## Your Tasks:

1. Use WebSearch to find popular platforms in {country}
2. Search in both {language} and English
3. Focus on: software review sites, tech forums, business directories

## Output Format:

Return JSON:

```json
{{
  "region": "{region}",
  "country": "{country}",
  "platforms_discovered": [
    {{
      "name": "Platform Name",
      "url": "https://...",
      "type": "software_reviews|forum|business_directory|tech_news",
      "language": "{language}",
      "description": "Brief description"
    }}
  ],
  "key_findings": ["Important observation"],
  "confidence": "high|medium|low"
}}
```

Be quick but thorough - find TOP 3-5 most relevant platforms.
"""


async def spawn_discovery_agent(region: str, country: str, language: str, agent_id: int):
    """Spawn a single platform discovery agent"""

    print(f"  [{agent_id}] Spawning agent for {region}...")
    start_time = time.time()

    prompt = create_platform_discovery_prompt(region, country, language)

    # NOTE: In actual implementation, this would use Task tool
    # For now, we'll simulate with a placeholder
    # Real call would be:
    # result = await Task(subagent_type="general-purpose", prompt=prompt)

    # Simulate agent work
    await asyncio.sleep(2)  # Placeholder for actual agent execution

    duration = time.time() - start_time
    print(f"  [{agent_id}] ✅ {region} completed in {duration:.1f}s")

    return {
        "agent_id": agent_id,
        "region": region,
        "duration": duration,
        "status": "completed"
    }


async def test_parallel_agents(num_agents: int, regions: list):
    """Test spawning N agents in parallel"""

    print(f"\n{'='*80}")
    print(f"TEST: Spawning {num_agents} Claude agents in parallel")
    print(f"{'='*80}\n")

    start_time = time.time()

    # Create agent tasks
    tasks = []
    region_data = [
        ("Romania", "Romania", "Romanian"),
        ("Poland", "Poland", "Polish"),
        ("Czech Republic", "Czech Republic", "Czech"),
        ("Japan", "Japan", "Japanese"),
        ("Thailand", "Thailand", "Thai"),
        ("Indonesia", "Indonesia", "Indonesian"),
        ("Germany", "Germany", "German"),
        ("Singapore", "Singapore", "English"),
        ("South Korea", "South Korea", "Korean"),
        ("India", "India", "English"),
    ]

    for i in range(min(num_agents, len(region_data))):
        region, country, language = region_data[i]
        task = spawn_discovery_agent(region, country, language, i+1)
        tasks.append(task)

    # Run all agents in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total_time = time.time() - start_time

    # Print results
    print(f"\n{'='*80}")
    print(f"RESULTS: {num_agents} agents")
    print(f"{'='*80}")
    print(f"Total execution time: {total_time:.1f}s")
    print(f"Average time per agent: {total_time/num_agents:.1f}s")

    successful = sum(1 for r in results if not isinstance(r, Exception))
    failed = num_agents - successful

    print(f"Successful: {successful}/{num_agents}")
    print(f"Failed: {failed}/{num_agents}")

    return {
        "num_agents": num_agents,
        "total_time": total_time,
        "avg_time": total_time / num_agents,
        "successful": successful,
        "failed": failed
    }


async def run_scalability_test():
    """Test different levels of concurrency"""

    print("\n" + "="*100)
    print("SCALABILITY TEST: Claude Agent Parallel Execution")
    print("="*100 + "\n")

    test_cases = [1, 3, 5, 10]
    results = []

    for num_agents in test_cases:
        result = await test_parallel_agents(num_agents, [])
        results.append(result)

        # Wait between tests
        await asyncio.sleep(1)

    # Summary
    print("\n" + "="*100)
    print("SUMMARY: Scalability Test Results")
    print("="*100 + "\n")

    print(f"{'Agents':<10} {'Total Time':<15} {'Avg/Agent':<15} {'Success Rate':<15}")
    print("-" * 60)

    for r in results:
        success_rate = f"{r['successful']}/{r['num_agents']}"
        print(f"{r['num_agents']:<10} {r['total_time']:.1f}s{'':<10} {r['avg_time']:.1f}s{'':<10} {success_rate:<15}")

    print("\n" + "="*100)
    print("NEXT: Run actual Claude agents using Task tool")
    print("="*100 + "\n")


if __name__ == "__main__":
    asyncio.run(run_scalability_test())
