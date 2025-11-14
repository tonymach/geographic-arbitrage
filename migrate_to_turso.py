#!/usr/bin/env python3
"""
Migrate existing SQLite database to Turso

This script:
1. Creates schema in Turso
2. Migrates existing data from local SQLite
3. Verifies migration success
"""

import asyncio
import sqlite3
from libsql_client import create_client_sync

# Turso credentials
TURSO_URL = "libsql://geographic-arbitrage-tonymach.aws-us-east-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NjMxNTIzOTIsImlkIjoiZGMzMjZiMGItY2RlZS00YzU4LWJkNTEtMWZiYTFmMDViMjE1IiwicmlkIjoiOGVlODQxM2ItOWVlYy00MTFjLWJhNjktOWQwOWNkODJlNmFhIn0.GLgYbi9KunMPoTCuMiR7Ce-SI7I_z_Ggwt4dJPXnYVHb2oAk697DNyUq-znMnA-htrSZesNjetUwX8CjSUw0Bw"

LOCAL_DB = "data/arbitrage.db"


def create_turso_schema(client):
    """Create tables in Turso"""

    print("📋 Creating schema in Turso...")

    # local_platforms table
    client.execute("""
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
        )
    """)

    # arbitrage_opportunities table
    client.execute("""
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
        )
    """)

    # pain_signals table (for future)
    client.execute("""
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
        )
    """)

    print("✅ Schema created successfully!")


def migrate_platforms(local_conn, turso_client):
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

        # Insert (skip id, let Turso auto-generate)
        turso_client.execute("""
            INSERT INTO local_platforms
            (region, country, name, url, type, language, description,
             estimated_users, has_software_discussions, accessibility,
             activity_level, notes, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            data.get('region'),
            data.get('country'),
            data.get('name'),
            data.get('url'),
            data.get('type'),
            data.get('language'),
            data.get('description'),
            data.get('estimated_users'),
            data.get('has_software_discussions', 1),
            data.get('accessibility'),
            data.get('activity_level'),
            data.get('notes'),
            'migrated_from_local'
        ])

        migrated += 1
        print(f"   ✓ Migrated: {data.get('name')} ({data.get('region')})")

    print(f"\n✅ Migrated {migrated} platforms successfully!")
    return migrated


def verify_migration(turso_client, expected_count):
    """Verify migration was successful"""

    print("\n🔍 Verifying migration...")

    result = turso_client.execute("SELECT COUNT(*) FROM local_platforms")
    count = result.rows[0][0]

    print(f"   Expected: {expected_count}")
    print(f"   Found: {count}")

    if count == expected_count:
        print("✅ Migration verified successfully!")
        return True
    else:
        print(f"❌ Migration verification failed! Missing {expected_count - count} platforms")
        return False


def show_sample_data(turso_client):
    """Show sample data from Turso"""

    print("\n📊 Sample data from Turso:")

    result = turso_client.execute("""
        SELECT region, name, language
        FROM local_platforms
        LIMIT 10
    """)

    for row in result.rows:
        print(f"   • {row[0]}: {row[1]} ({row[2]})")


def main():
    print("=" * 80)
    print("TURSO MIGRATION SCRIPT")
    print("=" * 80)
    print()
    print(f"Source: {LOCAL_DB}")
    print(f"Target: {TURSO_URL}")
    print()

    # Connect to local SQLite
    print("🔌 Connecting to local SQLite...")
    local_conn = sqlite3.connect(LOCAL_DB)

    # Connect to Turso
    print("🔌 Connecting to Turso...")
    turso_client = create_client_sync(
        url=TURSO_URL,
        auth_token=TURSO_TOKEN
    )

    # Create schema
    create_turso_schema(turso_client)

    # Migrate data
    migrated_count = migrate_platforms(local_conn, turso_client)

    # Verify migration
    verify_migration(turso_client, migrated_count)

    # Show sample data
    show_sample_data(turso_client)

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
