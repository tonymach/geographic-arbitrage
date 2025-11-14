#!/usr/bin/env python3
"""
LIVE DEMONSTRATION: TRUE Claude Agent for Platform Discovery

This shows how we'll spawn a REAL Claude subagent that:
- Uses web_search to find local platforms
- Reasons about what platforms locals would use
- Returns structured findings

The agent has FULL autonomy and intelligence - it's not a script!
"""

import asyncio
import json
from pathlib import Path


def create_platform_discovery_task_prompt(region: str, country: str, language: str) -> str:
    """
    Creates the prompt for a TRUE Claude subagent

    This agent will be spawned via the Task tool and will have access to:
    - WebSearch: To find local platforms
    - WebFetch: To verify platforms are active
    - Full reasoning capabilities
    """

    return f"""
You are a Platform Discovery Agent researching {country} ({region}).

Your mission: Discover what platforms locals in {country} actually use for:
1. Software reviews and comparisons
2. Business discussions and forums
3. Tech news and startup ecosystems
4. Q&A and community support

Primary language: {language}

## Your Tasks:

1. **Research Local Platforms**
   - Use WebSearch to find popular platforms in {country}
   - Search in both {language} and English
   - Look for:
     * Software review sites (like G2, but local)
     * Tech forums and communities
     * Business directories
     * Q&A platforms
     * Startup/tech news sites

2. **Validate Each Platform**
   - Use WebFetch to visit each platform
   - Check if it's active (recent content)
   - Verify it has software/tech discussions
   - Assess if it's scrapable

3. **Reason About Relevance**
   - Would a {country} business owner looking for software use this?
   - Does this platform have critical mass in the market?
   - Is the content in {language} or English?

## Search Strategy:

Use queries like:
- "{country} software review sites"
- "{country} tech forums"
- "best software {country}" (in {language})
- "{country} startup community"
- "{country} business software comparison"
- Popular local equivalents of G2/Capterra

## Output Format:

After your research, return your findings as a JSON code block:

```json
{{
  "region": "{region}",
  "country": "{country}",
  "language": "{language}",
  "platforms_discovered": [
    {{
      "name": "Platform Name",
      "url": "https://...",
      "type": "software_reviews|forum|business_directory|tech_news|q_and_a",
      "language": "{language}|English|Mixed",
      "description": "What this platform is and why it's relevant",
      "estimated_users": "If you can find traffic data or user count",
      "has_software_discussions": true,
      "accessibility": "easy|medium|hard",
      "activity_level": "high|medium|low",
      "notes": "Any important details"
    }}
  ],
  "search_queries_used": ["List of queries you used"],
  "key_findings": [
    "Important observations about the {country} platform landscape"
  ],
  "reasoning": "Explain how you identified these platforms and why they're relevant",
  "confidence": "high|medium|low"
}}
```

## Important:

- Be thorough but practical - find TOP 5-10 most relevant platforms
- Verify platforms are ACTIVE and RELEVANT
- Explain your reasoning - don't just list URLs
- If you can't find local platforms, explain why (maybe everything is English-language)

Start your research now!
"""


