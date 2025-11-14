"""
Web search helper utilities for discovering platforms and gathering intelligence
Uses Claude's web search capabilities
"""

import json
from typing import List, Dict, Any, Optional
import time
import logging

logger = logging.getLogger(__name__)


class WebSearchHelper:
    """Helper for web searches and intelligence gathering"""

    def __init__(self, rate_limit_delay: float = 1.0):
        self.rate_limit_delay = rate_limit_delay
        self.last_search_time = 0

    def _rate_limit(self):
        """Enforce rate limiting between searches"""
        elapsed = time.time() - self.last_search_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_search_time = time.time()

    def search_local_platforms(
        self,
        region: str,
        country: str,
        language: str,
        platform_types: List[str] = None
    ) -> List[str]:
        """
        Generate search queries to discover local platforms

        Returns list of search queries that Claude should execute
        """
        if platform_types is None:
            platform_types = [
                "software review sites",
                "business directories",
                "SaaS comparison platforms",
                "tech news sites",
                "startup directories",
                "business review platforms"
            ]

        search_queries = []

        # Base queries
        for platform_type in platform_types:
            # English query
            search_queries.append(
                f"best {platform_type} in {country} {region}"
            )
            search_queries.append(
                f"{country} local {platform_type} popular"
            )
            search_queries.append(
                f"where do {country} companies find software {platform_type}"
            )

            # Native language query if not English
            if language.lower() != "english":
                search_queries.append(
                    f"{platform_type} {country} {language}"
                )

        # Specific vertical queries
        search_queries.extend([
            f"{country} B2B software marketplace",
            f"{country} technology review platform",
            f"{country} business software directory",
            f"alternative to G2 in {country}",
            f"alternative to Capterra in {country}",
            f"{country} startup ecosystem platforms",
            f"where {country} businesses review software",
        ])

        return search_queries

    def parse_platform_discovery_results(
        self,
        search_results: str,
        region: str
    ) -> List[Dict[str, Any]]:
        """
        Parse search results to extract potential platforms

        This is a template - actual parsing will be done by Claude
        Returns list of discovered platforms with metadata
        """
        # This will be filled in by Claude during actual discovery
        # Template structure for what we expect
        platforms = []

        platform_template = {
            'name': '',
            'url': '',
            'type': '',  # review_site, directory, tech_media, etc.
            'region': region,
            'language': '',
            'description': '',
            'estimated_traffic': None,
            'discovery_source': 'web_search'
        }

        return platforms

    async def validate_platform_url(self, url: str) -> Dict[str, Any]:
        """
        Generate validation checks for a platform URL

        Returns dict with validation requirements
        """
        return {
            'url': url,
            'checks_needed': [
                'is_accessible',  # Can we reach it?
                'has_recent_content',  # Is it active?
                'contains_software_data',  # Has relevant data?
                'is_scrapeable',  # Can we scrape it?
                'has_sufficient_size',  # Enough content to be useful?
            ]
        }

    def generate_company_search_queries(
        self,
        region: str,
        country: str,
        language: str
    ) -> List[str]:
        """Generate search queries to find top companies in a region"""

        queries = [
            # Top company lists
            f"top 100 companies {country} {region}",
            f"fastest growing companies {country}",
            f"largest companies {country} by revenue",
            f"{country} unicorn startups",
            f"{country} top tech companies",

            # Industry specific
            f"{country} leading software companies",
            f"{country} SaaS companies",
            f"{country} technology sector leaders",

            # Rankings and lists
            f"{country} Deloitte Fast 500",
            f"{country} Forbes top companies",
            f"{country} startup ecosystem",
            f"{country} stock exchange largest companies",

            # Investment and funding
            f"{country} most funded startups 2024",
            f"{country} venture capital investments",
            f"{country} series A companies",

            # Native language if applicable
            f"best companies {country} {language}" if language != "English" else None,
        ]

        return [q for q in queries if q is not None]

    def generate_software_search_queries(
        self,
        region: str,
        country: str,
        category: str,
        language: str
    ) -> List[str]:
        """Generate search queries to find software in a specific category"""

        queries = [
            # Direct category searches
            f"best {category} software {country}",
            f"popular {category} tools {region}",
            f"{category} software used in {country}",
            f"{country} companies using {category} software",

            # Comparison and reviews
            f"{category} software reviews {country}",
            f"compare {category} tools {region}",
            f"{category} software market {country}",

            # Market specific
            f"{category} SaaS {country} market",
            f"{category} software adoption {country}",
            f"what {category} software do {country} companies use",

            # Native language
            f"{category} software {country} {language}" if language != "English" else None,
        ]

        return [q for q in queries if q is not None]

    def generate_pain_signal_queries(
        self,
        region: str,
        country: str,
        category: str
    ) -> List[str]:
        """Generate queries to find pain signals"""

        queries = [
            # Reddit
            f"site:reddit.com {country} {category} software problems",
            f"site:reddit.com {region} need better {category} tool",
            f"site:reddit.com {country} frustrated with {category}",

            # Forums
            f"{country} forum {category} software recommendations",
            f"{country} business forum {category} tools",

            # Q&A sites
            f"site:quora.com {country} best {category} software",
            f"{country} companies {category} software challenges",

            # Social proof
            f"{country} twitter {category} software complaints",
            f"{category} problems {country} businesses",
        ]

        return queries

    def generate_contract_keywords(self, category: str) -> List[str]:
        """
        Generate keywords to search for in government contracts
        for a specific software category
        """

        # Base keywords by category
        keyword_map = {
            "Project Management": [
                "project management", "task tracking", "collaboration software",
                "workflow management", "project tracking", "PMO"
            ],
            "CRM": [
                "customer relationship management", "CRM", "sales automation",
                "contact management", "customer database", "lead management"
            ],
            "Accounting & Finance": [
                "accounting software", "financial management", "bookkeeping",
                "invoicing", "expense management", "financial reporting"
            ],
            "HR & Payroll": [
                "human resources", "payroll", "HR management", "employee management",
                "time tracking", "benefits administration", "HRIS"
            ],
            "Construction Management": [
                "construction management", "project scheduling", "job costing",
                "contractor management", "construction tracking", "site management"
            ],
            "Coworking & Space Management": [
                "coworking", "space management", "desk booking", "workspace management",
                "facility management", "office space", "shared workspace", "hot desking"
            ],
            # Add more categories as needed
        }

        return keyword_map.get(category, [category.lower(), f"{category} software"])

    def create_research_prompt(
        self,
        research_type: str,
        region: str,
        **kwargs
    ) -> str:
        """
        Create detailed research prompts for Claude

        research_type: 'discover_platforms', 'find_companies', 'find_software', etc.
        """

        prompts = {
            'discover_platforms': f"""
                Research and identify the TOP platforms used in {region} for:
                - Software reviews and comparisons
                - Business directories
                - Startup ecosystems
                - Technology news and reviews
                - B2B software discovery

                For each platform found:
                1. Name and URL
                2. Type (review site, directory, media, forum)
                3. Primary language
                4. Estimated popularity/traffic
                5. Whether it has software/company data
                6. Whether it appears scrapeable

                Focus on platforms that LOCALS actually use, not just
                international platforms with a regional section.

                Use web search to validate these platforms exist and are active.
                Return structured data.
            """,

            'find_companies': f"""
                Find the top 50-200 most successful companies in {region}.

                Look for:
                - Revenue/funding data
                - Growth rates
                - Industry/vertical
                - Company websites
                - Employee counts

                Use multiple sources:
                - Local business rankings
                - Tech company lists
                - Stock exchange data
                - Funding announcements
                - Industry reports

                Return structured data with sources cited.
            """,

            'find_software': f"""
                Identify the most popular software in the {kwargs.get('category')}
                category used in {region}.

                Find:
                - Product names
                - Review counts and ratings
                - Pricing information
                - Target market (SMB, enterprise, etc.)
                - Key features
                - Company/vendor information

                Search both international platforms (G2, Capterra) filtered by
                region AND local platforms.

                Return structured data.
            """,

            'validate_pain': f"""
                Search for pain signals related to {kwargs.get('category')}
                software in {region}.

                Look on:
                - Reddit (region-specific subreddits)
                - Local business forums
                - Tech forums
                - Q&A sites
                - Social media

                Identify:
                - What are people complaining about?
                - What solutions are they asking for?
                - What current tools are frustrating them?
                - What features are missing?

                Rate pain intensity (1-10) based on:
                - Frequency of complaints
                - Severity of problems
                - Number of people affected

                Return structured findings.
            """
        }

        return prompts.get(research_type, f"Research {research_type} for {region}")

    def extract_structured_data(
        self,
        research_results: str,
        data_type: str
    ) -> List[Dict[str, Any]]:
        """
        Template for extracting structured data from research results
        Actual extraction will be done by Claude
        """

        templates = {
            'platforms': {
                'name': '',
                'url': '',
                'type': '',
                'language': '',
                'estimated_traffic': None,
                'has_software_data': False,
                'scrapeable': None,
                'notes': ''
            },
            'companies': {
                'name': '',
                'website': '',
                'industry': '',
                'revenue': None,
                'employee_count': None,
                'growth_rate': None,
                'data_source': ''
            },
            'products': {
                'name': '',
                'category': '',
                'review_count': 0,
                'rating': None,
                'pricing': '',
                'url': '',
                'platform_source': ''
            },
            'pain_signals': {
                'source': '',
                'title': '',
                'content': '',
                'pain_intensity': 0,
                'category': '',
                'url': ''
            }
        }

        return []  # Claude will fill this in

    def format_discovery_summary(
        self,
        platforms: List[Dict],
        region: str
    ) -> str:
        """Format platform discovery results for human review"""

        summary = f"\n{'='*80}\n"
        summary += f"PLATFORM DISCOVERY RESULTS: {region}\n"
        summary += f"{'='*80}\n\n"

        summary += f"Found {len(platforms)} platforms:\n\n"

        for i, platform in enumerate(platforms, 1):
            summary += f"{i}. {platform.get('name')} ({platform.get('type')})\n"
            summary += f"   URL: {platform.get('url')}\n"
            summary += f"   Language: {platform.get('language')}\n"
            summary += f"   Notes: {platform.get('notes', 'N/A')}\n\n"

        return summary


# Usage example
if __name__ == "__main__":
    helper = WebSearchHelper()

    # Example: discover platforms in Romania
    queries = helper.search_local_platforms(
        region="Eastern Europe",
        country="Romania",
        language="Romanian"
    )

    print("Search queries for Romania platform discovery:")
    for q in queries[:5]:  # Show first 5
        print(f"  - {q}")
