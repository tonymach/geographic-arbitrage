#!/usr/bin/env python3
"""
Test HTTP Turso Client

Quick test to verify HTTP client works before running full flow
"""

import asyncio
import os
from dotenv import load_dotenv
from utils.turso_http_client import create_http_client

load_dotenv()

TURSO_URL = os.getenv('TURSO_URL')
TURSO_TOKEN = os.getenv('TURSO_TOKEN')


async def test_http_client():
    print("=" * 80)
    print("TESTING TURSO HTTP CLIENT")
    print("=" * 80)
    print()

    # Create client
    print("Creating HTTP client...")
    client = create_http_client(TURSO_URL, TURSO_TOKEN)
    print()

    # Test 1: Simple query
    print("Test 1: Simple SELECT query...")
    try:
        result = await client.execute("SELECT 1 as test")
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    print()

    # Test 2: Count platforms
    print("Test 2: Count local_platforms...")
    try:
        result = await client.execute("SELECT COUNT(*) as count FROM local_platforms")
        rows = result.get('rows', [])
        if rows:
            count = rows[0][0]
            print(f"✅ Found {count} platforms in database")
        else:
            print("⚠️  No rows returned")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    print()

    # Test 3: Parameterized query (INSERT)
    print("Test 3: Parameterized INSERT...")
    try:
        await client.execute(
            "INSERT INTO local_platforms (region, country, name, url, type, language, description, data_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ['Test Region', 'Test Country', 'Test Platform', 'https://test.com', 'test', 'English', 'Test description', 'http_test']
        )
        print("✅ INSERT successful")

        # Verify it was inserted
        result = await client.execute("SELECT COUNT(*) as count FROM local_platforms WHERE data_source = 'http_test'")
        count = result['rows'][0][0]
        print(f"✅ Verified: {count} test record(s) found")

        # Clean up
        await client.execute("DELETE FROM local_platforms WHERE data_source = 'http_test'")
        print("✅ Cleanup successful")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    print()

    print("=" * 80)
    print("✅ ALL TESTS PASSED - HTTP CLIENT IS WORKING!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Run: python update_schema.py")
    print("2. Run: python run_complete_flow.py")


if __name__ == "__main__":
    asyncio.run(test_http_client())
