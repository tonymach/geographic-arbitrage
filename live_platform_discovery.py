#!/usr/bin/env python3
"""
LIVE Platform Discovery using TRUE Claude Agent

This script demonstrates spawning a REAL Claude subagent via the Task tool
to discover platforms for Romania.

The agent will:
1. Use WebSearch to find Romanian platforms
2. Validate each platform
3. Return structured findings
"""

print("""
================================================================================
LIVE CLAUDE AGENT: Platform Discovery for Romania
================================================================================

This demonstrates TRUE Claude orchestration:

1. We create a research prompt
2. Claude spawns a subagent via Task tool
3. The subagent autonomously:
   - Uses WebSearch to find platforms
   - Validates platforms are active
   - Reasons about relevance
   - Returns structured JSON

4. We parse the results and use them

Ready to spawn the agent!
================================================================================
""")

# The prompt that will be sent to the Claude subagent
PLATFORM_DISCOVERY_PROMPT = """
You are a Platform Discovery Agent researching Romania.

Your mission: Discover what platforms locals in Romania actually use for:
1. Software reviews and comparisons
2. Business discussions and forums
3. Tech news and startup ecosystems
4. Q&A and community support

Primary language: Romanian

## Your Tasks:

1. **Research Local Platforms**
   - Use WebSearch to find popular platforms in Romania
   - Search in both Romanian and English
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
   - Would a Romania business owner looking for software use this?
   - Does this platform have critical mass in the market?
   - Is the content in Romanian or English?

## Search Strategy:

Use queries like:
- "Romania software review sites"
- "Romania tech forums"
- "best software Romania" (in Romanian)
- "Romania startup community"
- "Romania business software comparison"
- "forum software Romania"
- "comunitate tech Romania"

## Output Format:

After your research, return your findings as a JSON code block:

```json
{
  "region": "Romania",
  "country": "Romania",
  "language": "Romanian",
  "platforms_discovered": [
    {
      "name": "Platform Name",
      "url": "https://...",
      "type": "software_reviews|forum|business_directory|tech_news|q_and_a",
      "language": "Romanian|English|Mixed",
      "description": "What this platform is and why it's relevant",
      "estimated_users": "If you can find traffic data or user count",
      "has_software_discussions": true,
      "accessibility": "easy|medium|hard",
      "activity_level": "high|medium|low",
      "notes": "Any important details"
    }
  ],
  "search_queries_used": ["List of queries you used"],
  "key_findings": [
    "Important observations about the Romania platform landscape"
  ],
  "reasoning": "Explain how you identified these platforms and why they're relevant",
  "confidence": "high|medium|low"
}
```

## Important:

- Be thorough but practical - find TOP 5-10 most relevant platforms
- Verify platforms are ACTIVE and RELEVANT
- Explain your reasoning - don't just list URLs
- If you can't find local platforms, explain why

Start your research now!
"""

print("\nPrompt prepared!")
print("\nNOTE: To spawn the agent, Claude will use:")
print("  Task(subagent_type='general-purpose', prompt=PLATFORM_DISCOVERY_PROMPT)")
print("\nThis will create a TRUE Claude agent with:")
print("  ✓ WebSearch capability")
print("  ✓ WebFetch capability")
print("  ✓ Full reasoning")
print("  ✓ Autonomous research")
print("\n" + "="*80)
print("\nReady for Claude to spawn the agent!")
print("="*80)
