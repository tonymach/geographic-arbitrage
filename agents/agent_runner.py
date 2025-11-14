#!/usr/bin/env python3
"""
Agent Runner - Extensions to ClaudeOrchestrator for PE-grade analysis

Adds Phases 1-3 with unit economics and financial modeling
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


class AgentRunner:
    """
    Extends ClaudeOrchestrator with PE-grade analysis phases

    This class adds the missing phases while working with existing ClaudeOrchestrator
    """

    def __init__(self, orchestrator):
        """
        Args:
            orchestrator: Instance of ClaudeOrchestrator
        """
        self.orchestrator = orchestrator
        self.prompts_dir = Path(__file__).parent / 'prompts'

    async def run_phase1_ecosystem_mapping(self, regions: List[str], categories: List[str]) -> Dict:
        """
        Phase 1: Map software ecosystems for each region + category

        For each region/category pair:
        - Search G2/Capterra for products
        - Search local platforms
        - Calculate adoption scores
        - Save to software_products table in Turso

        Returns:
            Dict mapping (region, category) -> products list
        """

        logger.info(f"🔍 Phase 1: Mapping ecosystems for {len(regions)} regions x {len(categories)} categories")

        ecosystem_map = {}
        total_products = 0

        for region in regions:
            for category in categories:
                logger.info(f"\n  Analyzing: {category} in {region}")

                # Load prompt template
                prompt = self._create_ecosystem_mapping_prompt(region, category)

                # TODO: Spawn Claude Task agent here
                # products = await self._spawn_agent(prompt)

                # For now, use placeholder
                products = await self._mock_ecosystem_research(region, category)

                # Save each product to Turso
                for product in products:
                    await self._save_product_to_turso(product)
                    total_products += 1

                ecosystem_map[(region, category)] = products
                logger.info(f"  ✅ Found {len(products)} products for {category} in {region}")

        logger.info(f"\n✅ Phase 1 complete: {total_products} products mapped")
        return ecosystem_map

    async def run_phase2_gap_detection(self, ecosystem_map: Dict) -> List[Dict]:
        """
        Phase 2: Detect arbitrage gaps

        Analyzes ecosystem_map to find where successful products in mature
        markets are missing in emerging markets.

        Returns:
            List of opportunities sorted by gap_score
        """

        logger.info(f"\n🎯 Phase 2: Detecting arbitrage gaps")

        # Load prompt template
        prompt = self._create_gap_detection_prompt(ecosystem_map)

        # TODO: Spawn Claude Task agent
        # opportunities = await self._spawn_agent(prompt)

        # For now, use placeholder
        opportunities = await self._mock_gap_detection(ecosystem_map)

        # Save each opportunity to Turso
        for opp in opportunities:
            opp_id = await self._save_opportunity_to_turso(opp)
            opp['id'] = opp_id

        logger.info(f"✅ Phase 2 complete: {len(opportunities)} gaps detected")
        return opportunities

    async def run_phase3_validation(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Phase 3: Validate opportunities with unit economics

        For each opportunity:
        - Research pain signals in target market
        - Calculate TAM
        - Calculate unit economics (ACV, CAC, LTV)
        - Build 3-year financial model
        - Assess risks and moat
        - Save to pain_signals table + update opportunities

        Returns:
            List of validated opportunities
        """

        logger.info(f"\n✅ Phase 3: Validating {len(opportunities)} opportunities")

        validated = []

        for opp in opportunities:
            logger.info(f"\n  Validating: {opp['source_product']} → {opp['target_region']}")

            # Load prompt template
            prompt = self._create_validation_prompt(opp)

            # TODO: Spawn Claude Task agent
            # validation = await self._spawn_agent(prompt)

            # For now, use placeholder
            validation = await self._mock_validation(opp)

            # Save pain signals
            for signal in validation.get('pain_signals', []):
                await self._save_pain_signal_to_turso(signal, opp['id'])

            # Update opportunity with validation data
            await self._update_opportunity_with_validation(opp['id'], validation)

            # Add to validated list if meets criteria
            if validation['recommendation'] in ['BUILD NOW', 'VALIDATE MORE']:
                validated.append({**opp, **validation})
                logger.info(f"  ✅ VALIDATED: {validation['recommendation']}")
            else:
                logger.info(f"  ❌ REJECTED: {validation['recommendation']}")

        logger.info(f"\n✅ Phase 3 complete: {len(validated)} opportunities validated")
        return validated

    # ======================
    # DATABASE SAVE METHODS
    # ======================

    async def _save_product_to_turso(self, product: Dict):
        """Save software product to Turso"""
        if not self.orchestrator.use_turso:
            logger.warning("Turso not configured, skipping save")
            return

        await self.orchestrator._init_turso()

        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.orchestrator.turso_client.execute("""
                    INSERT INTO software_products
                    (region, category, product_name, url, reviews, rating,
                     adoption_score, source_platforms, estimated_revenue, pricing,
                     target_customer, key_features, discovered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, [
                    product.get('region'),
                    product.get('category'),
                    product.get('product_name'),
                    product.get('url'),
                    product.get('reviews'),
                    product.get('rating'),
                    product.get('adoption_score'),
                    product.get('source_platforms'),
                    product.get('estimated_revenue'),
                    product.get('pricing'),
                    product.get('target_customer'),
                    product.get('key_features')
                ])
                logger.debug(f"✅ Saved product: {product['product_name']}")
                return  # Success, exit retry loop
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️  Retry {attempt + 1}/{max_retries} for {product['product_name']}: {e}")
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"❌ Failed to save product after {max_retries} attempts: {e}")

    async def _save_opportunity_to_turso(self, opp: Dict) -> int:
        """Save opportunity to Turso, return ID"""
        if not self.orchestrator.use_turso:
            logger.warning("Turso not configured, using mock ID")
            return 1  # Return mock ID

        await self.orchestrator._init_turso()

        try:
            result = await self.orchestrator.turso_client.execute("""
                INSERT INTO arbitrage_opportunities
                (source_region, source_product, source_category, source_reviews,
                 source_rating, target_region, target_competition, gap_score,
                 reasoning, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                RETURNING id
            """, [
                opp.get('source_region'),
                opp.get('source_product'),
                opp.get('source_category'),
                opp.get('source_reviews'),
                opp.get('source_rating'),
                opp.get('target_region'),
                opp.get('target_competition'),
                opp.get('gap_score'),
                opp.get('reasoning')
            ])

            opp_id = result.rows[0]['id']
            logger.debug(f"✅ Saved opportunity #{opp_id}")
            return opp_id
        except Exception as e:
            logger.error(f"❌ Failed to save opportunity: {e}")
            return 1  # Return mock ID to continue flow

    async def _save_pain_signal_to_turso(self, signal: Dict, opp_id: int):
        """Save pain signal to Turso"""
        if not self.orchestrator.use_turso:
            logger.debug("Turso not configured, skipping pain signal save")
            return

        await self.orchestrator._init_turso()

        try:
            await self.orchestrator.turso_client.execute("""
                INSERT INTO pain_signals
                (opportunity_id, region, category, source, source_url,
                 title, quote, pain_intensity, engagement_upvotes,
                 engagement_comments, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, [
                opp_id,
                signal.get('region'),
                signal.get('category'),
                signal.get('source'),
                signal.get('url'),
                signal.get('title'),
                signal.get('quote'),
                signal.get('pain_intensity'),
                signal.get('upvotes'),
                signal.get('comments', 0)
            ])
            logger.debug(f"✅ Saved pain signal from {signal['source']}")
        except Exception as e:
            logger.error(f"❌ Failed to save pain signal: {e}")

    async def _update_opportunity_with_validation(self, opp_id: int, validation: Dict):
        """Update opportunity with validation data"""
        if not self.orchestrator.use_turso:
            logger.debug("Turso not configured, skipping opportunity update")
            return

        await self.orchestrator._init_turso()

        unit_econ = validation.get('unit_economics', {})
        financial = validation.get('financial_model', {})
        exit_strat = validation.get('exit_strategy', {})
        moat = validation.get('moat', {})

        try:
            await self.orchestrator.turso_client.execute("""
                UPDATE arbitrage_opportunities
                SET
                    validated = 1,
                    opportunity_score = ?,
                    tam_estimate = ?,
                    acv = ?,
                    cac = ?,
                    ltv = ?,
                    ltv_cac_ratio = ?,
                    payback_period_months = ?,
                    gross_margin_pct = ?,
                    year_1_revenue = ?,
                    year_2_revenue = ?,
                    year_3_revenue = ?,
                    year_3_ebitda = ?,
                    exit_value_base = ?,
                    exit_value_bull = ?,
                    capital_required = ?,
                    breakeven_month = ?,
                    roi_multiple = ?,
                    moat_score = ?,
                    risk_summary = ?,
                    execution_plan = ?
                WHERE id = ?
            """, [
                validation.get('demand_score'),
                validation.get('market_size', {}).get('tam'),
                unit_econ.get('acv'),
                unit_econ.get('cac'),
                unit_econ.get('ltv'),
                unit_econ.get('ltv_cac_ratio'),
                unit_econ.get('payback_period_months'),
                unit_econ.get('gross_margin_pct'),
                financial.get('year_1_revenue'),
                financial.get('year_2_revenue'),
                financial.get('year_3_revenue'),
                financial.get('year_3_ebitda'),
                exit_strat.get('exit_value_base'),
                exit_strat.get('exit_value_bull'),
                financial.get('capital_required'),
                financial.get('breakeven_month'),
                exit_strat.get('roi_multiple'),
                moat.get('overall_score'),
                json.dumps(validation.get('risks', [])),
                validation.get('recommendation'),
                opp_id
            ])
            logger.debug(f"✅ Updated opportunity #{opp_id} with validation")
        except Exception as e:
            logger.error(f"❌ Failed to update opportunity: {e}")

    # ===================
    # PROMPT GENERATORS
    # ===================

    def _create_ecosystem_mapping_prompt(self, region: str, category: str) -> str:
        """Load and populate ecosystem mapping prompt template"""
        template_path = self.prompts_dir / 'phase1_ecosystem_mapping.txt'
        with open(template_path) as f:
            template = f.read()

        # Get local platforms for this region
        platforms = self._get_platforms_for_region(region)
        platform_list = '\n'.join([f"   - {p['name']} ({p['url']})" for p in platforms])

        # Get native language
        language = self.orchestrator._get_primary_language(region)

        return template.format(
            region=region,
            category=category,
            platforms=platform_list,
            platform_list=platform_list,
            native_language=language,
            native_language_term=f"{category} {language}"
        )

    def _create_gap_detection_prompt(self, ecosystem_map: Dict) -> str:
        """Load and populate gap detection prompt template"""
        template_path = self.prompts_dir / 'phase2_gap_detection.txt'
        with open(template_path) as f:
            template = f.read()

        # Convert tuple keys to strings for JSON serialization
        serializable_map = {}
        for (region, category), products in ecosystem_map.items():
            key = f"{region}_{category}"
            serializable_map[key] = {
                "region": region,
                "category": category,
                "products": products
            }

        # Format ecosystem data
        ecosystem_json = json.dumps(serializable_map, indent=2)

        return template.format(ecosystem_data=ecosystem_json)

    def _create_validation_prompt(self, opportunity: Dict) -> str:
        """Load and populate validation prompt template"""
        template_path = self.prompts_dir / 'phase3_validation.txt'
        with open(template_path) as f:
            template = f.read()

        # Get local platforms for target region
        platforms = self._get_platforms_for_region(opportunity['target_region'])
        platform_list = '\n'.join([f"   - {p['name']} ({p['url']})" for p in platforms])

        return template.format(
            opportunity_data=json.dumps(opportunity, indent=2),
            opportunity_id=opportunity.get('id'),
            target_region=opportunity['target_region'],
            category=opportunity['source_category'],
            source_product=opportunity['source_product'],
            source_pricing=opportunity.get('source_pricing', '$299/month'),
            local_platforms=platform_list,
            native_language=self.orchestrator._get_primary_language(opportunity['target_region'])
        )

    def _get_platforms_for_region(self, region: str) -> List[Dict]:
        """Get local platforms for a region from orchestrator's data"""
        # This would query from Turso or use cached data
        # For now, return empty list
        return []

    # ================
    # MOCK FUNCTIONS (Replace with real Task agents)
    # ================

    async def _mock_ecosystem_research(self, region: str, category: str) -> List[Dict]:
        """Mock ecosystem research - REPLACE WITH TASK AGENT"""
        await asyncio.sleep(0.1)  # Simulate research

        # Return mock data
        if "Poland" in region and "Construction" in category:
            return [
                {
                    "region": region,
                    "category": category,
                    "product_name": "BudowaPlus",
                    "url": "https://budowaplus.pl",
                    "reviews": 12,
                    "rating": 3.5,
                    "adoption_score": 15.0,
                    "source_platforms": "G2,Local forums",
                    "estimated_revenue": "$500k ARR",
                    "pricing": "$89/month",
                    "target_customer": "Small construction firms",
                    "key_features": "Project tracking, Basic docs"
                }
            ]
        return []

    async def _mock_gap_detection(self, ecosystem_map: Dict) -> List[Dict]:
        """Mock gap detection - REPLACE WITH TASK AGENT"""
        await asyncio.sleep(0.1)

        return [
            {
                "source_region": "United States",
                "source_product": "Procore",
                "source_category": "Construction Management",
                "source_reviews": 1200,
                "source_rating": 4.7,
                "source_pricing": "$375/month",
                "target_region": "Poland",
                "target_competition": "2 products, 18 total reviews",
                "gap_score": 9.2,
                "reasoning": "Massive gap between US market maturity and Polish offerings"
            }
        ]

    async def _mock_validation(self, opp: Dict) -> Dict:
        """Mock validation - REPLACE WITH TASK AGENT"""
        await asyncio.sleep(0.1)

        return {
            "validation_status": "VALIDATED",
            "demand_score": 8.9,
            "pain_signals": [
                {
                    "region": opp['target_region'],
                    "category": opp['source_category'],
                    "source": "Wykop.pl",
                    "url": "https://wykop.pl/link/example",
                    "title": "Polish alternative to Procore?",
                    "quote": "Does anyone know a Polish alternative to Procore?",
                    "upvotes": 47,
                    "comments": 23,
                    "pain_intensity": 8.5
                }
            ],
            "market_size": {
                "tam": "$45M",
                "target_customers": 15000,
                "avg_contract_value": "$3000"
            },
            "unit_economics": {
                "acv": 3000,
                "cac": 900,
                "ltv": 12750,
                "ltv_cac_ratio": 14.2,
                "payback_period_months": 3.6,
                "gross_margin_pct": 85
            },
            "financial_model": {
                "year_1_revenue": 90000,
                "year_2_revenue": 360000,
                "year_3_revenue": 1080000,
                "year_3_ebitda": 250000,
                "capital_required": 120000,
                "breakeven_month": 18
            },
            "exit_strategy": {
                "exit_value_base": 5400000,
                "exit_value_bull": 12000000,
                "roi_multiple": 45
            },
            "moat": {
                "network_effects": 7,
                "switching_costs": 9,
                "regulatory": 6,
                "brand": 5,
                "overall_score": 6.75
            },
            "risks": [
                {
                    "risk": "Procore enters Poland",
                    "probability": "medium",
                    "impact": "high",
                    "mitigation": "Speed, local focus, pricing"
                }
            ],
            "recommendation": "BUILD NOW",
            "confidence": "high"
        }
