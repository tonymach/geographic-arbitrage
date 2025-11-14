"""
Database utilities for Global Software Arbitrage
Creates and manages SQLite database with all necessary tables
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml


class Database:
    """Manages the arbitrage opportunity database"""

    def __init__(self, db_path: str = "data/arbitrage.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dicts
        self.cursor = self.conn.cursor()
        return self

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.close()

    def init_schema(self):
        """Initialize database schema"""

        # Table 1: Local Platforms (Phase 0 - Discovered platforms)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_platforms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT NOT NULL,
                country TEXT NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                type TEXT,  -- review_site, directory, tech_media, forum, etc.
                language TEXT,
                traffic_rank INTEGER,
                last_scraped TIMESTAMP,
                scraper_available BOOLEAN DEFAULT 0,
                scraper_code TEXT,  -- Store generated scraper code
                scraper_class_name TEXT,  -- Generated class name
                validation_status TEXT,  -- passed, failed, pending
                validation_checks JSON,  -- Results of validation checks
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(region, url)
            )
        """)

        # Table 2: Companies (Phase 1 - Regional company intelligence)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                region TEXT NOT NULL,
                country TEXT NOT NULL,
                industry TEXT,
                vertical TEXT,  -- More specific than industry
                website TEXT,
                revenue REAL,  -- Annual revenue in USD
                employee_count INTEGER,
                growth_rate REAL,  -- Year-over-year growth %
                funding_total REAL,  -- Total funding raised
                tech_stack JSON,  -- Technologies used
                data_sources JSON,  -- Where we found this company
                confidence_score REAL,  -- 0-1, how confident we are in the data
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, region)
            )
        """)

        # Table 3: Software Products (Phase 2 - Software ecosystem mapping)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS software_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                region TEXT NOT NULL,
                country TEXT,
                platform_id INTEGER,  -- Which platform discovered this
                platform_name TEXT,
                review_count INTEGER DEFAULT 0,
                rating REAL,  -- 0-5 scale
                pricing TEXT,  -- Pricing tier info
                pricing_min REAL,  -- Minimum price/month in USD
                pricing_max REAL,  -- Maximum price/month in USD
                adoption_score REAL,  -- 0-10, how popular in this region
                features JSON,  -- Key features
                target_market TEXT,  -- SMB, Enterprise, etc.
                url TEXT,
                language TEXT,  -- Primary language of product
                founded_year INTEGER,
                company_size TEXT,  -- startup, scaleup, enterprise
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (platform_id) REFERENCES local_platforms(id),
                UNIQUE(name, category, region)
            )
        """)

        # Table 4: Arbitrage Opportunities (Phase 3 - Cross-region gaps)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- Source region (where it's successful)
                source_region TEXT NOT NULL,
                source_country TEXT,
                source_product_id INTEGER,
                source_product_name TEXT NOT NULL,
                source_category TEXT NOT NULL,
                source_adoption INTEGER,  -- Number of reviews/users
                source_reviews INTEGER,
                source_rating REAL,
                source_pricing TEXT,

                -- Target region (where it's missing/weak)
                target_region TEXT NOT NULL,
                target_country TEXT,
                target_competitors JSON,  -- List of existing competitors
                target_competition_level INTEGER,  -- 0-5 scale
                target_best_alternative TEXT,  -- Current best solution

                -- Gap metrics
                gap_score REAL,  -- 0-10, how big is the gap
                review_count_gap INTEGER,  -- Difference in review counts
                rating_gap REAL,  -- Difference in ratings
                competition_gap REAL,  -- How much less competition

                -- Validation signals
                need_validated BOOLEAN DEFAULT 0,
                company_need_score REAL,  -- 0-10
                contract_validation JSON,  -- Government contract evidence
                pain_signals JSON,  -- Reddit, forums, etc.
                job_market_signals JSON,  -- Job postings mentioning this type of tool

                -- Opportunity sizing
                estimated_tam REAL,  -- Total Addressable Market in USD
                estimated_companies INTEGER,  -- Companies that could use this
                opportunity_score REAL,  -- 0-10, overall opportunity score

                -- Timing & market insight
                market_maturity TEXT,  -- emerging, growing, mature
                digitalization_lag_years INTEGER,  -- Years behind source region
                market_readiness TEXT,  -- ready, developing, early

                -- Narrative
                insight_narrative TEXT,  -- Human-readable opportunity description
                recommended_action TEXT,  -- Build, partner, localize, etc.

                -- Metadata
                confidence_score REAL,  -- 0-1, confidence in this opportunity
                last_validated TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (source_product_id) REFERENCES software_products(id),
                UNIQUE(source_product_name, source_category, source_region, target_region)
            )
        """)

        # Table 5: Government Contracts (Phase 4 - Validation)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT NOT NULL,
                country TEXT NOT NULL,
                contract_id TEXT,  -- Original contract ID from source
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,  -- Inferred software category
                keywords JSON,  -- Extracted keywords
                value REAL,  -- Contract value in USD
                currency TEXT,
                department TEXT,  -- Government department
                agency TEXT,
                deadline DATE,
                award_date DATE,
                status TEXT,  -- open, awarded, closed
                winner TEXT,  -- Winning company if awarded
                url TEXT,
                source_platform TEXT,  -- Which gov platform
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(country, contract_id)
            )
        """)

        # Table 6: Pain Signals (Phase 4 - Validation)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pain_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT NOT NULL,
                country TEXT,
                category TEXT NOT NULL,
                source TEXT NOT NULL,  -- reddit, indie_hackers, forums, etc.
                source_url TEXT,
                title TEXT,
                content TEXT,
                sentiment TEXT,  -- negative, neutral, positive
                pain_intensity REAL,  -- 0-10, how strong is the pain
                mentions_count INTEGER DEFAULT 1,
                upvotes INTEGER,
                comments_count INTEGER,
                keywords JSON,
                posted_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table 7: Tech Stacks (Phase 2 - Company technology detection)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tech_stacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                technology TEXT NOT NULL,
                category TEXT,  -- frontend, backend, infrastructure, SaaS tools, etc.
                confidence REAL,  -- 0-1, how confident we are
                source TEXT,  -- builtwith, wappalyzer, job_posting, etc.
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                UNIQUE(company_id, technology)
            )
        """)

        # Table 8: Job Postings (Phase 2 - Market signal validation)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_postings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                region TEXT NOT NULL,
                country TEXT,
                title TEXT NOT NULL,
                description TEXT,
                required_tools JSON,  -- Software tools mentioned
                required_skills JSON,
                category TEXT,  -- Job category
                posted_date DATE,
                source TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Create indexes for better query performance
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_platforms_region
            ON local_platforms(region, type)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_companies_region
            ON companies(region, industry)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_region_category
            ON software_products(region, category, adoption_score DESC)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_opportunities_score
            ON arbitrage_opportunities(opportunity_score DESC, gap_score DESC)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_contracts_region_category
            ON contracts(region, category, value DESC)
        """)

        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_pain_region_category
            ON pain_signals(region, category, pain_intensity DESC)
        """)

        self.conn.commit()
        print("✅ Database schema initialized successfully")

    # Helper methods for data insertion

    def insert_platform(self, platform: Dict[str, Any]) -> int:
        """Insert a discovered platform"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO local_platforms
            (region, country, name, url, type, language, validation_status, validation_checks, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            platform.get('region'),
            platform.get('country'),
            platform.get('name'),
            platform.get('url'),
            platform.get('type'),
            platform.get('language'),
            platform.get('validation_status', 'pending'),
            json.dumps(platform.get('validation_checks', {})),
            platform.get('notes')
        ))
        return self.cursor.lastrowid

    def insert_company(self, company: Dict[str, Any]) -> int:
        """Insert a company"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO companies
            (name, region, country, industry, vertical, website, revenue, employee_count,
             growth_rate, funding_total, tech_stack, data_sources, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company.get('name'),
            company.get('region'),
            company.get('country'),
            company.get('industry'),
            company.get('vertical'),
            company.get('website'),
            company.get('revenue'),
            company.get('employee_count'),
            company.get('growth_rate'),
            company.get('funding_total'),
            json.dumps(company.get('tech_stack', {})),
            json.dumps(company.get('data_sources', [])),
            company.get('confidence_score', 0.5)
        ))
        return self.cursor.lastrowid

    def insert_product(self, product: Dict[str, Any]) -> int:
        """Insert a software product"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO software_products
            (name, category, region, country, platform_id, platform_name, review_count,
             rating, pricing, pricing_min, pricing_max, adoption_score, features,
             target_market, url, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product.get('name'),
            product.get('category'),
            product.get('region'),
            product.get('country'),
            product.get('platform_id'),
            product.get('platform_name'),
            product.get('review_count', 0),
            product.get('rating'),
            product.get('pricing'),
            product.get('pricing_min'),
            product.get('pricing_max'),
            product.get('adoption_score'),
            json.dumps(product.get('features', [])),
            product.get('target_market'),
            product.get('url'),
            product.get('language')
        ))
        return self.cursor.lastrowid

    def insert_opportunity(self, opportunity: Dict[str, Any]) -> int:
        """Insert an arbitrage opportunity"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO arbitrage_opportunities
            (source_region, source_country, source_product_name, source_category,
             source_adoption, source_reviews, source_rating, source_pricing,
             target_region, target_country, target_competitors, target_competition_level,
             gap_score, review_count_gap, rating_gap, competition_gap,
             need_validated, company_need_score, contract_validation, pain_signals,
             estimated_tam, opportunity_score, market_maturity, digitalization_lag_years,
             insight_narrative, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            opportunity.get('source_region'),
            opportunity.get('source_country'),
            opportunity.get('source_product_name'),
            opportunity.get('source_category'),
            opportunity.get('source_adoption'),
            opportunity.get('source_reviews'),
            opportunity.get('source_rating'),
            opportunity.get('source_pricing'),
            opportunity.get('target_region'),
            opportunity.get('target_country'),
            json.dumps(opportunity.get('target_competitors', [])),
            opportunity.get('target_competition_level'),
            opportunity.get('gap_score'),
            opportunity.get('review_count_gap'),
            opportunity.get('rating_gap'),
            opportunity.get('competition_gap'),
            opportunity.get('need_validated', False),
            opportunity.get('company_need_score'),
            json.dumps(opportunity.get('contract_validation', {})),
            json.dumps(opportunity.get('pain_signals', {})),
            opportunity.get('estimated_tam'),
            opportunity.get('opportunity_score'),
            opportunity.get('market_maturity'),
            opportunity.get('digitalization_lag_years'),
            opportunity.get('insight_narrative'),
            opportunity.get('confidence_score', 0.5)
        ))
        return self.cursor.lastrowid

    def insert_contract(self, contract: Dict[str, Any]) -> int:
        """Insert a government contract"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO contracts
            (region, country, contract_id, title, description, category, keywords,
             value, currency, department, agency, deadline, status, url, source_platform)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contract.get('region'),
            contract.get('country'),
            contract.get('contract_id'),
            contract.get('title'),
            contract.get('description'),
            contract.get('category'),
            json.dumps(contract.get('keywords', [])),
            contract.get('value'),
            contract.get('currency', 'USD'),
            contract.get('department'),
            contract.get('agency'),
            contract.get('deadline'),
            contract.get('status'),
            contract.get('url'),
            contract.get('source_platform')
        ))
        return self.cursor.lastrowid

    def insert_pain_signal(self, pain: Dict[str, Any]) -> int:
        """Insert a pain signal"""
        self.cursor.execute("""
            INSERT INTO pain_signals
            (region, country, category, source, source_url, title, content,
             sentiment, pain_intensity, mentions_count, upvotes, keywords, posted_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pain.get('region'),
            pain.get('country'),
            pain.get('category'),
            pain.get('source'),
            pain.get('source_url'),
            pain.get('title'),
            pain.get('content'),
            pain.get('sentiment'),
            pain.get('pain_intensity'),
            pain.get('mentions_count', 1),
            pain.get('upvotes'),
            json.dumps(pain.get('keywords', [])),
            pain.get('posted_date')
        ))
        return self.cursor.lastrowid

    # Query helpers

    def get_platforms_by_region(self, region: str) -> List[Dict]:
        """Get all platforms for a region"""
        self.cursor.execute("""
            SELECT * FROM local_platforms
            WHERE region = ? AND validation_status = 'passed'
            ORDER BY traffic_rank ASC
        """, (region,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_products_by_region_category(self, region: str, category: str) -> List[Dict]:
        """Get all products for a region and category"""
        self.cursor.execute("""
            SELECT * FROM software_products
            WHERE region = ? AND category = ?
            ORDER BY adoption_score DESC, review_count DESC
        """, (region, category))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_top_opportunities(self, limit: int = 10) -> List[Dict]:
        """Get top arbitrage opportunities"""
        self.cursor.execute("""
            SELECT * FROM arbitrage_opportunities
            ORDER BY opportunity_score DESC, gap_score DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_contracts_by_region_category(self, region: str, category: str) -> List[Dict]:
        """Get contracts for validation"""
        self.cursor.execute("""
            SELECT * FROM contracts
            WHERE region = ? AND category = ?
            ORDER BY value DESC
        """, (region, category))
        return [dict(row) for row in self.cursor.fetchall()]


def init_database(db_path: str = "data/arbitrage.db"):
    """Initialize the database with schema"""
    with Database(db_path) as db:
        db.init_schema()
    return db_path


if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing database...")
    init_database()
    print("Database ready!")
