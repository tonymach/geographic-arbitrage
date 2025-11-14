#!/usr/bin/env python3
"""
Batch Processor for Global Software Arbitrage

Runs the pipeline at SCALE to discover and validate 10,000+ opportunities.

Process:
1. Expands to all available regions
2. Tests all 25+ software categories
3. Runs in batches for performance
4. Validates each opportunity with local forums
5. Tracks progress
6. Exports consolidated results

Usage:
    python batch_processor.py --target 10000
    python batch_processor.py --batch-size 1000
    python batch_processor.py --continue  # Resume from last run
"""

import asyncio
import argparse
import logging
from pathlib import Path
import yaml
import json
from datetime import datetime
import sys

from agents.orchestrator import MasterOrchestrator


class BatchProcessor:
    """
    Processes arbitrage opportunities at scale

    Target: 10,000 validated opportunities
    """

    def __init__(self, config_path: str = 'config.yaml', target_count: int = 10000):
        self.config_path = config_path
        self.target_count = target_count

        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Progress tracking
        self.progress_file = Path('data/batch_progress.json')
        self.results_dir = Path('data/batch_results')
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.total_found = 0
        self.total_validated = 0
        self.batches_completed = 0

        self.logger = logging.getLogger(__name__)

    def load_progress(self) -> dict:
        """Load progress from previous run"""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return json.load(f)
        return {
            'total_opportunities': 0,
            'total_validated': 0,
            'batches_completed': 0,
            'regions_processed': [],
            'started_at': None,
            'last_updated': None
        }

    def save_progress(self, progress: dict):
        """Save current progress"""
        progress['last_updated'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)

    async def run_batch_discovery(
        self,
        batch_id: int,
        regions: list,
        categories: list = None
    ) -> dict:
        """
        Run a single batch of discovery

        Args:
            batch_id: Batch number
            regions: List of regions to process
            categories: Optional category list override

        Returns:
            Batch results
        """

        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"BATCH {batch_id}: Processing {len(regions)} regions")
        self.logger.info(f"{'='*80}\n")

        # Configure for this batch
        batch_config = self.config.copy()
        batch_config['test_mode']['enabled'] = True
        batch_config['test_mode']['test_regions'] = regions

        if categories:
            # Override categories in software mapper
            # (Would need to pass this through config)
            pass

        # Create orchestrator for this batch
        orchestrator = MasterOrchestrator(batch_config, db_path=f"data/batch_{batch_id}.db")

        # Run pipeline
        results = await orchestrator.run_full_pipeline()

        # Extract stats
        batch_stats = {
            'batch_id': batch_id,
            'regions': regions,
            'opportunities_found': results['phases']['gap_detection']['opportunities_found'],
            'opportunities_validated': results['phases'].get('validation', {}).get('opportunities_validated', 0),
            'high_confidence': results['phases'].get('validation', {}).get('high_confidence', 0),
            'medium_confidence': results['phases'].get('validation', {}).get('medium_confidence', 0),
            'duration_seconds': results['duration_seconds'],
            'completed_at': datetime.now().isoformat()
        }

        # Save batch results
        batch_file = self.results_dir / f'batch_{batch_id}_results.json'
        with open(batch_file, 'w') as f:
            json.dump(batch_stats, f, indent=2)

        self.logger.info(f"\n✅ Batch {batch_id} complete:")
        self.logger.info(f"   Found: {batch_stats['opportunities_found']}")
        self.logger.info(f"   Validated: {batch_stats['opportunities_validated']}")
        self.logger.info(f"   High confidence: {batch_stats['high_confidence']}")

        return batch_stats

    async def run_to_target(self, resume: bool = False):
        """
        Run batches until we reach target count

        Args:
            resume: Continue from previous run
        """

        self.logger.info(f"\n{'='*100}")
        self.logger.info(f"BATCH PROCESSOR - TARGET: {self.target_count:,} VALIDATED OPPORTUNITIES")
        self.logger.info(f"{'='*100}\n")

        # Load progress if resuming
        progress = self.load_progress() if resume else {
            'total_opportunities': 0,
            'total_validated': 0,
            'batches_completed': 0,
            'regions_processed': [],
            'started_at': datetime.now().isoformat(),
            'last_updated': None
        }

        start_batch_id = progress['batches_completed'] + 1
        total_validated = progress['total_validated']

        # Get all available regions
        all_regions = []
        for region_group in self.config['regions'].values():
            all_regions.extend(region_group)

        self.logger.info(f"Available regions: {len(all_regions)}")
        self.logger.info(f"Starting from batch: {start_batch_id}")
        self.logger.info(f"Already validated: {total_validated:,}\n")

        # Create batches of regions
        batch_size = 5  # Process 5 regions per batch
        region_batches = [
            all_regions[i:i + batch_size]
            for i in range(0, len(all_regions), batch_size)
        ]

        self.logger.info(f"Total batches to run: {len(region_batches)}")

        # Run batches until target reached
        batch_id = start_batch_id

        for region_batch in region_batches:
            if total_validated >= self.target_count:
                self.logger.info(f"\n🎯 TARGET REACHED: {total_validated:,} validated opportunities")
                break

            # Run this batch
            batch_results = await self.run_batch_discovery(
                batch_id=batch_id,
                regions=region_batch
            )

            # Update totals
            total_validated += batch_results['opportunities_validated']
            progress['total_opportunities'] += batch_results['opportunities_found']
            progress['total_validated'] = total_validated
            progress['batches_completed'] = batch_id
            progress['regions_processed'].extend(region_batch)

            # Save progress
            self.save_progress(progress)

            self.logger.info(f"\n📊 CUMULATIVE PROGRESS:")
            self.logger.info(f"   Total validated: {total_validated:,} / {self.target_count:,}")
            self.logger.info(f"   Progress: {(total_validated/self.target_count)*100:.1f}%")
            self.logger.info(f"   Batches completed: {batch_id}")

            batch_id += 1

        # Final summary
        self.logger.info(f"\n{'='*100}")
        self.logger.info(f"BATCH PROCESSING COMPLETE")
        self.logger.info(f"{'='*100}")
        self.logger.info(f"Total opportunities found: {progress['total_opportunities']:,}")
        self.logger.info(f"Total validated: {progress['total_validated']:,}")
        self.logger.info(f"Batches completed: {progress['batches_completed']}")
        self.logger.info(f"Regions processed: {len(progress['regions_processed'])}")

        # Consolidate all batch results
        await self.consolidate_results()

        return progress

    async def consolidate_results(self):
        """
        Consolidate all batch results into single file

        Aggregates:
        - All opportunities
        - Top opportunities by score
        - Opportunities by category
        - Opportunities by region
        - High confidence opportunities
        """

        self.logger.info("\n📦 Consolidating all batch results...")

        all_opportunities = []
        all_stats = []

        # Load all batch result files
        for batch_file in sorted(self.results_dir.glob('batch_*_results.json')):
            with open(batch_file) as f:
                stats = json.load(f)
                all_stats.append(stats)

            # Load opportunities from batch DB
            # (Would need to query each batch's database)

        # Create consolidated report
        consolidated = {
            'generated_at': datetime.now().isoformat(),
            'total_batches': len(all_stats),
            'total_opportunities': sum(s['opportunities_found'] for s in all_stats),
            'total_validated': sum(s['opportunities_validated'] for s in all_stats),
            'high_confidence_count': sum(s['high_confidence'] for s in all_stats),
            'medium_confidence_count': sum(s['medium_confidence'] for s in all_stats),
            'batch_stats': all_stats
        }

        # Export
        output_file = self.results_dir / 'consolidated_results.json'
        with open(output_file, 'w') as f:
            json.dump(consolidated, f, indent=2)

        self.logger.info(f"✅ Consolidated results saved to: {output_file}")

        # Print summary
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"CONSOLIDATED SUMMARY")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Total opportunities: {consolidated['total_opportunities']:,}")
        self.logger.info(f"Validated opportunities: {consolidated['total_validated']:,}")
        self.logger.info(f"High confidence (8.0+): {consolidated['high_confidence_count']:,}")
        self.logger.info(f"Medium confidence (6-8): {consolidated['medium_confidence_count']:,}")
        self.logger.info(f"{'='*80}\n")


async def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description='Batch processor for global software arbitrage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run to discover 10,000 opportunities
  python batch_processor.py --target 10000

  # Run specific number
  python batch_processor.py --target 5000

  # Resume from previous run
  python batch_processor.py --continue

  # Quick test (100 opportunities)
  python batch_processor.py --target 100
        """
    )

    parser.add_argument(
        '--target',
        type=int,
        default=10000,
        help='Target number of validated opportunities (default: 10,000)'
    )

    parser.add_argument(
        '--continue',
        dest='resume',
        action='store_true',
        help='Resume from previous run'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/batch_processor.log')
        ]
    )

    # Create processor
    processor = BatchProcessor(target_count=args.target)

    # Run to target
    try:
        progress = await processor.run_to_target(resume=args.resume)

        print(f"\n✅ Successfully processed {progress['total_validated']:,} opportunities")
        print(f"Results saved to: data/batch_results/consolidated_results.json")

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Batch processing interrupted")
        print("Run with --continue to resume")
        sys.exit(130)

    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
