#!/usr/bin/env python3
"""
Global Software Arbitrage - Main Entry Point

Discovers software arbitrage opportunities across global markets by:
1. Discovering local platforms per region (not just US-centric ones)
2. Mapping successful companies and software ecosystems
3. Finding gaps where software dominates one region but is missing in another
4. Validating opportunities with contracts and pain signals

Example opportunities:
- Coworking software dominates UK, missing in Romania (but Romania just started coworking)
- Construction software popular in Germany, weak in Poland
- Vertical SaaS strong in US, nonexistent in emerging markets

Usage:
  python main.py                    # Run full pipeline
  python main.py --test             # Run on test regions only (Romania, Japan)
  python main.py --regions Romania  # Run on specific regions
"""

import asyncio
import argparse
import logging
from pathlib import Path
import yaml
import sys

from agents.orchestrator import MasterOrchestrator


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / 'arbitrage.log')
        ]
    )


async def run_pipeline(
    config_path: str = 'config.yaml',
    test_mode: bool = False,
    regions: list = None,
    verbose: bool = False
):
    """
    Run the full pipeline

    Args:
        config_path: Path to config.yaml
        test_mode: If True, only process test regions
        regions: List of specific regions to process
        verbose: Enable verbose logging
    """

    setup_logging(verbose)

    logger = logging.getLogger(__name__)

    # Load config
    logger.info(f"Loading config from: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Override test mode
    if test_mode:
        config['test_mode']['enabled'] = True
        logger.info("TEST MODE ENABLED")

    # Override regions if specified
    if regions:
        config['test_mode']['enabled'] = True
        config['test_mode']['test_regions'] = regions
        logger.info(f"Processing specific regions: {regions}")

    # Create orchestrator
    orchestrator = MasterOrchestrator(config)

    # Run pipeline
    logger.info("\n🚀 Starting Global Software Arbitrage Pipeline\n")

    results = await orchestrator.run_full_pipeline()

    # Print results
    if results.get('status') == 'completed':
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
        print(f"Regions processed: {len(results.get('regions', []))}")
        print(f"Opportunities found: {results['phases']['gap_detection']['opportunities_found']}")
        print("\nResults exported to:")
        print("  - data/results/opportunities.json")
        print("  - data/results/opportunities.txt")
        print("  - data/results/pipeline_summary.json")
        print("="*80 + "\n")
    else:
        print("\n" + "="*80)
        print("❌ PIPELINE FAILED")
        print("="*80)
        print(f"Error: {results.get('error')}")
        print("="*80 + "\n")

    return results


def main():
    """Main CLI entry point"""

    parser = argparse.ArgumentParser(
        description='Global Software Arbitrage - Find software opportunities across regions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline on all regions
  python main.py

  # Run on test regions only (Romania, Japan)
  python main.py --test

  # Run on specific regions
  python main.py --regions Romania Poland Germany

  # Verbose logging
  python main.py --test --verbose
        """
    )

    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (only process test regions)'
    )

    parser.add_argument(
        '--regions',
        nargs='+',
        help='Specific regions to process (e.g., Romania Japan Germany)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Run pipeline
    try:
        results = asyncio.run(run_pipeline(
            config_path=args.config,
            test_mode=args.test,
            regions=args.regions,
            verbose=args.verbose
        ))

        # Exit code based on status
        sys.exit(0 if results.get('status') == 'completed' else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user\n")
        sys.exit(130)

    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
