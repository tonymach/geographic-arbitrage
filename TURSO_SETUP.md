# 🚀 TURSO SETUP GUIDE

## What You Need To Do (5 minutes):

### Step 1: Pull the Code
```bash
cd ~/code/geographic-arbitrage
git pull origin claude/global-software-arbitrage-map-01DsBgU7nidmdKUxbABhB9Pq
```

### Step 2: Install Dependencies
```bash
pip install libsql-client python-dotenv
```

### Step 3: Set Environment Variables
```bash
# Copy the example env file
cp .env.example .env

# The .env file already has your Turso credentials!
# TURSO_URL=libsql://geographic-arbitrage-tonymach.aws-us-east-1.turso.io
# TURSO_TOKEN=eyJhbGc...
```

### Step 4: Run the Migration
```bash
python migrate_to_turso.py
```

This will:
- ✅ Create schema in Turso
- ✅ Migrate all 45 platforms from local SQLite
- ✅ Verify migration success

### Step 5: Test Turso Connection
```bash
# Quick test
python -c "
import os
from dotenv import load_dotenv
from libsql_client import create_client_sync

load_dotenv()

client = create_client_sync(
    url=os.getenv('TURSO_URL'),
    auth_token=os.getenv('TURSO_TOKEN')
)

result = client.execute('SELECT COUNT(*) FROM local_platforms')
print(f'✅ Turso connected! Platforms in database: {result.rows[0][0]}')
"
```

### Step 6: Open the Turso-Powered Frontend
```bash
# Just open in browser
open explorer_turso.html
```

The frontend will:
- Load data directly from Turso (not local file!)
- Show real-time updates
- Work from ANY computer (no local database needed)

---

## How It Works Now:

### Before (Local SQLite):
```
Agents → Local SQLite → Git commit → Git push → You pull → explorer_db.html
         ↓
      data/arbitrage.db (binary file in git 😢)
```

### After (Turso):
```
Agents → Turso Cloud DB → You see changes INSTANTLY!
                ↓
         explorer_turso.html (queries Turso directly)
```

---

## Testing the Full Pipeline:

### 1. Test that orchestrator writes to Turso:
```bash
# Load env vars
export $(cat .env | xargs)

# Run a quick test
python3 << 'EOF'
import asyncio
from claude_orchestrator import ClaudeOrchestrator

async def test():
    # Orchestrator will auto-detect Turso from env vars
    orch = ClaudeOrchestrator()

    # Save a test platform
    await orch._save_platform_to_turso({
        'region': 'TEST',
        'country': 'TEST',
        'name': 'Test Platform',
        'url': 'https://test.com',
        'type': 'test',
        'language': 'English',
        'description': 'Test entry'
    })

    print("✅ Successfully wrote to Turso!")

asyncio.run(test())
EOF
```

### 2. Verify in Turso CLI:
```bash
turso db shell geographic-arbitrage

# In the shell:
SELECT * FROM local_platforms WHERE region = 'TEST';
```

### 3. Check frontend updates:
Open `explorer_turso.html` and you should see the test platform appear!

---

## Environment Variables Explained:

```bash
# .env file:
TURSO_URL=libsql://geographic-arbitrage-tonymach.aws-us-east-1.turso.io
TURSO_TOKEN=eyJhbGc...

# The orchestrator auto-detects these:
# - If set → uses Turso
# - If not set → falls back to local SQLite
```

---

## Frontend Options:

1. **explorer.html** - Reads from local JSON (static, fast)
2. **explorer_db.html** - Reads from local SQLite via WebAssembly
3. **explorer_turso.html** - Reads from Turso (real-time, cloud!) ← **USE THIS ONE**

---

## What Happens When Agents Run:

```python
# In claude_orchestrator.py:
orchestrator = ClaudeOrchestrator()  # Auto-detects Turso from env

# Spawn 15 agents to discover platforms
platform_map = await orchestrator.spawn_platform_discovery_agents([
    'France', 'Spain', 'Italy', 'Portugal', ...
])

# Each agent discovery is INSTANTLY written to Turso:
await orch._save_platform_to_turso({
    'region': 'France',
    'name': 'FrenchTech',
    ...
})

# YOU SEE IT IMMEDIATELY in explorer_turso.html!
# No git commits needed!
```

---

## Troubleshooting:

### "Cannot connect to Turso"
```bash
# Check your token is valid:
turso db tokens create geographic-arbitrage

# Update .env with new token
```

### "libsql-client not found"
```bash
pip install libsql-client
```

### "Environment variables not loaded"
```bash
# Make sure to load them:
export $(cat .env | xargs)

# Or use python-dotenv:
pip install python-dotenv

# In Python:
from dotenv import load_dotenv
load_dotenv()
```

---

## Next Steps:

1. ✅ Run migration (`python migrate_to_turso.py`)
2. ✅ Test connection
3. ✅ Open `explorer_turso.html`
4. 🚀 Run agents and watch data appear in real-time!

Then we'll add:
- Live WebSocket updates (see data appear as agents discover)
- Opportunity table (gap detection results)
- Pain signals table (forum validation)
- Analytics dashboard

---

**The Vision:** You open `explorer_turso.html` on your laptop, I spawn 40 agents in parallel, and you watch platforms populate in real-time across 40 countries. Zero infrastructure. Pure magic. 🔥
