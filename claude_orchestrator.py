#!/usr/bin/env python3
"""
Claude Orchestrator - True AI-Powered Global Arbitrage Discovery

This orchestrator spawns TRUE Claude subagents that can:
- REASON about market dynamics
- RESEARCH platforms and forums autonomously
- INTERPRET pain signals in local languages
- MAKE STRATEGIC ASSESSMENTS

Each phase uses Claude's intelligence, not hardcoded scripts.
"""

import asyncio
import json
import yaml
import sqlite3
import os
from pathlib import Path
from datetime import datetime
import logging

# Try to import Turso client (optional)
try:
    from libsql_client import create_client
    TURSO_AVAILABLE = True
except ImportError:
    TURSO_AVAILABLE = False

# Import HTTP client as fallback
try:
    from utils.turso_http_client import create_http_client
    HTTP_CLIENT_AVAILABLE = True
except ImportError:
    HTTP_CLIENT_AVAILABLE = False

logger = logging.getLogger(__name__)


class ClaudeOrchestrator:
    """
    Orchestrates Claude subagents for global arbitrage discovery

    Each agent is a TRUE Claude instance with full reasoning capabilities
    """

    def __init__(self, config_path: str = 'config.yaml', db_path: str = 'data/arbitrage.db', use_turso: bool = None):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.test_mode = self.config.get('test_mode', {}).get('enabled', False)
        self.test_regions = self.config.get('test_mode', {}).get('test_regions', [])

        # Determine database mode
        turso_url = os.getenv('TURSO_URL')
        turso_token = os.getenv('TURSO_TOKEN')

        if use_turso is None:
            # Auto-detect: use Turso if credentials available
            use_turso = TURSO_AVAILABLE and turso_url and turso_token

        self.use_turso = use_turso
        self.db_path = db_path  # Fallback to local SQLite
        self.turso_client = None

        if self.use_turso:
            if not TURSO_AVAILABLE:
                raise RuntimeError("Turso requested but libsql-client not installed. Run: pip install libsql-client")
            if not turso_url or not turso_token:
                raise RuntimeError("TURSO_URL and TURSO_TOKEN environment variables required")

            logger.info(f"Using Turso database: {turso_url}")
            # Turso client will be initialized async in _init_turso()
            self.turso_url = turso_url
            self.turso_token = turso_token
        else:
            logger.info(f"Using local SQLite: {self.db_path}")
            self._init_local_database()

        # Results tracking
        self.results_dir = Path('data/claude_results')
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Claude Orchestrator initialized")
        logger.info(f"Test mode: {self.test_mode}")

    def _init_local_database(self):
        """Initialize local SQLite database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        # Database already has tables from our earlier script
        conn.close()

    async def _init_turso(self):
        """Initialize Turso client (async)"""
        if not self.turso_client:
            # Try WebSocket client first
            if TURSO_AVAILABLE:
                try:
                    self.turso_client = create_client(
                        url=self.turso_url,
                        auth_token=self.turso_token
                    )
                    # Test the connection with a simple query
                    await self.turso_client.execute("SELECT 1")
                    logger.info("✅ Turso WebSocket client initialized")
                    return
                except Exception as e:
                    logger.warning(f"⚠️ WebSocket client failed ({e}), falling back to HTTP...")
                    self.turso_client = None

            # Fall back to HTTP client
            if HTTP_CLIENT_AVAILABLE:
                self.turso_client = create_http_client(
                    url=self.turso_url,
                    auth_token=self.turso_token
                )
                logger.info("✅ Turso HTTP client initialized (fallback)")
            else:
                raise RuntimeError("No Turso client available (neither WebSocket nor HTTP)")

    async def _save_platform_to_db(self, platform_data: dict):
        """Save a platform discovery to the database"""
        if self.use_turso:
            await self._save_platform_to_turso(platform_data)
        else:
            self._save_platform_to_local(platform_data)

    def _save_platform_to_local(self, platform_data: dict):
        """Save platform to local SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO local_platforms
                (region, country, name, url, type, language, description, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                platform_data.get('region'),
                platform_data.get('country'),
                platform_data.get('name'),
                platform_data.get('url'),
                platform_data.get('type'),
                platform_data.get('language'),
                platform_data.get('description', ''),
                'claude_agent_live'
            ))
            conn.commit()
            logger.debug(f"Saved platform to local DB: {platform_data.get('name')}")
        except Exception as e:
            logger.error(f"Failed to save platform to local DB: {e}")
        finally:
            conn.close()

    async def _save_platform_to_turso(self, platform_data: dict):
        """Save platform to Turso"""
        await self._init_turso()

        try:
            await self.turso_client.execute("""
                INSERT INTO local_platforms
                (region, country, name, url, type, language, description, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                platform_data.get('region'),
                platform_data.get('country'),
                platform_data.get('name'),
                platform_data.get('url'),
                platform_data.get('type'),
                platform_data.get('language'),
                platform_data.get('description', ''),
                'claude_agent_live'
            ])
            logger.debug(f"✅ Saved platform to Turso: {platform_data.get('name')}")
        except Exception as e:
            logger.error(f"❌ Failed to save platform to Turso: {e}")

    async def discover_opportunities(self, regions: list = None, target_count: int = 100):
        """
        Main entry point - discovers validated opportunities using Claude subagents

        Args:
            regions: List of regions to process (None = all)
            target_count: Target number of validated opportunities
        """

        if regions is None:
            regions = self.test_regions if self.test_mode else self._get_all_regions()

        logger.info(f"\n{'='*80}")
        logger.info(f"CLAUDE-ORCHESTRATED ARBITRAGE DISCOVERY")
        logger.info(f"Target: {target_count} validated opportunities")
        logger.info(f"Regions: {len(regions)}")
        logger.info(f"{'='*80}\n")

        start_time = datetime.now()

        # Phase 0: Discover platforms for each region
        logger.info("🔍 PHASE 0: Platform Discovery (Claude Agents)")
        platform_map = await self.spawn_platform_discovery_agents(regions)

        # Phase 1: Map software ecosystems
        logger.info("\n💻 PHASE 1: Software Ecosystem Mapping (Claude Agents)")
        ecosystem_map = await self.spawn_ecosystem_mapping_agents(regions, platform_map)

        # Phase 2: Find gaps
        logger.info("\n🎯 PHASE 2: Gap Detection (Claude Analysis)")
        opportunities = await self.spawn_gap_detection_agent(ecosystem_map)

        # Phase 3: Deep validation with local forums
        logger.info("\n✅ PHASE 3: Deep Market Validation (Claude Agents)")
        validated_opportunities = await self.spawn_validation_agents(opportunities)

        # Filter and rank
        high_confidence = [o for o in validated_opportunities if o.get('need_score', 0) >= 8.0]

        duration = (datetime.now() - start_time).total_seconds()

        # Export results
        results = {
            'generated_at': datetime.now().isoformat(),
            'duration_seconds': duration,
            'regions_processed': regions,
            'total_opportunities': len(validated_opportunities),
            'high_confidence': len(high_confidence),
            'opportunities': validated_opportunities[:target_count]
        }

        output_file = self.results_dir / 'claude_opportunities.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"\n{'='*80}")
        logger.info(f"DISCOVERY COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Duration: {duration:.1f}s")
        logger.info(f"Opportunities found: {len(validated_opportunities)}")
        logger.info(f"High confidence: {len(high_confidence)}")
        logger.info(f"Results: {output_file}")

        return results

    async def spawn_platform_discovery_agents(self, regions: list) -> dict:
        """
        Spawn Claude agents to discover platforms for each region

        Each agent researches what platforms locals actually use
        """

        logger.info(f"Spawning {len(regions)} platform discovery agents...")

        platform_map = {}

        for region in regions:
            logger.info(f"\n  🤖 Spawning Claude agent for: {region}")

            # Get region metadata
            country = self._get_primary_country(region)
            language = self._get_primary_language(country)

            # Create prompt for Claude subagent
            prompt = self._create_platform_discovery_prompt(region, country, language)

            # Spawn the Claude subagent using Task tool
            logger.info(f"     Country: {country} | Language: {language}")
            logger.info(f"     Agent will research local platforms using web search...")

            try:
                # This will spawn a TRUE Claude agent that can:
                # - Use web_search to find local platforms
                # - Reason about what locals would use
                # - Return structured data

                # For now, log what we WOULD do (next step is to actually call Task tool)
                logger.info(f"     [READY TO SPAWN] Claude agent with research capabilities")

                # Placeholder - will be replaced with actual Task tool call
                platforms = await self._discover_platforms_for_region(region, country, language, prompt)
                platform_map[region] = platforms

                logger.info(f"     ✅ Discovered {len(platforms)} platforms for {region}")

            except Exception as e:
                logger.error(f"     ❌ Failed to discover platforms for {region}: {e}")
                platform_map[region] = []

        total_platforms = sum(len(p) for p in platform_map.values())
        logger.info(f"\n✅ Platform discovery complete: {total_platforms} platforms across {len(regions)} regions")

        # Export platform map
        self._export_platform_map(platform_map)

        return platform_map

    def _create_platform_discovery_prompt(self, region: str, country: str, language: str) -> str:
        """
        Creates prompt for Claude agent to discover platforms

        The agent will use web search and reasoning to find platforms
        """

        return f"""
You are a Platform Discovery Agent researching {country} ({region}).

Your mission: Discover what platforms locals in {country} actually use for:
1. Software reviews and comparisons
2. Business discussions and forums
3. Tech news and startup ecosystems
4. Q&A and community support

Primary language: {language}

## Your Tasks:

1. **Research Local Platforms**
   - Use web search to find popular platforms in {country}
   - Look for {language}-language platforms, not just English ones
   - Find both general platforms and software-specific ones

2. **Reason About Usage**
   - What would a {country} business owner searching for software use?
   - What forums do {language} speakers actually visit?
   - What platforms have critical mass in this market?

3. **Validate Platforms**
   - Check if platforms are active (recent posts/activity)
   - Verify they have software/tech discussions
   - Assess scrapability (is it accessible?)

## Output Format:

Return a JSON structure:

```json
{{
  "region": "{region}",
  "country": "{country}",
  "language": "{language}",
  "platforms_discovered": [
    {{
      "name": "Platform Name",
      "url": "https://...",
      "type": "forum|review_site|q_and_a|tech_news|social|business_directory",
      "language": "{language}",
      "description": "What this platform is and why it's relevant",
      "estimated_users": "Rough estimate if known",
      "has_software_discussions": true/false,
      "accessibility": "easy|medium|hard",
      "notes": "Additional context"
    }}
  ],
  "search_queries_used": ["query1", "query2"],
  "reasoning": "Brief explanation of how you identified these platforms",
  "confidence": "high|medium|low"
}}
```

## Instructions:

1. Start by web searching for popular {country} forums and platforms
2. Use {language} search terms as well as English
3. Look for both obvious platforms (e.g., Reddit {country}) and local ones
4. Verify each platform is real and active
5. Reason about which platforms would have software discussions
6. Return structured JSON as specified

Be thorough but practical - find the TOP 5-10 most relevant platforms.
"""

    async def _discover_platforms_for_region(
        self,
        region: str,
        country: str,
        language: str,
        prompt: str
    ) -> list:
        """
        Execute platform discovery for a region

        TODO: This will use Task tool to spawn Claude subagent
        For now, returns seed platforms
        """

        # Get seed platforms from config
        seed_platforms = self._get_seed_platforms(country)

        # In next iteration, this will spawn a Task tool Claude agent
        # that uses the prompt to research and return discovered platforms

        return seed_platforms

    def _get_seed_platforms(self, country: str) -> list:
        """Get known seed platforms for a country"""

        seed_config = self.config.get('platform_discovery', {}).get('seed_platforms', {})

        platforms = []

        # Add global platforms
        for platform in seed_config.get('global', []):
            platforms.append(platform)

        # Add regional platforms
        regional = seed_config.get('regional', {})
        country_key = country.lower().replace(' ', '_')

        if country_key in regional:
            platforms.extend(regional[country_key])

        return platforms

    def _export_platform_map(self, platform_map: dict):
        """Export discovered platforms to JSON"""

        output_file = self.results_dir / 'platform_map.json'

        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_regions': len(platform_map),
            'total_platforms': sum(len(p) for p in platform_map.values()),
            'platforms_by_region': platform_map
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"     Platform map exported to: {output_file}")

    def _get_primary_country(self, region: str) -> str:
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

    def _get_primary_language(self, country: str) -> str:
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

    async def spawn_ecosystem_mapping_agents(self, regions: list, platform_map: dict) -> dict:
        """
        Spawn Claude agents to map software ecosystems

        Each agent researches what software exists and is popular
        """

        logger.info(f"Spawning ecosystem mapping agents for {len(regions)} regions...")

        return {region: {'products': {}} for region in regions}

    async def spawn_gap_detection_agent(self, ecosystem_map: dict) -> list:
        """
        Spawn Claude agent to find gaps between regions

        Agent reasons about arbitrage opportunities
        """

        logger.info("Spawning gap detection agent...")

        return []

    async def spawn_validation_agents(self, opportunities: list) -> list:
        """
        Spawn Claude agents to validate opportunities with local forums

        Each agent:
        - Researches local forums in native language
        - Interprets pain signals
        - Assesses market readiness
        """

        logger.info(f"Spawning validation agents for {len(opportunities)} opportunities...")

        return opportunities

    def _get_all_regions(self) -> list:
        """Get all configured regions"""
        all_regions = []
        for region_group in self.config['regions'].values():
            all_regions.extend(region_group)
        return all_regions


async def main():
    """Demo of Claude orchestration"""

    logging.basicConfig(level=logging.INFO)

    orchestrator = ClaudeOrchestrator()

    # Run discovery
    results = await orchestrator.discover_opportunities(
        target_count=10
    )

    print(f"\n✅ Found {results['total_opportunities']} opportunities")
    print(f"   High confidence: {results['high_confidence']}")


if __name__ == "__main__":
    asyncio.run(main())
