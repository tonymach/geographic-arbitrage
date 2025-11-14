#!/usr/bin/env python3
"""
Test WebSocket Turso Client (properly with asyncio)
"""

import asyncio
import os
from dotenv import load_dotenv
from libsql_client import create_client

load_dotenv()

TURSO_URL = os.getenv('TURSO_URL')
TURSO_TOKEN = os.getenv('TURSO_TOKEN')


async def test_ws_client():
    print("=" * 80)
    print("TESTING TURSO WEBSOCKET CLIENT")
    print("=" * 80)
    print()

    print(f"URL: {TURSO_URL}")
    print(f"Token: {TURSO_TOKEN[:20]}...")
    print()

    # Create client
    print("Creating WebSocket client...")
    try:
        client = create_client(url=TURSO_URL, auth_token=TURSO_TOKEN)
        print("✅ Client created")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return
    print()

    # Test 1: Simple query
    print("Test 1: SELECT 1...")
    try:
        result = await client.execute("SELECT 1 as test")
        print(f"✅ Result: {result}")
        print(f"   Rows: {result.rows}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    print()

    # Test 2: Count platforms
    print("Test 2: Count local_platforms...")
    try:
        result = await client.execute("SELECT COUNT(*) as count FROM local_platforms")
        count = result.rows[0]['count']
        print(f"✅ Found {count} platforms")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    print()

    print("=" * 80)
    print("✅ WEBSOCKET CLIENT WORKS FROM SANDBOX!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_ws_client())
