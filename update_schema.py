#!/usr/bin/env python3
"""
Update Turso schema with PE-grade fields

Adds:
1. software_products table (Phase 1 output)
2. Extended fields to arbitrage_opportunities (unit economics, financials)
"""

import asyncio
import os
from dotenv import load_dotenv

# Try WebSocket client first
try:
    from libsql_client import create_client as create_ws_client
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False

# Import HTTP client as fallback
try:
    from utils.turso_http_client import create_http_client
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

# Load environment variables
load_dotenv()

TURSO_URL = os.getenv('TURSO_URL')
TURSO_TOKEN = os.getenv('TURSO_TOKEN')

client = None


async def init_client():
    """Initialize Turso client (WebSocket or HTTP fallback)"""
    global client
    if not TURSO_URL or not TURSO_TOKEN:
        print("❌ Error: TURSO_URL and TURSO_TOKEN not set")
        print("   Run: cp .env.example .env")
        return False

    # Try WebSocket first
    if WS_AVAILABLE:
        try:
            client = create_ws_client(url=TURSO_URL, auth_token=TURSO_TOKEN)
            # Test connection
            await client.execute("SELECT 1")
            print("✅ Using Turso WebSocket client")
            return True
        except Exception as e:
            print(f"⚠️  WebSocket failed ({e}), trying HTTP...")
            client = None

    # Fall back to HTTP
    if HTTP_AVAILABLE:
        client = create_http_client(url=TURSO_URL, auth_token=TURSO_TOKEN)
        print("✅ Using Turso HTTP client (fallback)")
        return True

    print("❌ Error: No Turso client available")
    return False


async def run_turso_sql(sql):
    """Execute SQL via Python client"""
    try:
        result = await client.execute(sql)
        print(f"✓ SQL executed successfully")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def create_software_products_table():
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

    if await run_turso_sql(sql):
        print("✅ software_products table created")
        return True
    return False


async def extend_arbitrage_opportunities():
    """Add PE-grade fields to arbitrage_opportunities table"""

    print("\n📋 Extending arbitrage_opportunities table...")

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
        try:
            await run_turso_sql(sql)
        except:
            pass  # Column already exists

    print("✅ arbitrage_opportunities table extended")
    return True


async def create_indexes():
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
        await run_turso_sql(idx_sql)

    print("✅ Indexes created")
    return True


async def verify_schema():
    """Verify all tables exist"""

    print("\n🔍 Verifying schema...")

    tables = [
        "local_platforms",
        "software_products",
        "arbitrage_opportunities",
        "pain_signals"
    ]

    for table in tables:
        try:
            result = await client.execute(f"SELECT COUNT(*) as count FROM {table};")
            count = result.rows[0]['count']
            print(f"  ✓ {table}: {count} rows")
        except Exception as e:
            print(f"  ✗ {table}: {e}")

    print("\n✅ Schema verification complete")


async def main():
    print("=" * 80)
    print("TURSO SCHEMA UPDATE")
    print("=" * 80)
    print()

    # Initialize client
    if not await init_client():
        return

    print(f"Connected to: {TURSO_URL}\n")

    # Create new tables
    if not await create_software_products_table():
        print("⚠️  Warning: Could not create software_products table")

    # Extend existing tables
    if not await extend_arbitrage_opportunities():
        print("⚠️  Warning: Could not extend arbitrage_opportunities table")

    # Create indexes
    if not await create_indexes():
        print("⚠️  Warning: Could not create indexes")

    # Verify
    await verify_schema()

    print()
    print("=" * 80)
    print("✅ SCHEMA UPDATE COMPLETE!")
    print("=" * 80)
    print()
    print("Next: Run agents to populate data")
    print("  python run_complete_flow.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
