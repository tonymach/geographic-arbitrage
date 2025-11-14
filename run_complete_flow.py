#!/usr/bin/env python3
"""
Run Complete Arbitrage Discovery Flow

This script runs all phases:
1. Phase 0: Platform Discovery (already done - 45 platforms in Turso)
2. Phase 1: Ecosystem Mapping
3. Phase 2: Gap Detection
4. Phase 3: Validation & Unit Economics
"""

import asyncio
import logging
from dotenv import load_dotenv

from claude_orchestrator import ClaudeOrchestrator
from agents.agent_runner import AgentRunner

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("=" * 80)
    logger.info("COMPLETE ARBITRAGE DISCOVERY FLOW")
    logger.info("=" * 80)
    logger.info("")

    # Initialize orchestrator (connects to Turso)
    orch = ClaudeOrchestrator()
    runner = AgentRunner(orch)

    # Configure regions and categories
    regions = ['Poland', 'Romania', 'Czech Republic']
    categories = ['Construction Management', 'HR & Payroll', 'Field Service Management']

    logger.info(f"Regions: {regions}")
    logger.info(f"Categories: {categories}")
    logger.info("")

    # PHASE 1: Ecosystem Mapping
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1: SOFTWARE ECOSYSTEM MAPPING")
    logger.info("=" * 80)

    ecosystem_map = await runner.run_phase1_ecosystem_mapping(regions, categories)

    # PHASE 2: Gap Detection
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2: ARBITRAGE GAP DETECTION")
    logger.info("=" * 80)

    opportunities = await runner.run_phase2_gap_detection(ecosystem_map)

    logger.info(f"\n🎯 Found {len(opportunities)} opportunities:")
    for opp in opportunities[:5]:
        logger.info(f"   • {opp['source_product']} → {opp['target_region']} (Gap Score: {opp['gap_score']})")

    # PHASE 3: Validation
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 3: VALIDATION & UNIT ECONOMICS")
    logger.info("=" * 80)

    validated = await runner.run_phase3_validation(opportunities)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("DISCOVERY COMPLETE")
    logger.info("=" * 80)
    logger.info(f"")
    logger.info(f"Total Opportunities Found: {len(opportunities)}")
    logger.info(f"Validated Opportunities: {len(validated)}")
    logger.info(f"")
    logger.info("Top 5 Opportunities:")

    for i, opp in enumerate(validated[:5], 1):
        logger.info(f"\n{i}. {opp['source_product']} → {opp['target_region']}")
        logger.info(f"   Category: {opp['source_category']}")
        logger.info(f"   Gap Score: {opp['gap_score']}")
        logger.info(f"   Demand Score: {opp.get('demand_score', 'N/A')}")
        logger.info(f"   TAM: {opp.get('market_size', {}).get('tam', 'N/A')}")
        logger.info(f"   LTV:CAC: {opp.get('unit_economics', {}).get('ltv_cac_ratio', 'N/A')}")
        logger.info(f"   Year 3 Revenue: ${opp.get('financial_model', {}).get('year_3_revenue', 0):,}")
        logger.info(f"   Recommendation: {opp.get('recommendation', 'N/A')}")

    logger.info("\n" + "=" * 80)
    logger.info("All data saved to Turso database")
    logger.info("View in dashboard: explorer_turso.html")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
