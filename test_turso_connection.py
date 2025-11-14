#!/usr/bin/env python3
"""
Test Turso Connection

Quick script to test if Turso is working
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

TURSO_URL = os.getenv('TURSO_URL')
TURSO_TOKEN = os.getenv('TURSO_TOKEN')

print("=" * 80)
print("TURSO CONNECTION TEST")
print("=" * 80)
print(f"\nTURSO_URL: {TURSO_URL}")
print(f"TURSO_TOKEN: {TURSO_TOKEN[:20]}...")
print()

# Test 1: Try with libsql_client
print("Test 1: Using libsql-client...")
try:
    from libsql_client import create_client

    client = create_client(
        url=TURSO_URL,
        auth_token=TURSO_TOKEN
    )

    async def test_query():
        result = await client.execute("SELECT 1 as test")
        print(f"✅ libsql-client works! Result: {result.rows}")
        return True

    asyncio.run(test_query())
except Exception as e:
    print(f"❌ libsql-client failed: {e}")
    print()

# Test 2: Try with HTTP client (requests)
print("\nTest 2: Using direct HTTP API...")
try:
    import requests
    import json

    # Turso HTTP API endpoint
    # URL format: libsql://database-name.turso.io -> https://database-name.turso.io
    http_url = TURSO_URL.replace('libsql://', 'https://')

    headers = {
        'Authorization': f'Bearer {TURSO_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Simple query
    payload = {
        'statements': ['SELECT COUNT(*) as count FROM local_platforms']
    }

    response = requests.post(http_url, headers=headers, json=payload, timeout=10)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ HTTP API works! Response: {result}")
    else:
        print(f"❌ HTTP API failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ HTTP API failed: {e}")
    print()

# Test 3: Check environment
print("\nTest 3: Environment check...")
print(f"✓ TURSO_URL is set: {bool(TURSO_URL)}")
print(f"✓ TURSO_TOKEN is set: {bool(TURSO_TOKEN)}")
print(f"✓ Token length: {len(TURSO_TOKEN) if TURSO_TOKEN else 0} chars")

print("\n" + "=" * 80)
print("DIAGNOSTIC INFO")
print("=" * 80)
print("""
If libsql-client is failing with 505 errors, try:

1. Regenerate Turso token:
   turso db tokens create geographic-arbitrage

2. Update .env file with new token

3. Try connecting with turso CLI:
   turso db shell geographic-arbitrage

4. Check if database exists:
   turso db list

5. Alternative: Use HTTP API instead of WebSocket
""")
