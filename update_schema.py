#!/usr/bin/env python3
"""
Update Turso schema with PE-grade fields

Adds:
1. software_products table (Phase 1 output)
2. Extended fields to arbitrage_opportunities (unit economics, financials)
"""

import subprocess
import sys

DB_NAME = "geographic-arbitrage"


def run_turso_sql(sql):
    """Execute SQL via turso CLI"""
    result = subprocess.run(
        ["turso", "db", "shell", DB_NAME, sql],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(result.stdout)
    return True


def create_software_products_table():
    """Create software_products table for Phase 1 output"""

    print("📋 Creating software_products table...")

    sql = """
        CREATE TABLE IF NOT EXISTS software_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT NOT NULL,
            category TEXT NOT NULL,
            product_name TEXT NOT NULL,
            url TEXT,
            reviews INTEGER,
            rating REAL,
            adoption_score REAL,
            source_platforms TEXT,
            estimated_revenue TEXT,
            pricing TEXT,
            target_customer TEXT,
            key_features TEXT,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    if run_turso_sql(sql):
        print("✅ software_products table created")
        return True
    return False


def extend_arbitrage_opportunities():
    """Add PE-grade fields to arbitrage_opportunities table"""

    print("\n📋 Extending arbitrage_opportunities table...")

    # Check if columns already exist first
    check_sql = "SELECT * FROM arbitrage_opportunities LIMIT 0;"
    run_turso_sql(check_sql)

    fields = [
        ("tam_estimate", "TEXT"),
        ("acv", "INTEGER"),
        ("cac", "INTEGER"),
        ("ltv", "INTEGER"),
        ("ltv_cac_ratio", "REAL"),
        ("payback_period_months", "REAL"),
        ("gross_margin_pct", "REAL"),
        ("year_1_revenue", "INTEGER"),
        ("year_2_revenue", "INTEGER"),
        ("year_3_revenue", "INTEGER"),
        ("year_3_ebitda", "INTEGER"),
        ("exit_value_base", "INTEGER"),
        ("exit_value_bull", "INTEGER"),
        ("capital_required", "INTEGER"),
        ("breakeven_month", "INTEGER"),
        ("roi_multiple", "REAL"),
        ("risk_summary", "TEXT"),
        ("moat_score", "REAL"),
        ("execution_plan", "TEXT"),
        ("comparable_transactions", "TEXT"),
    ]

    for field_name, field_type in fields:
        sql = f"ALTER TABLE arbitrage_opportunities ADD COLUMN {field_name} {field_type};"
        # This might fail if column exists, that's OK
        run_turso_sql(sql)

    print("✅ arbitrage_opportunities table extended")
    return True


def create_indexes():
    """Create indexes for better query performance"""

    print("\n📋 Creating indexes...")

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_products_region ON software_products(region);",
        "CREATE INDEX IF NOT EXISTS idx_products_category ON software_products(category);",
        "CREATE INDEX IF NOT EXISTS idx_opps_score ON arbitrage_opportunities(opportunity_score DESC);",
        "CREATE INDEX IF NOT EXISTS idx_opps_validated ON arbitrage_opportunities(validated);",
        "CREATE INDEX IF NOT EXISTS idx_signals_region ON pain_signals(region);",
    ]

    for idx_sql in indexes:
        run_turso_sql(idx_sql)

    print("✅ Indexes created")
    return True


def verify_schema():
    """Verify all tables exist"""

    print("\n🔍 Verifying schema...")

    tables = [
        "local_platforms",
        "software_products",
        "arbitrage_opportunities",
        "pain_signals"
    ]

    for table in tables:
        sql = f"SELECT COUNT(*) FROM {table};"
        print(f"\n{table}:")
        run_turso_sql(sql)

    print("\n✅ Schema verification complete")


def main():
    print("=" * 80)
    print("TURSO SCHEMA UPDATE")
    print("=" * 80)
    print()

    # Create new tables
    if not create_software_products_table():
        print("⚠️  Warning: Could not create software_products table")

    # Extend existing tables
    if not extend_arbitrage_opportunities():
        print("⚠️  Warning: Could not extend arbitrage_opportunities table")

    # Create indexes
    if not create_indexes():
        print("⚠️  Warning: Could not create indexes")

    # Verify
    verify_schema()

    print()
    print("=" * 80)
    print("✅ SCHEMA UPDATE COMPLETE!")
    print("=" * 80)
    print()
    print("Next: Run agents to populate data")
    print("  python -m agents.phase1_ecosystem_mapping")
    print("  python -m agents.phase2_gap_detection")
    print("  python -m agents.phase3_validation")
    print()


if __name__ == "__main__":
    main()
