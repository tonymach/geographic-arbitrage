#!/usr/bin/env python3
"""
Test script for Claude Orchestrator

Demonstrates TRUE Claude subagent orchestration
"""

import asyncio
import logging
from claude_orchestrator import ClaudeOrchestrator


async def test_platform_discovery():
    """Test platform discovery with Claude agents"""

    print("\n" + "="*80)
    print("TESTING CLAUDE-ORCHESTRATED PLATFORM DISCOVERY")
    print("="*80 + "\n")

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    # Create orchestrator
    orchestrator = ClaudeOrchestrator()

    # Test with Romania first (single region)
    test_regions = ['Romania']

    print("Phase 0: Platform Discovery")
    print(f"Testing with: {test_regions}\n")

    # Spawn platform discovery agents
    platform_map = await orchestrator.spawn_platform_discovery_agents(test_regions)

    # Print results
    print("\n" + "="*80)
    print("PLATFORM DISCOVERY RESULTS")
    print("="*80 + "\n")

    for region, platforms in platform_map.items():
        print(f"\n{region}:")
        print("-" * 40)

        if platforms:
            for platform in platforms:
                print(f"\n  📍 {platform.get('name', 'Unknown')}")
                print(f"     Type: {platform.get('type', 'unknown')}")
                print(f"     URL: {platform.get('url', 'N/A')}")
                print(f"     Language: {platform.get('language', 'unknown')}")
        else:
            print("  No platforms discovered")

    print("\n" + "="*80)
    print(f"Total platforms discovered: {sum(len(p) for p in platform_map.values())}")
    print("="*80 + "\n")

    return platform_map


async def test_full_pipeline():
    """Test the full Claude orchestration pipeline"""

    print("\n" + "="*80)
    print("TESTING FULL CLAUDE ORCHESTRATION PIPELINE")
    print("="*80 + "\n")

    logging.basicConfig(level=logging.INFO)

    orchestrator = ClaudeOrchestrator()

    # Run with small set of regions
    results = await orchestrator.discover_opportunities(
        regions=['Romania', 'Poland', 'United Kingdom'],
        target_count=10
    )

    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"Duration: {results['duration_seconds']:.1f}s")
    print(f"Regions: {len(results['regions_processed'])}")
    print(f"Opportunities: {results['total_opportunities']}")
    print(f"High confidence: {results['high_confidence']}")
    print("="*80 + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "full":
        asyncio.run(test_full_pipeline())
    else:
        asyncio.run(test_platform_discovery())
