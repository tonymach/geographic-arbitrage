#!/usr/bin/env python3
"""
Simple JSON-Based Orchestrator

No database. Just Claude agents researching and saving to JSON files.
This is what Claude Code was MADE for.
"""

import asyncio
import json
import yaml
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SimpleOrchestrator:
    """
    Spawns Claude Task agents that do REAL research
    Saves everything to local JSON files
    """

    def __init__(self, config_path: str = 'config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.test_mode = self.config.get('test_mode', {}).get('enabled', False)
        self.test_regions = self.config.get('test_mode', {}).get('test_regions', [])

        # JSON output directory
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)

        logger.info("Simple Orchestrator initialized (JSON-based)")
        logger.info(f"Test mode: {self.test_mode}")

    def save_json(self, filename: str, data: dict):
        """Save data to JSON file"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Saved: {filepath}")

    def load_json(self, filename: str) -> dict:
        """Load data from JSON file"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_regions(self) -> list:
        """Get regions to process"""
        if self.test_mode:
            return self.test_regions

        all_regions = []
        for region_group in self.config['regions'].values():
            all_regions.extend(region_group)
        return all_regions

    def get_primary_country(self, region: str) -> str:
        """Get primary country for region"""
        region_map = {
            'Romania': 'Romania',
            'Poland': 'Poland',
            'Czech Republic': 'Czech Republic',
            'United States': 'United States',
            'United Kingdom': 'United Kingdom',
            'Germany': 'Germany',
            'Singapore': 'Singapore',
            'South Korea': 'South Korea',
            'Japan': 'Japan',
            'India': 'India',
            'Thailand': 'Thailand',
            'Indonesia': 'Indonesia',
        }
        return region_map.get(region, region)

    def get_primary_language(self, country: str) -> str:
        """Get primary language for country"""
        language_map = {
            'Romania': 'Romanian',
            'Poland': 'Polish',
            'Czech Republic': 'Czech',
            'United States': 'English',
            'United Kingdom': 'English',
            'Germany': 'German',
            'Singapore': 'English',
            'South Korea': 'Korean',
            'Japan': 'Japanese',
            'India': 'English',
            'Thailand': 'Thai',
            'Indonesia': 'Indonesian',
        }
        return language_map.get(country, 'English')


async def main():
    """Demo of simple orchestrator"""
    logging.basicConfig(level=logging.INFO)

    orch = SimpleOrchestrator()

    # Test save/load
    test_data = {
        'timestamp': datetime.now().isoformat(),
        'message': 'Simple JSON-based system ready!'
    }
    orch.save_json('test.json', test_data)

    loaded = orch.load_json('test.json')
    print(f"\n✅ Test: {loaded['message']}")
    print(f"   Timestamp: {loaded['timestamp']}")


if __name__ == "__main__":
    asyncio.run(main())