def create_gap_analysis_task_prompt(ecosystem_map: dict) -> str:
    """
    Creates prompt for Claude agent to find arbitrage opportunities

    This agent will REASON about gaps, not just calculate
    """

    return f"""
You are a Gap Analysis Agent finding software arbitrage opportunities.

## Software Ecosystem Data:

{json.dumps(ecosystem_map, indent=2)}

## Your Mission:

Find opportunities where software is PROVEN in one region but MISSING or WEAK in another.

This is about REASONING, not just math. Look for:

1. **Strong Source Products**
   - What software has massive adoption in mature markets (US, UK, Germany)?
   - What categories are well-established with multiple strong players?

2. **Target Market Gaps**
   - Which emerging markets (Poland, Romania, Indonesia, Thailand) lack these solutions?
   - Where is competition weak or non-existent?
   - Where are companies at the RIGHT stage of digitalization to need this?

3. **Strategic Opportunities**
   - WHY does this gap exist? (language barrier, digitalization lag, market timing)
   - Is the target market READY for this software?
   - What would the play be? (build localized version, partner, white-label)

## Your Tasks:

1. **Systematically Compare Regions**
   - For each category, compare mature vs emerging markets
   - Identify specific products with strong proof (high reviews, high ratings)
   - Find target markets with weak competition

2. **Reason About Each Gap**
   - Is this a REAL opportunity or just noise?
   - Would businesses in the target market actually need this?
   - What signals suggest readiness (digitalization, company types, etc.)?

3. **Score Opportunities**
   - Gap size (review count difference)
   - Source strength (proven product)
   - Target competition (lower is better)
   - Market readiness (are they ready to adopt?)

## Output Format:

Return JSON with your analysis:

```json
{{
  "opportunities": [
    {{
      "source_region": "United States",
      "source_product": "Procore",
      "source_category": "Construction Management",
      "source_metrics": {{"reviews": 3400, "rating": 4.5}},
      "target_region": "Poland",
      "target_competition": ["List of competitors or 'None'"],
      "target_strongest_competitor": {{"name": "X", "reviews": 50}} or null,
      "gap_score": 9.2,
      "reasoning": "Why this is a strong opportunity - explain the market dynamics",
      "market_readiness": "ready|developing|early",
      "recommended_approach": "Your strategic recommendation",
      "estimated_tam": "Rough market size if you can reason about it"
    }}
  ],
  "methodology": "Explain how you identified and ranked opportunities",
  "key_insights": [
    "Strategic insights about global software arbitrage patterns"
  ],
  "confidence": "high|medium|low"
}}
```

## Scoring Guidance:

Gap Score (0-10):
- 9-10: Massive proven market, zero competition, market ready
- 7-8: Strong source, weak competition, good readiness
- 5-6: Moderate opportunity, some competition
- <5: Weak opportunity

Think like an investor - which opportunities would YOU pursue?
"""


def create_pain_validation_task_prompt(
    opportunity: dict,
    target_region: str,
    category: str,
    forums: list
) -> str:
    """
    Creates prompt for Claude agent to validate pain signals

    Agent will research forums in local language and interpret pain
    """

    return f"""
You are a Market Validation Agent researching demand for {category} software in {target_region}.

## Opportunity Being Validated:

{json.dumps(opportunity, indent=2)}

## Your Mission:

Research if businesses in {target_region} actually NEED this type of software by finding pain signals.

## Forums to Research:

{json.dumps(forums, indent=2)}

## Your Tasks:

1. **Search for Pain Signals**
   - Use WebSearch to find discussions about {category} in {target_region}
   - Look for frustrations, complaints, feature requests
   - Search patterns like:
     * "looking for {category} software"
     * "need better solution for [category problem]"
     * "frustrated with current [category] tools"
     * Keywords in local language!

2. **Interpret Findings**
   - Are people actually frustrated with current solutions?
   - Are they actively looking for software in this category?
   - What specific pain points are mentioned?
   - How intense is the pain? (1-10 scale)

3. **Assess Market Readiness**
   - Is this an emerging need or mature market?
   - Are there signs of digitalization in this vertical?
   - Do discussions suggest willingness to pay?

## Search Strategy:

For each forum, search for:
- Category-specific keywords in local language
- Pain indicators ("problem with", "need better", "looking for")
- Recent discussions (last 1-2 years)

## Output Format:

```json
{{
  "target_region": "{target_region}",
  "category": "{category}",
  "pain_signals_found": [
    {{
      "source": "Forum name or Reddit",
      "url": "https://...",
      "title": "Discussion title",
      "pain_description": "What pain was expressed",
      "pain_intensity": 7.5,
      "posted_date": "Approximate date if visible",
      "engagement": "Upvotes/comments if visible",
      "quote": "Relevant quote from discussion"
    }}
  ],
  "need_score": 7.5,
  "market_readiness": "ready|developing|early|not_ready",
  "key_insights": [
    "What you learned about market need",
    "Readiness signals you observed"
  ],
  "reasoning": "Explain how you assessed need and readiness",
  "confidence": "high|medium|low",
  "recommendation": "Should we pursue this opportunity?"
}}
```

## Scoring:

Need Score (0-10):
- 9-10: Strong, frequent pain signals + high engagement + recent
- 7-8: Clear pain signals + moderate engagement
- 5-6: Some pain signals but weak/old
- <5: Little to no evidence of need

Be honest - if you don't find strong signals, say so!
Start researching now.
"""


