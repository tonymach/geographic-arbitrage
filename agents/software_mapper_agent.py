"""
Software Mapper Agent - Phase 2

Maps software ecosystems per region to understand:
1. What software products exist and are popular
2. What categories have strong adoption
3. What gaps exist in each region's ecosystem
4. What the competitive landscape looks like

Uses BOTH global platforms (G2, Capterra) AND local platforms
discovered in Phase 0.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import Database
from utils.web_search_helper import WebSearchHelper

logger = logging.getLogger(__name__)


class SoftwareMapperAgent:
    """
    Maps software ecosystems per region

    Creates a "tapestry" of software showing:
    - What products dominate each category
    - How many reviews/users each has
    - Pricing levels
    - Adoption scores
    """

    def __init__(self, config: Dict[str, Any], db: Database):
        self.config = config
        self.db = db
        self.search_helper = WebSearchHelper()

        self.categories = config.get('categories', [])
        self.test_mode = config.get('test_mode', {}).get('enabled', False)
        self.max_products = config.get('test_mode', {}).get('max_products_per_category', 20)

        logger.info(f"Software Mapper Agent initialized ({len(self.categories)} categories)")

    async def map_all_ecosystems(
        self,
        regions: List[str],
        platform_map: Dict[str, List[Dict]],
        company_map: Dict[str, List[Dict]]
    ) -> Dict[str, Dict]:
        """
        Map software ecosystems for all regions

        Returns: {region: {
            'popular_products': {category: [products]},
            'company_tech_stacks': {...},
            'ecosystem_stats': {...}
        }}
        """

        logger.info(f"Starting software ecosystem mapping for {len(regions)} regions")

        tasks = []
        for region in regions:
            platforms = platform_map.get(region, [])
            companies = company_map.get(region, [])
            task = self.map_software_ecosystem(region, platforms, companies)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        ecosystem_map = {}
        for region, result in zip(regions, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to map software for {region}: {result}")
                ecosystem_map[region] = {}
            else:
                ecosystem_map[region] = result
                total_products = sum(
                    len(products)
                    for products in result.get('popular_products', {}).values()
                )
                logger.info(f"Mapped {total_products} products for {region}")

        return ecosystem_map

    async def map_software_ecosystem(
        self,
        region: str,
        platforms: List[Dict[str, Any]],
        companies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Map software ecosystem for a single region

        Steps:
        1. For each category, find popular products
        2. Scrape from global platforms (G2, Capterra) filtered by region
        3. Scrape from local platforms
        4. Analyze company tech stacks
        5. Calculate adoption scores
        6. Store in database
        """

        logger.info(f"\n{'='*80}")
        logger.info(f"Mapping software ecosystem for: {region}")
        logger.info(f"{'='*80}\n")

        country = self._get_primary_country(region)
        language = self._get_primary_language(country)

        ecosystem = {
            'region': region,
            'popular_products': {},
            'company_tech_stacks': {},
            'ecosystem_stats': {}
        }

        # Limit categories in test mode
        categories = self.categories
        if self.test_mode:
            # Include diverse categories that demonstrate gaps across regions
            categories = [
                "Project Management",
                "CRM & Sales",
                "HR & Payroll",
                "Accounting & Finance",
                "Coworking & Space Management",
                "Construction Management",
                "Manufacturing & Supply Chain",
                "Healthcare Management"
            ]
            logger.info(f"  TEST MODE: Testing {len(categories)} categories")

        # Map products for each category
        for category in categories:
            logger.info(f"  Mapping category: {category}")

            products = await self._find_products_in_category(
                region=region,
                country=country,
                category=category,
                platforms=platforms,
                language=language
            )

            ecosystem['popular_products'][category] = products

            logger.info(f"    Found {len(products)} products")

        # Analyze company tech stacks (if companies provided)
        if companies:
            logger.info(f"  Analyzing tech stacks from {len(companies)} companies...")
            ecosystem['company_tech_stacks'] = await self._analyze_company_tech_stacks(
                companies, region
            )

        # Calculate ecosystem stats
        ecosystem['ecosystem_stats'] = self._calculate_ecosystem_stats(ecosystem)

        # Store products in database
        total_products = sum(len(products) for products in ecosystem['popular_products'].values())
        logger.info(f"  Storing {total_products} products...")

        for category, products in ecosystem['popular_products'].items():
            for product in products:
                try:
                    self.db.insert_product(product)
                except Exception as e:
                    logger.error(f"Failed to store product {product.get('name')}: {e}")

        self.db.conn.commit()

        logger.info(f"\n✅ Software ecosystem mapping complete for {region}")
        logger.info(f"   Total products: {total_products}")
        logger.info(f"   Categories mapped: {len(ecosystem['popular_products'])}")

        return ecosystem

    async def _find_products_in_category(
        self,
        region: str,
        country: str,
        category: str,
        platforms: List[Dict[str, Any]],
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Find popular products in a category for this region

        Searches:
        1. Global platforms (G2, Capterra) with region filter
        2. Local platforms discovered in Phase 0
        3. Web search for popular tools
        """

        products = []

        # Step 1: Search on global platforms
        # TODO: In actual implementation, scrape G2/Capterra with region filter
        global_products = await self._search_global_platforms(
            region, country, category, language
        )
        products.extend(global_products)

        # Step 2: Search on local platforms
        local_products = await self._search_local_platforms(
            platforms, category, region
        )
        products.extend(local_products)

        # Step 3: Deduplicate
        products = self._deduplicate_products(products)

        # Step 4: Calculate adoption scores
        for product in products:
            product['adoption_score'] = self._calculate_adoption_score(product)

        # Sort by adoption score
        products.sort(key=lambda p: p.get('adoption_score', 0), reverse=True)

        # Limit in test mode
        if self.test_mode and len(products) > self.max_products:
            products = products[:self.max_products]

        return products

    async def _search_global_platforms(
        self,
        region: str,
        country: str,
        category: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Search global platforms (G2, Capterra) filtered by region

        TODO: Actual implementation would scrape these platforms
        """

        queries = self.search_helper.generate_software_search_queries(
            region, country, category, language
        )

        logger.debug(f"      Generated {len(queries)} search queries for global platforms")

        # Placeholder products
        products = []

        # Example data structure - UK has strong coworking software ecosystem
        if category == "Coworking & Space Management" and country.lower() == "united kingdom":
            products = [
                {
                    "name": "Nexudus",
                    "category": category,
                    "region": region,
                    "country": country,
                    "platform_name": "G2",
                    "review_count": 847,
                    "rating": 4.6,
                    "pricing": "$99-$499/month",
                    "pricing_min": 99,
                    "pricing_max": 499,
                    "url": "https://www.g2.com/products/nexudus",
                    "language": "English",
                    "features": ["Desk Booking", "Member Management", "Billing", "Access Control"]
                },
                {
                    "name": "OfficeRnD",
                    "category": category,
                    "region": region,
                    "country": country,
                    "platform_name": "G2",
                    "review_count": 234,
                    "rating": 4.5,
                    "pricing": "$79-$399/month",
                    "pricing_min": 79,
                    "pricing_max": 399,
                    "url": "https://www.g2.com/products/officernd",
                    "language": "English"
                },
                {
                    "name": "Cobot",
                    "category": category,
                    "region": region,
                    "country": country,
                    "platform_name": "G2",
                    "review_count": 156,
                    "rating": 4.4,
                    "pricing": "$79-$299/month",
                    "pricing_min": 79,
                    "pricing_max": 299,
                    "url": "https://www.g2.com/products/cobot",
                    "language": "English"
                }
            ]

        # Romania has weak coworking software ecosystem
        elif category == "Coworking & Space Management" and country.lower() == "romania":
            products = [
                {
                    "name": "Nexudus",
                    "category": category,
                    "region": region,
                    "country": country,
                    "platform_name": "G2",
                    "review_count": 847,
                    "rating": 4.6,
                    "pricing": "$99-$499/month",
                    "pricing_min": 99,
                    "pricing_max": 499,
                    "url": "https://www.g2.com/products/nexudus",
                    "language": "English",
                    "features": ["Desk Booking", "Member Management", "Billing", "Access Control"]
                },
                {
                    "name": "OfficeRnD",
                    "category": category,
                    "region": region,
                    "country": country,
                    "platform_name": "G2",
                    "review_count": 234,
                    "rating": 4.5,
                    "pricing": "$79-$399/month",
                    "pricing_min": 79,
                    "pricing_max": 399,
                    "url": "https://www.g2.com/products/officernd",
                    "language": "English"
                },
                # Romanian local option (few reviews)
                {
                    "name": "Local Romanian Coworking Tool",
                    "category": category,
                    "region": region,
                    "country": country,
                    "platform_name": "Lista Firmelor",
                    "review_count": 12,
                    "rating": 4.0,
                    "pricing": "$50/month",
                    "pricing_min": 50,
                    "pricing_max": 50,
                    "url": "https://example.ro",
                    "language": "Romanian"
                }
            ]

        # === PROJECT MANAGEMENT ===
        elif category == "Project Management":
            if country.lower() == "united states":
                products = [
                    {"name": "Asana", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 12500, "rating": 4.4,
                     "pricing": "$10.99-$24.99/user/month", "pricing_min": 10.99, "pricing_max": 24.99,
                     "url": "https://www.asana.com", "language": "English"},
                    {"name": "Monday.com", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 9800, "rating": 4.6,
                     "pricing": "$8-$16/user/month", "pricing_min": 8, "pricing_max": 16,
                     "url": "https://monday.com", "language": "English"},
                    {"name": "ClickUp", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 7200, "rating": 4.7,
                     "pricing": "$5-$19/user/month", "pricing_min": 5, "pricing_max": 19,
                     "url": "https://clickup.com", "language": "English"}
                ]
            elif country.lower() == "japan":
                products = [
                    {"name": "Backlog", "category": category, "region": region, "country": country,
                     "platform_name": "ITreview", "review_count": 1200, "rating": 4.4,
                     "pricing": "$35-$175/month", "pricing_min": 35, "pricing_max": 175,
                     "url": "https://backlog.com", "language": "Japanese"},
                    {"name": "Asana", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 890, "rating": 4.3,
                     "pricing": "$10.99-$24.99/user/month", "pricing_min": 10.99, "pricing_max": 24.99,
                     "url": "https://www.asana.com", "language": "English/Japanese"}
                ]
            elif country.lower() in ["poland", "czech republic", "thailand", "indonesia"]:
                # Emerging markets with weak PM software
                products = [
                    {"name": "Asana", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 45, "rating": 4.2,
                     "pricing": "$10.99-$24.99/user/month", "pricing_min": 10.99, "pricing_max": 24.99,
                     "url": "https://www.asana.com", "language": "English"}
                ]

        # === CONSTRUCTION MANAGEMENT ===
        elif category == "Construction Management":
            if country.lower() == "united states":
                products = [
                    {"name": "Procore", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 3400, "rating": 4.5,
                     "pricing": "$375-$950/user/month", "pricing_min": 375, "pricing_max": 950,
                     "url": "https://www.procore.com", "language": "English"},
                    {"name": "Buildertrend", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 2100, "rating": 4.3,
                     "pricing": "$299-$699/month", "pricing_min": 299, "pricing_max": 699,
                     "url": "https://buildertrend.com", "language": "English"}
                ]
            elif country.lower() == "germany":
                products = [
                    {"name": "PlanRadar", "category": category, "region": region, "country": country,
                     "platform_name": "OMR Reviews", "review_count": 1200, "rating": 4.6,
                     "pricing": "$39-$199/user/month", "pricing_min": 39, "pricing_max": 199,
                     "url": "https://www.planradar.com", "language": "German/English"}
                ]
            elif country.lower() in ["poland", "romania", "india", "thailand"]:
                # Huge gap in construction software
                products = []

        # === MANUFACTURING & SUPPLY CHAIN ===
        elif category == "Manufacturing & Supply Chain":
            if country.lower() == "germany":
                products = [
                    {"name": "SAP S/4HANA", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 850, "rating": 4.2,
                     "pricing": "Enterprise", "pricing_min": 10000, "pricing_max": 50000,
                     "url": "https://www.sap.com", "language": "German/English"},
                    {"name": "Siemens Opcenter", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 320, "rating": 4.4,
                     "pricing": "Enterprise", "pricing_min": 5000, "pricing_max": 25000,
                     "url": "https://www.siemens.com", "language": "German/English"}
                ]
            elif country.lower() == "south korea":
                products = [
                    {"name": "Infor CloudSuite", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 180, "rating": 4.1,
                     "pricing": "Enterprise", "pricing_min": 8000, "pricing_max": 30000,
                     "url": "https://www.infor.com", "language": "Korean/English"}
                ]
            elif country.lower() in ["poland", "romania", "thailand", "indonesia"]:
                # Minimal manufacturing software
                products = []

        # === HR & PAYROLL ===
        elif category == "HR & Payroll":
            if country.lower() == "united states":
                products = [
                    {"name": "BambooHR", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 5600, "rating": 4.6,
                     "pricing": "$6-$12/employee/month", "pricing_min": 6, "pricing_max": 12,
                     "url": "https://www.bamboohr.com", "language": "English"},
                    {"name": "Gusto", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 4200, "rating": 4.7,
                     "pricing": "$40-$80/month + $6/user", "pricing_min": 40, "pricing_max": 80,
                     "url": "https://gusto.com", "language": "English"}
                ]
            elif country.lower() == "singapore":
                products = [
                    {"name": "Employment Hero", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 890, "rating": 4.5,
                     "pricing": "$5-$10/employee/month", "pricing_min": 5, "pricing_max": 10,
                     "url": "https://employmenthero.com", "language": "English"}
                ]
            elif country.lower() in ["india", "thailand", "indonesia"]:
                # Weak HR software penetration
                products = [
                    {"name": "Zoho People", "category": category, "region": region, "country": country,
                     "platform_name": "G2", "review_count": 120, "rating": 4.0,
                     "pricing": "$1-$3/user/month", "pricing_min": 1, "pricing_max": 3,
                     "url": "https://www.zoho.com/people", "language": "English"}
                ]

        return products

    async def _search_local_platforms(
        self,
        platforms: List[Dict[str, Any]],
        category: str,
        region: str
    ) -> List[Dict[str, Any]]:
        """
        Search local platforms for products in this category

        Uses platforms discovered in Phase 0
        """

        products = []

        # Filter platforms that likely have software reviews
        software_platforms = [
            p for p in platforms
            if p['type'] in ['software_reviews', 'saas_comparison', 'business_directory']
        ]

        logger.debug(f"      Checking {len(software_platforms)} local platforms")

        for platform in software_platforms:
            # TODO: Use dynamic scraper to actually scrape the platform
            # For now, placeholder
            pass

        return products

    async def _analyze_company_tech_stacks(
        self,
        companies: List[Dict[str, Any]],
        region: str
    ) -> Dict[str, List[str]]:
        """
        Analyze what technologies companies are using

        This helps validate software needs and identify popular tools

        TODO: Could use BuiltWith, Wappalyzer, job postings, etc.
        """

        tech_stacks = {
            'frontend': [],
            'backend': [],
            'infrastructure': [],
            'saas_tools': []
        }

        # For now, just inferred from company data
        for company in companies:
            if company.get('tech_stack'):
                for category, tools in company['tech_stack'].items():
                    if category in tech_stacks:
                        tech_stacks[category].extend(tools)

        return tech_stacks

    def _deduplicate_products(
        self,
        products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate products by name"""

        seen = set()
        unique = []

        for product in products:
            name = product.get('name', '').lower()

            if name and name not in seen:
                seen.add(name)
                unique.append(product)

        return unique

    def _calculate_adoption_score(self, product: Dict[str, Any]) -> float:
        """
        Calculate adoption score (0-10) based on reviews, rating, etc.

        Higher score = more popular/adopted in this region
        """

        review_count = product.get('review_count', 0)
        rating = product.get('rating', 0)

        # Base score on review count (logarithmic scale)
        if review_count > 0:
            import math
            review_score = min(10, math.log10(review_count + 1) * 2)
        else:
            review_score = 0

        # Weight by rating
        rating_score = (rating / 5.0) * 10 if rating else 5

        # Combined score (70% reviews, 30% rating)
        score = (review_score * 0.7) + (rating_score * 0.3)

        return round(score, 2)

    def _calculate_ecosystem_stats(self, ecosystem: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics about the ecosystem"""

        products_by_category = ecosystem['popular_products']

        total_products = sum(len(products) for products in products_by_category.values())
        total_reviews = sum(
            p.get('review_count', 0)
            for products in products_by_category.values()
            for p in products
        )

        avg_adoption = sum(
            p.get('adoption_score', 0)
            for products in products_by_category.values()
            for p in products
        ) / max(total_products, 1)

        return {
            'total_products': total_products,
            'total_reviews': total_reviews,
            'categories_mapped': len(products_by_category),
            'avg_adoption_score': round(avg_adoption, 2)
        }

    def _get_primary_country(self, region: str) -> str:
        region_map = {
            'Romania': 'Romania',
            'Eastern Europe': 'Romania',
            'Japan': 'Japan',
            'Asia': 'Japan',
            'United Kingdom': 'United Kingdom',
            'Western Europe': 'United Kingdom',
            'United States': 'United States',
            'North America': 'United States',
            'Germany': 'Germany',
            'Poland': 'Poland',
            'Czech Republic': 'Czech Republic',
            'Singapore': 'Singapore',
            'South Korea': 'South Korea',
            'India': 'India',
            'Thailand': 'Thailand',
            'Indonesia': 'Indonesia',
        }
        return region_map.get(region, region)

    def _get_primary_language(self, country: str) -> str:
        language_map = {
            'Romania': 'Romanian',
            'Japan': 'Japanese',
            'Germany': 'German',
            'United Kingdom': 'English',
            'United States': 'English',
            'Poland': 'Polish',
            'Czech Republic': 'Czech',
            'Singapore': 'English',
            'South Korea': 'Korean',
            'India': 'English',
            'Thailand': 'Thai',
            'Indonesia': 'Indonesian',
        }
        return language_map.get(country, 'English')

    def export_ecosystem_map(
        self,
        ecosystem_map: Dict[str, Dict],
        output_path: str = "data/software_ecosystems/ecosystem_map.json"
    ) -> str:
        """Export ecosystem map to JSON"""

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_regions': len(ecosystem_map),
            'ecosystems': ecosystem_map
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"\n✅ Ecosystem map exported to: {output_path}")

        return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Software Mapper Agent ready")
