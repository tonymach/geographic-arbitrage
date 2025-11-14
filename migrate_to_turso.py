#!/usr/bin/env python3
"""
Migrate existing SQLite database to Turso

This script:
1. Creates schema in Turso
2. Migrates existing data from local SQLite
3. Verifies migration success
"""

import sqlite3
import subprocess
import json

DB_NAME = "geographic-arbitrage"
LOCAL_DB = "data/arbitrage.db"


def run_turso_sql(sql):
    """Execute SQL via turso CLI"""
    result = subprocess.run(
        ["turso", "db", "shell", DB_NAME, sql],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Turso error: {result.stderr}")
    return result.stdout


def create_turso_schema():
    """Create tables in Turso"""

    print("📋 Creating schema in Turso...")

    # local_platforms table
    run_turso_sql("""
        CREATE TABLE IF NOT EXISTS local_platforms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT NOT NULL,
            country TEXT NOT NULL,
            name TEXT NOT NULL,
            url TEXT,
            type TEXT,
            language TEXT,
            description TEXT,
            estimated_users TEXT,
            has_software_discussions BOOLEAN DEFAULT 1,
            accessibility TEXT,
            activity_level TEXT,
            notes TEXT,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_source TEXT DEFAULT 'claude_agent'
        );
    """)

    # arbitrage_opportunities table
    run_turso_sql("""
        CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_region TEXT NOT NULL,
            source_product TEXT NOT NULL,
            source_category TEXT NOT NULL,
            source_reviews INTEGER,
            source_rating REAL,
            target_region TEXT NOT NULL,
            target_competition TEXT,
            gap_score REAL,
            opportunity_score REAL,
            reasoning TEXT,
            validated BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # pain_signals table (for future)
    run_turso_sql("""
        CREATE TABLE IF NOT EXISTS pain_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id INTEGER,
            region TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            source_url TEXT,
            posted_date TEXT,
            title TEXT,
            quote TEXT,
            pain_type TEXT,
            pain_intensity REAL,
            engagement_upvotes INTEGER,
            engagement_comments INTEGER,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (opportunity_id) REFERENCES arbitrage_opportunities(id)
        );
    """)

    print("✅ Schema created successfully!")


def escape_sql_string(s):
    """Escape single quotes for SQL"""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def migrate_platforms(local_conn):
    """Migrate platform data from local SQLite to Turso"""

    print("\n📤 Migrating platforms from local DB...")

    # Read from local SQLite
    cursor = local_conn.cursor()
    cursor.execute("SELECT * FROM local_platforms")
    rows = cursor.fetchall()

    # Get column names
    columns = [description[0] for description in cursor.description]

    print(f"   Found {len(rows)} platforms to migrate")

    # Insert into Turso
    migrated = 0
    for row in rows:
        # Convert row to dict
        data = dict(zip(columns, row))

        # Build INSERT statement
        sql = f"""
            INSERT INTO local_platforms
            (region, country, name, url, type, language, description,
             estimated_users, has_software_discussions, accessibility,
             activity_level, notes, data_source)
            VALUES (
                {escape_sql_string(data.get('region'))},
                {escape_sql_string(data.get('country'))},
                {escape_sql_string(data.get('name'))},
                {escape_sql_string(data.get('url'))},
                {escape_sql_string(data.get('type'))},
                {escape_sql_string(data.get('language'))},
                {escape_sql_string(data.get('description'))},
                {escape_sql_string(data.get('estimated_users'))},
                {data.get('has_software_discussions', 1)},
                {escape_sql_string(data.get('accessibility'))},
                {escape_sql_string(data.get('activity_level'))},
                {escape_sql_string(data.get('notes'))},
                'migrated_from_local'
            );
        """

        run_turso_sql(sql)

        migrated += 1
        print(f"   ✓ Migrated: {data.get('name')} ({data.get('region')})")

    print(f"\n✅ Migrated {migrated} platforms successfully!")
    return migrated


def verify_migration(expected_count):
    """Verify migration was successful"""

    print("\n🔍 Verifying migration...")

    result = run_turso_sql("SELECT COUNT(*) FROM local_platforms;")
    # Parse the count from output
    count = int(result.strip().split('\n')[-1])

    print(f"   Expected: {expected_count}")
    print(f"   Found: {count}")

    if count == expected_count:
        print("✅ Migration verified successfully!")
        return True
    else:
        print(f"❌ Migration verification failed! Missing {expected_count - count} platforms")
        return False


def show_sample_data():
    """Show sample data from Turso"""

    print("\n📊 Sample data from Turso:")

    result = run_turso_sql("""
        SELECT region, name, language
        FROM local_platforms
        LIMIT 10;
    """)

    # Parse and display results
    lines = result.strip().split('\n')
    for line in lines[2:]:  # Skip header rows
        if line.strip():
            print(f"   • {line}")


def main():
    print("=" * 80)
    print("TURSO MIGRATION SCRIPT")
    print("=" * 80)
    print()
    print(f"Source: {LOCAL_DB}")
    print(f"Target: {DB_NAME}")
    print()

    # Connect to local SQLite
    print("🔌 Connecting to local SQLite...")
    local_conn = sqlite3.connect(LOCAL_DB)

    # Create schema
    create_turso_schema()

    # Migrate data
    migrated_count = migrate_platforms(local_conn)

    # Verify migration
    verify_migration(migrated_count)

    # Show sample data
    show_sample_data()

    # Close connections
    local_conn.close()

    print()
    print("=" * 80)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Update ClaudeOrchestrator to write to Turso")
    print("2. Update frontend to read from Turso")
    print("3. Test end-to-end flow")


if __name__ == "__main__":
    main()
