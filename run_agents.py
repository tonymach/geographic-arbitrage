#!/usr/bin/env python3
"""
Run Complete Agent Flow

Spawns real Claude Task agents to:
1. Map software ecosystems
2. Detect arbitrage gaps
3. Validate with deep research

Uses your $900 in credits. Saves to local JSON files.
"""

import asyncio
import logging
from simple_orchestrator import SimpleOrchestrator
from agents.real_agent_runner import RealAgentRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("=" * 80)
    logger.info("🚀 CLAUDE AGENT ARBITRAGE DISCOVERY")
    logger.info("=" * 80)
    logger.info("")
    logger.info("This will spawn REAL Claude agents that research and analyze.")
    logger.info("Results saved to data/*.json files.")
    logger.info("")

    # Initialize
    orch = SimpleOrchestrator()
    runner = RealAgentRunner(orch)

    # Configure scope
    regions = ['Poland', 'Romania', 'Czech Republic']
    categories = ['Construction Management', 'HR & Payroll', 'Field Service Management']

    logger.info(f"📍 Regions: {', '.join(regions)}")
    logger.info(f"📦 Categories: {', '.join(categories)}")
    logger.info(f"🎯 Total combinations: {len(regions)} x {len(categories)} = {len(regions) * len(categories)}")
    logger.info("")

    # PHASE 1
    logger.info("=" * 80)
    logger.info("PHASE 1: SOFTWARE ECOSYSTEM MAPPING")
    logger.info("=" * 80)
    ecosystem = await runner.run_phase1_ecosystem_mapping(regions, categories)

    # PHASE 2
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2: ARBITRAGE GAP DETECTION")
    logger.info("=" * 80)
    opportunities = await runner.run_phase2_gap_detection(ecosystem)

    logger.info(f"\n🎯 Found {len(opportunities)} opportunities:")
    for opp in opportunities[:5]:
        logger.info(f"   • {opp['source_product']} → {opp['target_region']} (Gap Score: {opp['gap_score']})")

    # PHASE 3
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 3: VALIDATION & UNIT ECONOMICS")
    logger.info("=" * 80)
    validated = await runner.run_phase3_validation(opportunities)

    # SUMMARY
    logger.info("\n" + "=" * 80)
    logger.info("✅ DISCOVERY COMPLETE")
    logger.info("=" * 80)
    logger.info(f"")
    logger.info(f"📊 Results:")
    logger.info(f"   • Products mapped: {sum(len(v) for v in ecosystem.values())}")
    logger.info(f"   • Opportunities found: {len(opportunities)}")
    logger.info(f"   • Validated opportunities: {len(validated)}")
    logger.info(f"")
    logger.info(f"💾 Saved to:")
    logger.info(f"   • data/products.json")
    logger.info(f"   • data/opportunities.json")
    logger.info(f"   • data/validated.json")
    logger.info(f"")
    logger.info(f"🌐 View results:")
    logger.info(f"   open explorer.html")
    logger.info("")

    # Show top opportunities
    if validated:
        logger.info("=" * 80)
        logger.info("TOP OPPORTUNITIES")
        logger.info("=" * 80)

        for i, opp in enumerate(validated[:5], 1):
            logger.info(f"\n{i}. {opp['source_product']} → {opp['target_region']}")
            logger.info(f"   Gap Score: {opp['gap_score']}")
            logger.info(f"   Demand Score: {opp.get('demand_score', 'N/A')}")

            ue = opp.get('unit_economics', {})
            if ue:
                logger.info(f"   LTV:CAC: {ue.get('ltv_cac_ratio', 'N/A')}")
                logger.info(f"   Payback: {ue.get('payback_months', 'N/A')} months")

            fm = opp.get('financial_model', {})
            if fm:
                logger.info(f"   Year 3 Revenue: ${fm.get('year_3_revenue', 0):,}")

            logger.info(f"   Recommendation: {opp.get('recommendation', 'N/A')}")

    logger.info("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
