#!/usr/bin/env python3
"""
Demo: True Claude Agent for Platform Discovery

This demonstrates spawning a REAL Claude subagent that can:
- Research platforms autonomously
- Use web search to find local forums
- Reason about what platforms locals would use
- Return structured findings

Compare to hardcoded scripts - this agent THINKS
"""

import json
from pathlib import Path


def create_platform_discovery_prompt(region: str, country: str, language: str) -> str:
    """
    Creates prompt for Claude agent to discover platforms

    The agent will use web search and reasoning to find platforms
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
   - Use web search to find popular platforms in {country}
   - Look for {language}-language platforms, not just English ones
   - Find both general platforms and software-specific ones

2. **Reason About Usage**
   - What would a {country} business owner searching for software use?
   - What forums do {language} speakers actually visit?
   - What platforms have critical mass in this market?

3. **Validate Platforms**
   - Check if platforms are active (recent posts/activity)
   - Verify they have software/tech discussions
   - Assess scrapability (is it accessible?)

## Output Format:

Return a JSON structure:

```json
{{
  "region": "{region}",
  "country": "{country}",
  "language": "{language}",
  "platforms_discovered": [
    {{
      "name": "Platform Name",
      "url": "https://...",
      "type": "forum|review_site|q_and_a|tech_news|social",
      "language": "{language}",
      "description": "What this platform is and why it's relevant",
      "estimated_users": "Rough estimate if known",
      "has_software_discussions": true/false,
      "accessibility": "easy|medium|hard",
      "notes": "Additional context"
    }}
  ],
  "search_queries_used": ["query1", "query2"],
  "reasoning": "Brief explanation of how you identified these platforms",
  "confidence": "high|medium|low"
}}
```

## Instructions:

1. Start by web searching for popular {country} forums and platforms
2. Use {language} search terms as well as English
3. Look for both obvious platforms (e.g., Reddit {country}) and local ones
4. Verify each platform is real and active
5. Reason about which platforms would have software discussions
6. Return structured JSON as specified

Be thorough but practical - find the TOP 5-10 most relevant platforms.
"""


def create_pain_validation_prompt(
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
   - What keywords would indicate need for {category} software?
   - Translate keywords to local language if needed
   - Search for frustrations, complaints, feature requests
   - Look for "looking for", "need better", "problem with" patterns

2. **Interpret Findings**
   - Are people actually frustrated with current solutions?
   - Are they actively looking for software in this category?
   - What specific pain points are mentioned?
   - How intense is the pain (scale 1-10)?

3. **Assess Market Readiness**
   - Is this an emerging need or mature market?
   - Are there signs of digitalization in this vertical?
   - Do discussions suggest willingness to pay for solutions?

## Output Format:

```json
{{
  "target_region": "{target_region}",
  "category": "{category}",
  "pain_signals_found": [
    {{
      "source": "Forum name",
      "url": "https://...",
      "title": "Discussion title",
      "pain_description": "What pain was expressed",
      "pain_intensity": 7.5,
      "posted_date": "2024-11-01",
      "engagement": "Number of upvotes/comments if visible"
    }}
  ],
  "need_score": 7.5,
  "market_readiness": "ready|developing|early|not_ready",
  "key_insights": [
    "Insight 1 about market need",
    "Insight 2 about readiness"
  ],
  "reasoning": "Explain how you assessed need and readiness",
  "confidence": "high|medium|low"
}}
```

## Instructions:

1. Generate search queries for pain signals in this category
2. If the local language isn't English, translate keywords
3. Research the provided forums
4. Interpret what you find - are these REAL pain points?
5. Score the need intensity based on:
   - How many signals you found
   - How intense the frustration is
   - How recent the signals are
   - How many people are affected
6. Return structured JSON

Be honest - if you don't find strong signals, say so!
"""


def create_gap_analysis_prompt(ecosystem_map: dict) -> str:
    """
    Creates prompt for Claude agent to find gaps

    Agent will reason about arbitrage opportunities
    """

    return f"""
You are a Gap Analysis Agent finding software arbitrage opportunities.

## Software Ecosystem Data:

{json.dumps(ecosystem_map, indent=2)}

## Your Mission:

Find opportunities where software is PROVEN in one region but MISSING or WEAK in another.

## Your Tasks:

1. **Compare Ecosystems**
   - For each software category, compare adoption across regions
   - Identify products with strong adoption in one region
   - Check if similar products exist in other regions

2. **Identify Gaps**
   - What's huge in Region A but missing in Region B?
   - Calculate the "gap size" (difference in reviews, adoption)
   - Consider: Is the gap meaningful? Or just noise?

3. **Reason About Opportunities**
   - WHY might this gap exist? (digitalization lag, language barrier, etc.)
   - Is the target market likely to need this software?
   - What would be the play here? (build, localize, partner?)

## Output Format:

```json
{{
  "opportunities": [
    {{
      "source_region": "United States",
      "source_product": "Procore",
      "source_category": "Construction Management",
      "source_metrics": {{"reviews": 3400, "rating": 4.5}},
      "target_region": "Poland",
      "target_competition": "None" or "Product names",
      "gap_score": 9.2,
      "reasoning": "Why this is an opportunity",
      "recommended_approach": "Build localized version | Partner | etc.",
      "estimated_tam": "Rough market size estimate"
    }}
  ],
  "total_gaps_analyzed": 50,
  "opportunities_identified": 10,
  "methodology": "How you identified and ranked opportunities",
  "confidence": "high|medium|low"
}}
```

## Scoring Criteria:

- **Gap Score (0-10):**
  - Review count difference
  - Competition level in target
  - Source product strength
  - Market similarity

## Instructions:

1. Systematically compare each category across all region pairs
2. Use reasoning - not just math - to identify true opportunities
3. Explain WHY each gap represents an opportunity
4. Rank by potential (gap size + market readiness)
5. Return structured JSON

Think like an investor - which opportunities would YOU pursue?
"""


# Demo usage
if __name__ == "__main__":
    print("CLAUDE AGENT PROMPTS")
    print("="*80)
    print("\n1. PLATFORM DISCOVERY AGENT")
    print("-"*80)
    print(create_platform_discovery_prompt("Eastern Europe", "Romania", "Romanian"))

    print("\n\n2. PAIN VALIDATION AGENT")
    print("-"*80)
    opp = {
        "product": "Procore",
        "category": "Construction Management",
        "source_region": "United States",
        "source_reviews": 3400
    }
    forums = [
        {"name": "Wykop", "url": "wykop.pl", "language": "Polish"},
        {"name": "Reddit Poland", "url": "reddit.com/r/Polska", "language": "Polish"}
    ]
    print(create_pain_validation_prompt(opp, "Poland", "Construction Management", forums))

    print("\n\nThese prompts would be sent to Claude subagents via the Task tool.")
    print("Each agent can use web_search, reason about findings, and return structured data.")
