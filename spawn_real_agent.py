#!/usr/bin/env python3
"""
Test spawning ONE real Task agent

This is a test to verify Task agents work before launching 20
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def test_single_agent():
    """Test spawning a single real Claude Task agent"""

    logger.info("=" * 80)
    logger.info("🧪 TESTING SINGLE REAL TASK AGENT")
    logger.info("=" * 80)

    # Simple test prompt
    prompt = """You are a software ecosystem research agent.

**Your Mission**: Find 3-5 construction management software products in Poland.

**Research Steps**:
1. Use WebSearch to find construction management software in Poland
2. Search for both English and Polish terms
3. Find products with pricing, reviews, adoption

**Output Format** (JSON):
```json
{
  "products": [
    {
      "name": "Product Name",
      "url": "https://...",
      "reviews": 100,
      "rating": 4.2,
      "pricing": "$99/month",
      "adoption": "medium"
    }
  ]
}
```

Return ONLY JSON, no other text.
"""

    logger.info("📝 Prompt created")
    logger.info("🚀 Spawning Task agent...")

    # NOTE: In Claude Code environment, we'd use the Task tool
    # Since we're in a Python script, we can't directly access Claude Code's Task tool
    # We need to either:
    # 1. Call this from within Claude Code (ask Claude to run it)
    # 2. Or use the agent framework to simulate

    logger.info("⚠️  Task tool requires Claude Code environment")
    logger.info("    This script should be called BY Claude, not run standalone")

    return {
        'status': 'ready',
        'message': 'Prompt ready for Claude to execute via Task tool'
    }


if __name__ == "__main__":
    result = asyncio.run(test_single_agent())
    print(f"\n✅ Result: {result}")
