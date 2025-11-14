"""
Cross Reference Agent - Phase 3

Finds arbitrage opportunities by comparing software ecosystems across regions.

Detects gaps where:
- Product is HUGE in Region A (high reviews, adoption)
- Product is MISSING or WEAK in Region B (low/no competition)
- But Region B shows NEED for this category (companies, contracts, pain signals)

Example:
- Coworking software dominates UK (Nexudus: 847 reviews)
- Romania has minimal coworking software (<3 options, 12 reviews total)
- But Romania opened 47 coworking spaces in last 2 years
- = OPPORTUNITY
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import Database

logger = logging.getLogger(__name__)


class CrossReferenceAgent:
    """
    Compares software ecosystems across regions to find gaps

    This is where the arbitrage magic happens
    """

    def __init__(self, config: Dict[str, Any], db: Database):
        self.config = config
        self.db = db

        # Gap detection settings
        self.gap_config = config.get('gap_detection', {})
        self.min_source_reviews = self.gap_config.get('min_source_reviews', 100)
        self.min_gap_score = self.gap_config.get('min_gap_score', 6.0)
        self.max_target_competition = self.gap_config.get('max_target_competition_level', 3)

        logger.info(f"Cross Reference Agent initialized")
        logger.info(f"  Min source reviews: {self.min_source_reviews}")
        logger.info(f"  Min gap score: {self.min_gap_score}")

    async def find_all_opportunities(
        self,
        ecosystem_map: Dict[str, Dict]
    ) -> List[Dict[str, Any]]:
        """
        Find arbitrage opportunities across all region pairs

        Compares every region against every other region to find gaps
        """

        logger.info(f"\n{'='*80}")
        logger.info(f"Finding arbitrage opportunities across {len(ecosystem_map)} regions")
        logger.info(f"{'='*80}\n")

        opportunities = []
        regions = list(ecosystem_map.keys())

        # Compare every region pair
        comparisons = []
        for i, source_region in enumerate(regions):
            for target_region in regions[i+1:]:
                comparisons.append((source_region, target_region))

        logger.info(f"Total region pair comparisons: {len(comparisons)}")

        # Find gaps for each pair in parallel
        tasks = []
        for source_region, target_region in comparisons:
            task = self._find_gaps_between_regions(
                source_region=source_region,
                source_ecosystem=ecosystem_map[source_region],
                target_region=target_region,
                target_ecosystem=ecosystem_map[target_region]
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect all opportunities
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Failed to find gaps: {result}")
            elif result:
                opportunities.extend(result)

        # Filter by minimum gap score
        opportunities = [
            opp for opp in opportunities
            if opp.get('gap_score', 0) >= self.min_gap_score
        ]

        # Calculate opportunity scores
        for opp in opportunities:
            opp['opportunity_score'] = self._calculate_opportunity_score(opp)

        # Sort by opportunity score
        opportunities.sort(key=lambda o: o.get('opportunity_score', 0), reverse=True)

        logger.info(f"\n✅ Found {len(opportunities)} opportunities (gap_score >= {self.min_gap_score})")

        return opportunities

    async def _find_gaps_between_regions(
        self,
        source_region: str,
        source_ecosystem: Dict[str, Any],
        target_region: str,
        target_ecosystem: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Find gaps between two specific regions

        Logic:
        1. For each category in source region, find top products
        2. Check if target region has similar products
        3. If source has strong adoption but target has weak adoption = gap
        4. Calculate gap metrics
        """

        logger.info(f"  Comparing: {source_region} → {target_region}")

        gaps = []

        source_products = source_ecosystem.get('popular_products', {})
        target_products = target_ecosystem.get('popular_products', {})

        # Compare each category
        for category, source_category_products in source_products.items():
            target_category_products = target_products.get(category, [])

            # Find top products in source
            top_source_products = sorted(
                source_category_products,
                key=lambda p: p.get('review_count', 0),
                reverse=True
            )[:3]  # Top 3 in source

            # Check each top source product
            for source_product in top_source_products:
                # Skip if source product doesn't meet minimum reviews
                if source_product.get('review_count', 0) < self.min_source_reviews:
                    continue

                # Check if significant gap exists
                gap = self._detect_gap(
                    source_region=source_region,
                    source_product=source_product,
                    target_region=target_region,
                    target_products=target_category_products,
                    category=category
                )

                if gap and gap.get('gap_score', 0) >= self.min_gap_score:
                    gaps.append(gap)
                    logger.info(f"    🎯 GAP FOUND: {category} - {source_product['name']}")
                    logger.info(f"       Gap score: {gap['gap_score']}")

        logger.info(f"    Found {len(gaps)} gaps")

        return gaps

    def _detect_gap(
        self,
        source_region: str,
        source_product: Dict[str, Any],
        target_region: str,
        target_products: List[Dict[str, Any]],
        category: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if a gap exists between source product and target region

        Returns gap dict if gap exists, None otherwise
        """

        source_reviews = source_product.get('review_count', 0)
        source_rating = source_product.get('rating', 0)
        source_adoption = source_product.get('adoption_score', 0)

        # Find competitors in target region
        target_competitors = sorted(
            target_products,
            key=lambda p: p.get('review_count', 0),
            reverse=True
        )[:5]  # Top 5 competitors in target

        # Calculate target competition metrics
        if target_competitors:
            target_max_reviews = max(p.get('review_count', 0) for p in target_competitors)
            target_avg_rating = sum(p.get('rating', 0) for p in target_competitors) / len(target_competitors)
            target_total_reviews = sum(p.get('review_count', 0) for p in target_competitors)
        else:
            target_max_reviews = 0
            target_avg_rating = 0
            target_total_reviews = 0

        # Calculate gap metrics
        review_count_gap = source_reviews - target_max_reviews
        rating_gap = source_rating - target_avg_rating

        # Determine competition level (0-5 scale)
        if len(target_competitors) == 0:
            competition_level = 0
        elif target_max_reviews < 50:
            competition_level = 1
        elif target_max_reviews < 200:
            competition_level = 2
        elif target_max_reviews < 500:
            competition_level = 3
        elif target_max_reviews < 1000:
            competition_level = 4
        else:
            competition_level = 5

        # Calculate gap score (0-10)
        gap_score = self._calculate_gap_score(
            source_reviews=source_reviews,
            target_max_reviews=target_max_reviews,
            competition_level=competition_level,
            source_adoption=source_adoption
        )

        # Only consider significant gaps
        if gap_score < self.min_gap_score:
            return None

        # Check if competition is low enough
        if competition_level > self.max_target_competition:
            logger.debug(f"      Skipping {source_product['name']} - too much competition ({competition_level})")
            return None

        # Create gap record
        gap = {
            # Source (where it's successful)
            'source_region': source_region,
            'source_product_name': source_product['name'],
            'source_category': category,
            'source_adoption': int(source_reviews),
            'source_reviews': int(source_reviews),
            'source_rating': round(source_rating, 2),
            'source_pricing': source_product.get('pricing'),

            # Target (where it's missing/weak)
            'target_region': target_region,
            'target_competitors': [
                {
                    'name': p['name'],
                    'reviews': p.get('review_count', 0),
                    'rating': p.get('rating', 0)
                }
                for p in target_competitors[:3]  # Top 3
            ],
            'target_competition_level': competition_level,
            'target_best_alternative': target_competitors[0]['name'] if target_competitors else None,

            # Gap metrics
            'gap_score': round(gap_score, 2),
            'review_count_gap': int(review_count_gap),
            'rating_gap': round(rating_gap, 2),
            'competition_gap': round(5 - competition_level, 2),  # Higher = less competition

            # Validation placeholders (will be filled in Phase 4)
            'need_validated': False,
            'company_need_score': None,
            'contract_validation': {},
            'pain_signals': {},

            # Opportunity metrics (will be calculated)
            'estimated_tam': None,
            'opportunity_score': None,

            # Timing insight
            'market_maturity': self._infer_market_maturity(target_total_reviews),
            'digitalization_lag_years': None,  # Will be inferred
            'market_readiness': 'unknown',

            # Metadata
            'confidence_score': 0.6,  # Base confidence, will be adjusted with validation
            'created_at': datetime.now().isoformat()
        }

        # Generate insight narrative
        gap['insight_narrative'] = self._generate_insight_narrative(gap)

        return gap

    def _calculate_gap_score(
        self,
        source_reviews: int,
        target_max_reviews: int,
        competition_level: int,
        source_adoption: float
    ) -> float:
        """
        Calculate gap score (0-10)

        Factors:
        - Review count difference
        - Competition level
        - Source adoption strength
        """

        weights = self.gap_config.get('weights', {})

        # Review count gap component (0-10)
        if target_max_reviews == 0:
            review_gap_component = 10
        else:
            ratio = source_reviews / max(target_max_reviews, 1)
            review_gap_component = min(10, ratio * 2)

        # Competition gap component (0-10)
        # Less competition = higher score
        competition_component = (5 - competition_level) * 2  # 0-10

        # Source strength component (0-10)
        source_component = min(10, source_adoption)

        # Weighted average
        score = (
            review_gap_component * weights.get('review_count_gap', 0.25) +
            competition_component * weights.get('competition_gap', 0.30) +
            source_component * weights.get('review_count_gap', 0.25)  # Using review count gap weight
        ) * 10  # Scale to 0-10

        return min(10, max(0, score))

    def _calculate_opportunity_score(self, opportunity: Dict[str, Any]) -> float:
        """
        Calculate overall opportunity score (0-10)

        Combines:
        - Gap score
        - Validation signals
        - Market readiness
        """

        gap_score = opportunity.get('gap_score', 0)
        competition_gap = opportunity.get('competition_gap', 0)
        source_reviews = opportunity.get('source_reviews', 0)

        # Base score from gap
        score = gap_score * 0.6

        # Bonus for high source adoption
        if source_reviews > 500:
            score += 1.5
        elif source_reviews > 200:
            score += 1.0

        # Bonus for low competition
        if competition_gap >= 4:
            score += 1.5
        elif competition_gap >= 3:
            score += 1.0

        # Would add validation bonuses in Phase 4:
        # if opportunity.get('need_validated'):
        #     score += 2.0

        return min(10, round(score, 2))

    def _infer_market_maturity(self, total_reviews: int) -> str:
        """
        Infer market maturity based on review counts

        emerging: <100 reviews total
        growing: 100-500 reviews
        mature: >500 reviews
        """

        if total_reviews < 100:
            return "emerging"
        elif total_reviews < 500:
            return "growing"
        else:
            return "mature"

    def _generate_insight_narrative(self, gap: Dict[str, Any]) -> str:
        """Generate human-readable narrative about this opportunity"""

        narrative = (
            f"{gap['source_product_name']} dominates {gap['source_category']} in {gap['source_region']} "
            f"with {gap['source_reviews']} reviews and {gap['source_rating']}/5 rating. "
            f"{gap['target_region']} has "
        )

        if gap['target_competition_level'] == 0:
            narrative += "NO existing solutions. "
        elif gap['target_competition_level'] <= 2:
            narrative += f"minimal competition (best alternative: {gap['target_best_alternative']} with limited adoption). "
        else:
            narrative += f"some competition but significant gap remains. "

        narrative += f"Market appears {gap['market_maturity']}. "

        return narrative

    async def validate_opportunities(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate opportunities with additional signals

        Phase 4:
        - Government contracts
        - Pain signals (Reddit, forums)
        - Company needs
        - Job market signals

        TODO: Implement validation logic
        """

        logger.info(f"\nValidating {len(opportunities)} opportunities...")

        # Placeholder - would add validation logic here
        # For now, just mark as validated if gap score is high

        for opp in opportunities:
            if opp['gap_score'] >= 8.0:
                opp['need_validated'] = True
                opp['company_need_score'] = 7.5
                opp['confidence_score'] = 0.8

        return opportunities

    def export_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        output_path: str = "data/results/opportunities.json"
    ) -> str:
        """Export opportunities to JSON"""

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_opportunities': len(opportunities),
            'top_10': opportunities[:10],
            'all_opportunities': opportunities
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"\n✅ Opportunities exported to: {output_path}")

        # Also export human-readable version
        txt_path = output_path.replace('.json', '.txt')
        self._export_human_readable(opportunities, txt_path)

        return output_path

    def _export_human_readable(
        self,
        opportunities: List[Dict[str, Any]],
        output_path: str
    ):
        """Export human-readable summary"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("GEOGRAPHIC ARBITRAGE OPPORTUNITIES\n")
            f.write("="*80 + "\n\n")

            f.write(f"Total opportunities found: {len(opportunities)}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("TOP 10 OPPORTUNITIES:\n")
            f.write("="*80 + "\n\n")

            for i, opp in enumerate(opportunities[:10], 1):
                f.write(f"{i}. {opp['source_product_name']} - {opp['source_category']}\n")
                f.write(f"   {opp['source_region']} → {opp['target_region']}\n")
                f.write(f"   Opportunity Score: {opp.get('opportunity_score', 0)}/10\n")
                f.write(f"   Gap Score: {opp['gap_score']}/10\n")
                f.write(f"   Source: {opp['source_reviews']} reviews, {opp['source_rating']}/5\n")
                f.write(f"   Target Competition: Level {opp['target_competition_level']}/5\n")
                f.write(f"   Market: {opp['market_maturity']}\n")
                f.write(f"   {opp['insight_narrative']}\n\n")

        logger.info(f"Human-readable summary exported to: {output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Cross Reference Agent ready")
