#!/usr/bin/env python3
"""
Prepare batch 2: Select 50 new combinations
"""
import json
import yaml
from pathlib import Path

# Load work universe
with open('work_universe.yaml') as f:
    universe = yaml.safe_load(f)

regions = universe['regions']
categories = universe['categories']

# Load completed work
with open('data/work_manifest.json') as f:
    manifest = json.load(f)
    completed = set(tuple(c) for c in manifest['completed'])

# Select 100 diverse new combinations 🚀
# Strategy: Round-robin across regions and categories for diversity
selected = []
region_idx = 0
category_idx = 0

while len(selected) < 100:
    region = regions[region_idx % len(regions)]
    category = categories[category_idx % len(categories)]

    combo = (region, category)
    if combo not in completed and combo not in selected:
        selected.append(combo)

    region_idx += 1
    category_idx += 1

    # Prevent infinite loop
    if region_idx > 1000:
        break

print("=" * 80)
print(f"📋 BATCH 2: Selected {len(selected)} new combinations")
print("=" * 80)

for i, (region, category) in enumerate(selected, 1):
    print(f"{i:2d}. {region:25s} → {category}")

# Save to file for reference
batch2_data = {
    "batch_number": 2,
    "agent_count": len(selected),
    "combinations": [[r, c] for r, c in selected]
}

with open('data/batch2_plan.json', 'w') as f:
    json.dump(batch2_data, f, indent=2)

print("=" * 80)
print(f"✅ Saved to data/batch2_plan.json")
print(f"💰 Estimated cost: ${len(selected) * 3} (~$3/agent)")
print("=" * 80)
