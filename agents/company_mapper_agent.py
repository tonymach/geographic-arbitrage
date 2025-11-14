"""
Company Mapper Agent - Phase 1

Maps successful companies in each region to understand:
1. What industries are thriving
2. What size companies exist
3. What their tech stacks might be
4. What software needs they likely have

This tells us what's WORKING in each region and helps us identify
software needs based on company verticals.
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


class CompanyMapperAgent:
    """
    Maps successful companies per region

    Sources:
    - CrunchBase
    - LinkedIn top companies
    - Local rankings (Deloitte Fast 500, etc.)
    - Stock exchanges
    - Tech media
    - Local business directories (from Platform Discovery)
    """

    def __init__(self, config: Dict[str, Any], db: Database):
        self.config = config
        self.db = db
        self.search_helper = WebSearchHelper()

        # Get test mode settings
        self.test_mode = config.get('test_mode', {}).get('enabled', False)
        self.max_companies = config.get('test_mode', {}).get('max_companies_per_region', 50)

        logger.info(f"Company Mapper Agent initialized (max companies: {self.max_companies})")

    async def map_all_regions(
        self,
        regions: List[str],
        platform_map: Dict[str, List[Dict]]
    ) -> Dict[str, List[Dict]]:
        """
        Map companies for all regions in parallel

        Returns: {region: [company1, company2, ...]}
        """

        logger.info(f"Starting company mapping for {len(regions)} regions")

        # Map companies in parallel
        tasks = []
        for region in regions:
            platforms = platform_map.get(region, [])
            task = self.map_region_companies(region, platforms)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build company map
        company_map = {}
        for region, result in zip(regions, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to map companies for {region}: {result}")
                company_map[region] = []
            else:
                company_map[region] = result
                logger.info(f"Mapped {len(result)} companies for {region}")

        return company_map

    async def map_region_companies(
        self,
        region: str,
        platforms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Map companies for a single region

        Steps:
        1. Search for top companies via web search
        2. Scrape local platforms (business directories)
        3. Identify industries and verticals
        4. Estimate size/revenue/growth
        5. Infer tech stack needs
        6. Store in database
        """

        logger.info(f"\n{'='*80}")
        logger.info(f"Mapping companies for: {region}")
        logger.info(f"{'='*80}\n")

        country = self._get_primary_country(region)
        language = self._get_primary_language(country)

        companies_found = []

        # Step 1: Search for top companies
        logger.info("  Searching for top companies...")
        search_companies = await self._search_top_companies(region, country, language)
        companies_found.extend(search_companies)
        logger.info(f"  Found {len(search_companies)} companies via web search")

        # Step 2: Scrape local platforms (business directories)
        logger.info("  Checking local business directories...")
        directory_companies = await self._scrape_business_directories(region, platforms)
        companies_found.extend(directory_companies)
        logger.info(f"  Found {len(directory_companies)} companies from directories")

        # Step 3: Deduplicate and enrich
        logger.info("  Deduplicating and enriching data...")
        unique_companies = self._deduplicate_companies(companies_found)
        enriched_companies = await self._enrich_companies(unique_companies, region)

        # Limit in test mode
        if self.test_mode and len(enriched_companies) > self.max_companies:
            enriched_companies = enriched_companies[:self.max_companies]
            logger.info(f"  TEST MODE: Limited to {self.max_companies} companies")

        # Step 4: Analyze industries and infer software needs
        logger.info("  Analyzing industries and inferring software needs...")
        for company in enriched_companies:
            company['inferred_software_needs'] = self._infer_software_needs(
                company.get('industry'),
                company.get('vertical'),
                company.get('employee_count')
            )

        # Step 5: Store in database
        logger.info(f"  Storing {len(enriched_companies)} companies...")
        for company in enriched_companies:
            try:
                self.db.insert_company(company)
            except Exception as e:
                logger.error(f"Failed to store company {company.get('name')}: {e}")

        self.db.conn.commit()

        logger.info(f"\n✅ Company mapping complete for {region}")
        logger.info(f"   Total companies: {len(enriched_companies)}")

        return enriched_companies

    async def _search_top_companies(
        self,
        region: str,
        country: str,
        language: str
    ) -> List[Dict[str, Any]]:
        """
        Use web search to find top companies in region

        TODO: In actual implementation, this would use Claude's web_search
        to find companies from various ranking lists
        """

        # Generate search queries
        queries = self.search_helper.generate_company_search_queries(
            region, country, language
        )

        logger.info(f"    Generated {len(queries)} search queries")
        logger.debug(f"    Sample queries: {queries[:3]}")

        # Create research prompt
        research_prompt = self.search_helper.create_research_prompt(
            research_type='find_companies',
            region=region,
            country=country,
            language=language
        )

        logger.info(f"""

        📋 RESEARCH PROMPT FOR CLAUDE:
        {research_prompt}

        SEARCH QUERIES:
        {chr(10).join(f"  - {q}" for q in queries[:5])}
        """)

        # Placeholder companies for testing
        companies = []

        if country.lower() == "romania":
            companies = [
                {
                    "name": "UiPath",
                    "region": region,
                    "country": country,
                    "industry": "Software",
                    "vertical": "RPA (Robotic Process Automation)",
                    "website": "https://www.uipath.com",
                    "revenue": 1_000_000_000,  # ~$1B
                    "employee_count": 4000,
                    "growth_rate": 25.0,
                    "funding_total": 2_000_000_000,
                    "data_sources": ["web_search", "crunchbase"],
                    "confidence_score": 0.9
                },
                {
                    "name": "Bitdefender",
                    "region": region,
                    "country": country,
                    "industry": "Software",
                    "vertical": "Cybersecurity",
                    "website": "https://www.bitdefender.com",
                    "revenue": 800_000_000,
                    "employee_count": 1800,
                    "growth_rate": 15.0,
                    "data_sources": ["web_search"],
                    "confidence_score": 0.85
                },
                {
                    "name": "Siveco Romania",
                    "region": region,
                    "country": country,
                    "industry": "IT Services",
                    "vertical": "Enterprise Software",
                    "website": "https://www.siveco.ro",
                    "revenue": 50_000_000,
                    "employee_count": 600,
                    "growth_rate": 10.0,
                    "data_sources": ["local_directory"],
                    "confidence_score": 0.7
                }
            ]

        elif country.lower() == "japan":
            companies = [
                {
                    "name": "Rakuten",
                    "region": region,
                    "country": country,
                    "industry": "E-commerce",
                    "vertical": "Marketplace",
                    "website": "https://www.rakuten.com",
                    "revenue": 15_000_000_000,
                    "employee_count": 28000,
                    "growth_rate": 12.0,
                    "data_sources": ["web_search"],
                    "confidence_score": 0.95
                },
                {
                    "name": "Mercari",
                    "region": region,
                    "country": country,
                    "industry": "E-commerce",
                    "vertical": "C2C Marketplace",
                    "website": "https://www.mercari.com",
                    "revenue": 500_000_000,
                    "employee_count": 2000,
                    "growth_rate": 20.0,
                    "data_sources": ["web_search"],
                    "confidence_score": 0.9
                },
                {
                    "name": "SmartHR",
                    "region": region,
                    "country": country,
                    "industry": "Software",
                    "vertical": "HR Tech",
                    "website": "https://smarthr.jp",
                    "revenue": 100_000_000,
                    "employee_count": 800,
                    "growth_rate": 40.0,
                    "data_sources": ["web_search", "local_platform"],
                    "confidence_score": 0.85
                }
            ]

        return companies

    async def _scrape_business_directories(
        self,
        region: str,
        platforms: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Scrape business directories to find companies

        Uses platforms discovered in Phase 0
        """

        companies = []

        # Find business directory platforms
        directories = [p for p in platforms if p['type'] == 'business_directory']

        logger.info(f"    Found {len(directories)} business directories")

        for directory in directories:
            logger.debug(f"    Scraping {directory['name']}...")

            # TODO: In actual implementation, use dynamic scraper
            # For now, placeholder

        return companies

    def _deduplicate_companies(
        self,
        companies: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate companies (by name or website)"""

        seen = set()
        unique = []

        for company in companies:
            key = (company.get('name', '').lower(), company.get('website', ''))

            if key not in seen:
                seen.add(key)
                unique.append(company)

        return unique

    async def _enrich_companies(
        self,
        companies: List[Dict[str, Any]],
        region: str
    ) -> List[Dict[str, Any]]:
        """
        Enrich company data with additional info

        TODO: Could fetch additional data from:
        - LinkedIn
        - Crunchbase API
        - Company websites
        - Job boards
        """

        # For now, just ensure all required fields exist
        for company in companies:
            company.setdefault('region', region)
            company.setdefault('data_sources', [])
            company.setdefault('confidence_score', 0.5)
            company.setdefault('tech_stack', {})

        return companies

    def _infer_software_needs(
        self,
        industry: str,
        vertical: str,
        employee_count: int
    ) -> List[str]:
        """
        Infer what software categories this company likely needs
        based on industry, vertical, and size
        """

        needs = []

        # Universal needs
        needs.extend(['CRM & Sales', 'HR & Payroll', 'Accounting & Finance'])

        # Size-based needs
        if employee_count and employee_count > 50:
            needs.extend(['Project Management', 'Business Intelligence & Analytics'])

        if employee_count and employee_count > 200:
            needs.extend(['Workflow Automation', 'Customer Support & Helpdesk'])

        # Industry-specific needs
        industry_map = {
            'Software': [
                'DevOps & Development Tools',
                'Project Management',
                'Cybersecurity',
                'Customer Support & Helpdesk'
            ],
            'E-commerce': [
                'E-commerce Platform',
                'Inventory Management',
                'Marketing Automation',
                'Customer Support & Helpdesk'
            ],
            'Manufacturing': [
                'Manufacturing & Supply Chain',
                'Inventory Management',
                'Project Management'
            ],
            'Construction': [
                'Construction Management',
                'Project Management',
                'Document Management'
            ],
            'Healthcare': [
                'Healthcare Management',
                'Document Management',
                'Customer Support & Helpdesk'
            ],
            'Real Estate': [
                'Real Estate Management',
                'Document Management',
                'CRM & Sales'
            ],
        }

        if industry in industry_map:
            needs.extend(industry_map[industry])

        return list(set(needs))  # Remove duplicates

    def _get_primary_country(self, region: str) -> str:
        """Get primary country for region"""
        region_map = {
            'Romania': 'Romania',
            'Eastern Europe': 'Romania',
            'Japan': 'Japan',
            'Asia': 'Japan',
            'United Kingdom': 'United Kingdom',
            'Western Europe': 'United Kingdom',
        }
        return region_map.get(region, region)

    def _get_primary_language(self, country: str) -> str:
        """Get primary language for country"""
        language_map = {
            'Romania': 'Romanian',
            'Japan': 'Japanese',
            'Germany': 'German',
            'United States': 'English',
            'United Kingdom': 'English',
        }
        return language_map.get(country, 'English')

    def export_company_map(
        self,
        company_map: Dict[str, List[Dict]],
        output_path: str = "data/companies/company_map.json"
    ) -> str:
        """Export company map to JSON"""

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        export_data = {
            'generated_at': datetime.now().isoformat(),
            'total_regions': len(company_map),
            'total_companies': sum(len(companies) for companies in company_map.values()),
            'companies_by_region': company_map
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"\n✅ Company map exported to: {output_path}")

        return output_path


# Test standalone
async def test_company_mapper():
    """Test company mapping"""
    import yaml
    from utils.db import Database

    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    db = Database('data/arbitrage.db')
    db.connect()
    db.init_schema()

    agent = CompanyMapperAgent(config, db)

    # Test with Romania
    companies = await agent.map_region_companies('Romania', [])

    print(f"\n✅ Found {len(companies)} companies in Romania")
    for c in companies[:5]:
        print(f"  • {c['name']} - {c['industry']} ({c.get('employee_count')} employees)")

    db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_company_mapper())