async def demonstrate_agent_spawning():
    """
    This demonstrates how we'll spawn TRUE Claude agents

    In the actual implementation, we'll use the Task tool like this:

    result = await Task(
        subagent_type="general-purpose",
        description="Discover platforms for Romania",
        prompt=create_platform_discovery_task_prompt("Romania", "Romania", "Romanian")
    )

    The agent will:
    1. Use WebSearch to find local platforms
    2. Use WebFetch to validate them
    3. Reason about relevance
    4. Return structured JSON
    """

    print("\n" + "="*100)
    print("DEMONSTRATION: TRUE Claude Agent Orchestration")
    print("="*100 + "\n")

    print("🤖 How it works:\n")
    print("1. We create a detailed prompt for a Claude subagent")
    print("2. We spawn the agent using the Task tool")
    print("3. The agent autonomously:")
    print("   - Uses WebSearch to research platforms")
    print("   - Uses WebFetch to validate platforms")
    print("   - Reasons about what locals would use")
    print("   - Returns structured JSON findings")
    print("4. We collect the agent's results and use them\n")

    # Example 1: Platform Discovery
    print("\n" + "="*100)
    print("EXAMPLE 1: Platform Discovery Agent for Romania")
    print("="*100 + "\n")

    prompt = create_platform_discovery_task_prompt("Romania", "Romania", "Romanian")

    print("This prompt will be sent to a Claude subagent:\n")
    print("-" * 100)
    print(prompt)
    print("-" * 100)

    print("\n💡 The agent will autonomously research and return JSON with discovered platforms!\n")

    # Example 2: Gap Analysis
    print("\n" + "="*100)
    print("EXAMPLE 2: Gap Analysis Agent")
    print("="*100 + "\n")

    ecosystem_map = {
        "United States": {
            "Construction Management": [
                {"name": "Procore", "reviews": 3400, "rating": 4.5}
            ]
        },
        "Poland": {
            "Construction Management": [
                {"name": "Local Polish Tool", "reviews": 45, "rating": 4.0}
            ]
        }
    }

    gap_prompt = create_gap_analysis_task_prompt(ecosystem_map)

    print("This agent will REASON about arbitrage opportunities:\n")
    print("-" * 100)
    print(gap_prompt[:1000] + "...\n[truncated]")
    print("-" * 100)

    print("\n💡 The agent will reason about WHY gaps exist and which ones to pursue!\n")

    # Example 3: Pain Validation
    print("\n" + "="*100)
    print("EXAMPLE 3: Pain Validation Agent")
    print("="*100 + "\n")

    opportunity = {
        "source_product": "Procore",
        "category": "Construction Management",
        "target_region": "Poland"
    }

    forums = [
        {"name": "Wykop", "url": "wykop.pl", "language": "Polish"},
        {"name": "Reddit Poland", "language": "Polish"}
    ]

    pain_prompt = create_pain_validation_task_prompt(opportunity, "Poland", "Construction Management", forums)

    print("This agent will research local forums in Polish:\n")
    print("-" * 100)
    print(pain_prompt[:1000] + "...\n[truncated]")
    print("-" * 100)

    print("\n💡 The agent will interpret pain signals in native language!\n")

    print("\n" + "="*100)
    print("NEXT STEP: Integrate Task tool to spawn these agents for real!")
    print("="*100 + "\n")


if __name__ == "__main__":
    asyncio.run(demonstrate_agent_spawning())
