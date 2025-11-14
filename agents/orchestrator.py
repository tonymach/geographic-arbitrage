"""
Master Orchestrator

Coordinates all phases of the Global Software Arbitrage system:

Phase 0: Platform Discovery - Find local platforms per region
Phase 1: Company Mapping - Map successful companies per region
Phase 2: Software Ecosystem Mapping - Map software products per region
Phase 3: Cross-Region Gap Detection - Find arbitrage opportunities
Phase 4: Validation - Validate with contracts and pain signals (TODO)

Runs all agents in the correct order with proper data flow.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import Database
from agents.platform_discovery_agent import PlatformDiscoveryAgent
from agents.company_mapper_agent import CompanyMapperAgent
from agents.software_mapper_agent import SoftwareMapperAgent
from agents.cross_reference_agent import CrossReferenceAgent
from agents.pain_validator_agent import PainValidatorAgent

logger = logging.getLogger(__name__)


class MasterOrchestrator:
    """
    Orchestrates the entire Global Software Arbitrage pipeline
    """

    def __init__(self, config: Dict[str, Any], db_path: str = "data/arbitrage.db"):
        self.config = config
        self.db_path = db_path

        # Initialize database
        self.db = Database(db_path)
        self.db.connect()
        self.db.init_schema()

        # Initialize agents
        self.platform_discovery = PlatformDiscoveryAgent(config, self.db)
        self.company_mapper = CompanyMapperAgent(config, self.db)
        self.software_mapper = SoftwareMapperAgent(config, self.db)
        self.cross_reference = CrossReferenceAgent(config, self.db)
        self.pain_validator = PainValidatorAgent(config, self.db)

        # Get regions from config
        all_regions = []
        for region_group, countries in config.get('regions', {}).items():
            all_regions.extend(countries)

        self.regions = all_regions

        # Test mode
        self.test_mode = config.get('test_mode', {}).get('enabled', False)
        if self.test_mode:
            test_regions = config.get('test_mode', {}).get('test_regions', [])
            self.regions = [r for r in self.regions if r in test_regions]
            logger.info(f"TEST MODE: Using regions: {self.regions}")

        logger.info(f"Master Orchestrator initialized")
        logger.info(f"  Regions to process: {len(self.regions)}")
        logger.info(f"  Database: {db_path}")

    async def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete pipeline

        Returns summary of results
        """

        logger.info("\n" + "="*80)
        logger.info("STARTING GLOBAL SOFTWARE ARBITRAGE PIPELINE")
        logger.info("="*80 + "\n")

        start_time = datetime.now()

        results = {
            'start_time': start_time.isoformat(),
            'regions': self.regions,
            'phases': {}
        }

        try:
            # PHASE 0: Discover Platforms
            logger.info("\n🔍 PHASE 0: Platform Discovery")
            logger.info("-" * 80)

            platform_map = await self.platform_discovery.discover_all_regional_platforms(
                regions=self.regions,
                test_mode=self.test_mode
            )

            results['phases']['platform_discovery'] = {
                'status': 'completed',
                'platforms_discovered': sum(len(p) for p in platform_map.values())
            }

            # Export platform map
            self.platform_discovery.export_platform_map(platform_map)
            self.platform_discovery.print_summary(platform_map)

            # PHASE 1: Map Companies
            logger.info("\n🏢 PHASE 1: Company Mapping")
            logger.info("-" * 80)

            company_map = await self.company_mapper.map_all_regions(
                regions=self.regions,
                platform_map=platform_map
            )

            results['phases']['company_mapping'] = {
                'status': 'completed',
                'companies_mapped': sum(len(c) for c in company_map.values())
            }

            # Export company map
            self.company_mapper.export_company_map(company_map)

            # PHASE 2: Map Software Ecosystems
            logger.info("\n💻 PHASE 2: Software Ecosystem Mapping")
            logger.info("-" * 80)

            ecosystem_map = await self.software_mapper.map_all_ecosystems(
                regions=self.regions,
                platform_map=platform_map,
                company_map=company_map
            )

            total_products = sum(
                sum(len(products) for products in ecosystem.get('popular_products', {}).values())
                for ecosystem in ecosystem_map.values()
            )

            results['phases']['software_mapping'] = {
                'status': 'completed',
                'products_mapped': total_products
            }

            # Export ecosystem map
            self.software_mapper.export_ecosystem_map(ecosystem_map)

            # PHASE 3: Find Arbitrage Opportunities
            logger.info("\n🎯 PHASE 3: Cross-Region Gap Detection")
            logger.info("-" * 80)

            opportunities = await self.cross_reference.find_all_opportunities(
                ecosystem_map=ecosystem_map
            )

            results['phases']['gap_detection'] = {
                'status': 'completed',
                'opportunities_found': len(opportunities)
            }

            # PHASE 4: Deep Market Validation
            logger.info("\n✅ PHASE 4: Deep Market Validation")
            logger.info("-" * 80)

            validated_opportunities = await self.pain_validator.validate_all_opportunities(
                opportunities=opportunities
            )

            results['phases']['validation'] = {
                'status': 'completed',
                'opportunities_validated': len(validated_opportunities),
                'high_confidence': sum(1 for o in validated_opportunities if o.get('need_validated_score', 0) >= 8.0),
                'medium_confidence': sum(1 for o in validated_opportunities if 6.0 <= o.get('need_validated_score', 0) < 8.0),
                'low_confidence': sum(1 for o in validated_opportunities if o.get('need_validated_score', 0) < 6.0)
            }

            # Replace opportunities with validated ones
            opportunities = validated_opportunities

            # Export validated opportunities
            self.cross_reference.export_opportunities(opportunities)

            # Print final summary
            self._print_final_summary(results, opportunities)

            # Mark completion
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = duration
            results['status'] = 'completed'

            # Export summary
            self._export_summary(results, opportunities)

        except Exception as e:
            logger.error(f"\n❌ Pipeline failed: {e}", exc_info=True)
            results['status'] = 'failed'
            results['error'] = str(e)

        finally:
            self.db.close()

        return results

    def _print_final_summary(
        self,
        results: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ):
        """Print final pipeline summary"""

        print("\n" + "="*80)
        print("PIPELINE SUMMARY")
        print("="*80 + "\n")

        for phase_name, phase_result in results.get('phases', {}).items():
            status = phase_result.get('status', 'unknown')
            print(f"{phase_name.upper():.<40} {status}")

            if phase_name == 'platform_discovery':
                print(f"  Platforms discovered: {phase_result.get('platforms_discovered', 0)}")
            elif phase_name == 'company_mapping':
                print(f"  Companies mapped: {phase_result.get('companies_mapped', 0)}")
            elif phase_name == 'software_mapping':
                print(f"  Products mapped: {phase_result.get('products_mapped', 0)}")
            elif phase_name == 'gap_detection':
                print(f"  Opportunities found: {phase_result.get('opportunities_found', 0)}")

        print("\n" + "="*80)
        print("TOP 10 OPPORTUNITIES")
        print("="*80 + "\n")

        for i, opp in enumerate(opportunities[:10], 1):
            print(f"{i}. {opp['source_product_name']} ({opp['source_category']})")
            print(f"   {opp['source_region']} → {opp['target_region']}")
            print(f"   Opportunity Score: {opp.get('opportunity_score', 0)}/10")
            print(f"   Gap Score: {opp['gap_score']}/10")
            print(f"   Competition Level: {opp['target_competition_level']}/5")
            print()

        print("="*80 + "\n")

    def _export_summary(
        self,
        results: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ):
        """Export pipeline summary"""

        output_dir = Path("data/results")
        output_dir.mkdir(parents=True, exist_ok=True)

        summary_path = output_dir / "pipeline_summary.json"

        summary = {
            **results,
            'top_opportunities': opportunities[:10],
            'config': {
                'test_mode': self.test_mode,
                'regions': self.regions,
                'min_gap_score': self.config.get('gap_detection', {}).get('min_gap_score'),
            }
        }

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"\n✅ Pipeline summary exported to: {summary_path}")


async def main():
    """
    Main entry point
    """

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/arbitrage.log')
        ]
    )

    # Create logs directory
    Path('logs').mkdir(exist_ok=True)

    # Load config
    import yaml

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Create orchestrator
    orchestrator = MasterOrchestrator(config)

    # Run pipeline
    results = await orchestrator.run_full_pipeline()

    # Print final status
    if results.get('status') == 'completed':
        print("\n✅ Pipeline completed successfully!")
        print(f"   Duration: {results.get('duration_seconds', 0):.2f} seconds")
        print(f"   Opportunities found: {results['phases']['gap_detection']['opportunities_found']}")
    else:
        print(f"\n❌ Pipeline failed: {results.get('error')}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
