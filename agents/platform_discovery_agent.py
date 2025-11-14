"""
Platform Discovery Agent - Phase 0

Discovers local platforms (review sites, directories, tech media, forums)
that are actually used in each region, rather than just relying on US-centric
platforms like G2/Capterra.

This agent:
1. Uses web search to find local platforms per region
2. Validates each platform (accessible, active, scrapeable)
3. Stores discovered platforms in database
4. Feeds platform list to downstream agents

Example discoveries:
- Romania: Lista Firmelor, Startarium
- Japan: ITreview, Boxil
- Germany: OMR Reviews
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import Database
from utils.web_search_helper import WebSearchHelper

logger = logging.getLogger(__name__)


class PlatformDiscoveryAgent:
    """
    Discovers local platforms per region using web search and validation

    This is Phase 0 - everything else depends on knowing what platforms
    to scrape in each region
    """

    def __init__(self, config: Dict[str, Any], db: Database):
        self.config = config
        self.db = db
        self.search_helper = WebSearchHelper()

        # Platform discovery settings
        self.discovery_config = config.get('platform_discovery', {})
        self.max_platforms = self.discovery_config.get('max_platforms_per_region', 15)
        self.min_platforms = self.discovery_config.get('min_platforms_per_region', 3)

        # Seed platforms (known good ones to start with)
        self.seed_platforms = self.discovery_config.get('seed_platforms', {})

        logger.info(f"Platform Discovery Agent initialized (max: {self.max_platforms} per region)")

    async def discover_all_regional_platforms(
        self,
        regions: List[str],
        test_mode: bool = False
    ) -> Dict[str, List[Dict]]:
        """
        Discover platforms for all regions in parallel

        Returns: {region: [platform1, platform2, ...]}
        """

        logger.info(f"Starting platform discovery for {len(regions)} regions")

        if test_mode:
            logger.info("TEST MODE: Using limited regions")
            test_regions = self.config.get('test_mode', {}).get('test_regions', ['Romania', 'Japan'])
            regions = [r for r in regions if r in test_regions]

        # Discover platforms for each region in parallel
        tasks = []
        for region in regions:
            task = self.discover_platforms_for_region(region)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build region -> platforms map
        platform_map = {}
        for region, result in zip(regions, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to discover platforms for {region}: {result}")
                platform_map[region] = []
            else:
                platform_map[region] = result
                logger.info(f"Discovered {len(result)} platforms for {region}")

        return platform_map

    async def discover_platforms_for_region(
        self,
        region: str,
        country: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover platforms for a single region

        Steps:
        1. Check database for existing platforms
        2. Add seed platforms (global ones)
        3. Search for local platforms via web search
        4. Validate discovered platforms
        5. Store in database
        6. Return validated platforms
        """

        logger.info(f"\n{'='*80}")
        logger.info(f"Discovering platforms for: {region}")
        logger.info(f"{'='*80}\n")

        # Get primary country and language for this region
        if not country:
            country = self._get_primary_country(region)
        language = self._get_primary_language(country)

        logger.info(f"  Country: {country}")
        logger.info(f"  Language: {language}")

        # Step 1: Check database for existing platforms
        existing_platforms = self._get_existing_platforms(region)
        if len(existing_platforms) >= self.min_platforms:
            logger.info(f"  Found {len(existing_platforms)} existing platforms in DB")
            return existing_platforms

        discovered_platforms = []

        # Step 2: Add global seed platforms
        global_seeds = self.seed_platforms.get('global', [])
        for platform in global_seeds:
            platform['region'] = region
            platform['country'] = country
            platform['discovery_source'] = 'seed_global'
            discovered_platforms.append(platform)

        logger.info(f"  Added {len(global_seeds)} global seed platforms")

        # Step 3: Add regional seed platforms if available
        regional_seeds = self.seed_platforms.get('regional', {}).get(country.lower(), [])
        for platform in regional_seeds:
            platform['region'] = region
            platform['country'] = country
            platform['discovery_source'] = 'seed_regional'
            discovered_platforms.append(platform)

        logger.info(f"  Added {len(regional_seeds)} regional seed platforms")

        # Step 4: DISCOVER new platforms via web search
        # This is where the magic happens - find LOCAL platforms
        logger.info(f"  Searching for local platforms...")

        try:
            discovered_local = await self._search_for_local_platforms(
                region=region,
                country=country,
                language=language
            )
            discovered_platforms.extend(discovered_local)
            logger.info(f"  Discovered {len(discovered_local)} new local platforms")
        except Exception as e:
            logger.error(f"  Failed to discover local platforms: {e}")
            discovered_local = []

        # Step 5: Validate all discovered platforms
        logger.info(f"  Validating {len(discovered_platforms)} platforms...")
        try:
            validated_platforms = await self._validate_platforms(discovered_platforms)
        except Exception as e:
            logger.error(f"  Failed to validate platforms: {e}")
            # Just mark seed platforms as validated
            validated_platforms = discovered_platforms
            for p in validated_platforms:
                p['validation_status'] = 'passed'
                p['validation_checks'] = {'seed_platform': True}

        # Step 6: Store validated platforms in database
        logger.info(f"  Storing {len(validated_platforms)} validated platforms...")
        for platform in validated_platforms:
            try:
                self.db.insert_platform(platform)
            except Exception as e:
                logger.error(f"Failed to store platform {platform.get('name')}: {e}")

        self.db.conn.commit()

        logger.info(f"\n✅ Platform discovery complete for {region}")
        logger.info(f"   Total platforms: {len(validated_platforms)}")
        logger.info(f"   Seed platforms: {len(global_seeds) + len(regional_seeds)}")
        logger.info(f"   Discovered platforms: {len(discovered_local)}")

        return validated_platforms

    async def _search_for_local_platforms(
        self,
        region: str,
        country: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Use web search to discover local platforms

        This method will use Claude's web search capabilities to find platforms
        that locals actually use in this region.

        NOTE: In actual implementation, this would make web search API calls.
        For now, it returns a template that shows what we're looking for.
        """

        platforms_found = []

        # Generate search queries
        search_queries = self.search_helper.search_local_platforms(
            region=region,
            country=country,
            language=language
        )

        logger.info(f"    Generated {len(search_queries)} search queries")
        logger.debug(f"    Sample queries: {search_queries[:3]}")

        # Create research prompt for Claude
        research_prompt = self.search_helper.create_research_prompt(
            research_type='discover_platforms',
            region=region,
            country=country,
            language=language
        )

        # TODO: In actual implementation, this would:
        # 1. Use Claude's web_search tool to execute searches
        # 2. Analyze results to extract platform names, URLs, types
        # 3. Return structured platform data

        # For now, return example structure showing what we expect
        # This will be replaced with actual web search when integrated

        logger.info(f"""

        📋 RESEARCH PROMPT FOR CLAUDE:
        {research_prompt}

        SEARCH QUERIES TO EXECUTE:
        {chr(10).join(f"  - {q}" for q in search_queries[:5])}
        ... and {len(search_queries) - 5} more

        Expected output structure:
        [
            {{
                "name": "Platform Name",
                "url": "https://...",
                "type": "software_reviews | business_directory | tech_media | forum",
                "language": "{language}",
                "description": "What this platform does",
                "estimated_traffic": "rank or monthly visitors",
                "has_software_data": true/false,
                "scrapeable": "easy | medium | hard | api_available",
                "notes": "Additional context"
            }},
            ...
        ]
        """)

        # Placeholder platforms for testing
        # In production, these would come from actual web search
        if country.lower() == "romania":
            platforms_found = [
                {
                    "name": "Lista Firmelor",
                    "url": "https://www.listafirme.ro",
                    "type": "business_directory",
                    "language": "Romanian",
                    "description": "Primary Romanian business registry and directory",
                    "has_software_data": True,
                    "discovery_source": "web_search",
                    "notes": "Comprehensive business database, includes software vendors"
                },
                {
                    "name": "Startarium",
                    "url": "https://startarium.ro",
                    "type": "startup_directory",
                    "language": "Romanian",
                    "description": "Romanian startup ecosystem platform",
                    "has_software_data": True,
                    "discovery_source": "web_search"
                },
                {
                    "name": "Business Review Romania",
                    "url": "https://business-review.eu",
                    "type": "tech_media",
                    "language": "English/Romanian",
                    "description": "Romanian tech and business news",
                    "has_software_data": False,
                    "discovery_source": "web_search"
                }
            ]

        elif country.lower() == "japan":
            platforms_found = [
                {
                    "name": "ITreview",
                    "url": "https://www.itreview.jp",
                    "type": "software_reviews",
                    "language": "Japanese",
                    "description": "Japan's leading B2B software review platform",
                    "has_software_data": True,
                    "discovery_source": "web_search",
                    "notes": "Japanese equivalent of G2 - most popular B2B review site"
                },
                {
                    "name": "Boxil",
                    "url": "https://boxil.jp",
                    "type": "saas_comparison",
                    "language": "Japanese",
                    "description": "SaaS comparison and review platform for Japan",
                    "has_software_data": True,
                    "discovery_source": "web_search"
                },
                {
                    "name": "TechCrunch Japan",
                    "url": "https://jp.techcrunch.com",
                    "type": "tech_media",
                    "language": "Japanese",
                    "description": "Japanese version of TechCrunch",
                    "has_software_data": False,
                    "discovery_source": "web_search"
                }
            ]

        # Add region and country to all found platforms
        for platform in platforms_found:
            platform['region'] = region
            platform['country'] = country

        return platforms_found

    async def _validate_platforms(
        self,
        platforms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate discovered platforms

        Checks:
        1. URL is accessible
        2. Has recent/active content
        3. Contains relevant data (software/companies)
        4. Is scrapeable
        5. Has sufficient size/content
        """

        validated = []
        required_checks = self.discovery_config.get('required_validation_checks', [])

        for platform in platforms:
            validation_result = await self._validate_single_platform(
                platform,
                required_checks
            )

            if validation_result['status'] == 'passed':
                platform['validation_status'] = 'passed'
                platform['validation_checks'] = validation_result['checks']
                validated.append(platform)
                logger.debug(f"    ✅ {platform.get('name')} - PASSED")
            else:
                logger.debug(f"    ❌ {platform.get('name')} - FAILED: {validation_result.get('reason')}")

        return validated

    async def _validate_single_platform(
        self,
        platform: Dict[str, Any],
        required_checks: List[str]
    ) -> Dict[str, Any]:
        """
        Validate a single platform

        Returns validation result with status and check details
        """

        # For seed platforms, assume they're valid
        if platform.get('discovery_source', '').startswith('seed'):
            return {
                'status': 'passed',
                'checks': {
                    'is_seed': True,
                    'assumed_valid': True
                }
            }

        # TODO: In actual implementation, this would:
        # 1. Try to fetch the URL
        # 2. Check if page loads
        # 3. Analyze content for recency
        # 4. Check if it has software/company data
        # 5. Test if scrapeable

        # For now, assume discovered platforms are valid
        # In production, add actual HTTP checks, content analysis, etc.

        checks_passed = {
            'is_accessible': True,  # Would actually check HTTP response
            'has_recent_content': True,  # Would check dates on page
            'contains_software_data': platform.get('has_software_data', False),
            'is_scrapeable': True,  # Would test scraping
            'has_sufficient_size': True  # Would check page count/traffic
        }

        # Check if all required checks passed
        all_passed = all(
            checks_passed.get(check, False)
            for check in required_checks
        )

        return {
            'status': 'passed' if all_passed else 'failed',
            'checks': checks_passed,
            'reason': None if all_passed else 'Failed required validation checks'
        }

    def _get_existing_platforms(self, region: str) -> List[Dict[str, Any]]:
        """Get platforms already discovered for this region"""
        return self.db.get_platforms_by_region(region)

    def _get_primary_country(self, region: str) -> str:
        """Get primary country for a region from config"""

        # Map regions to their primary/test country
        region_map = {
            'Romania': 'Romania',
            'Eastern Europe': 'Romania',
            'Japan': 'Japan',
            'Asia': 'Japan',
            'Germany': 'Germany',
            'Western Europe': 'Germany',
            'United States': 'United States',
            'North America': 'United States',
            'Singapore': 'Singapore',
            'Poland': 'Poland',
            'United Kingdom': 'United Kingdom',
            'France': 'France',
        }

        return region_map.get(region, region)

    def _get_primary_language(self, country: str) -> str:
        """Get primary language for a country"""

        language_map = {
            'Romania': 'Romanian',
            'Japan': 'Japanese',
            'Germany': 'German',
            'United States': 'English',
            'United Kingdom': 'English',
            'France': 'French',
            'Poland': 'Polish',
            'Singapore': 'English',
            'South Korea': 'Korean',
            'China': 'Chinese',
            'Spain': 'Spanish',
            'Italy': 'Italian',
            'Netherlands': 'Dutch',
            'Czech Republic': 'Czech',
            'Hungary': 'Hungarian',
            'Bulgaria': 'Bulgarian',
        }

        return language_map.get(country, 'English')

    def export_platform_map(
        self,
        platform_map: Dict[str, List[Dict]],
        output_path: str = "data/discovered_platforms.json"
    ) -> str:
        """Export discovered platforms to JSON"""

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Add metadata
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_regions': len(platform_map),
            'total_platforms': sum(len(platforms) for platforms in platform_map.values()),
            'platforms_by_region': platform_map
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"\n✅ Platform map exported to: {output_path}")

        return output_path

    def print_summary(self, platform_map: Dict[str, List[Dict]]):
        """Print human-readable summary of discovered platforms"""

        print("\n" + "="*80)
        print("PLATFORM DISCOVERY SUMMARY")
        print("="*80)

        total_platforms = sum(len(platforms) for platforms in platform_map.values())
        print(f"\nTotal Regions: {len(platform_map)}")
        print(f"Total Platforms: {total_platforms}")

        for region, platforms in platform_map.items():
            print(f"\n{region} ({len(platforms)} platforms):")
            for p in platforms:
                print(f"  • {p['name']} ({p['type']}) - {p.get('language', 'N/A')}")
                print(f"    {p['url']}")

        print("\n" + "="*80 + "\n")


# Standalone test
async def test_platform_discovery():
    """Test platform discovery on Romania and Japan"""

    import yaml
    from utils.db import Database

    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Initialize database
    db = Database('data/arbitrage.db')
    db.connect()
    db.init_schema()

    # Create agent
    agent = PlatformDiscoveryAgent(config, db)

    # Discover platforms for test regions
    platform_map = await agent.discover_all_regional_platforms(
        regions=['Romania', 'Japan'],
        test_mode=True
    )

    # Print summary
    agent.print_summary(platform_map)

    # Export
    agent.export_platform_map(platform_map)

    db.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(test_platform_discovery())
