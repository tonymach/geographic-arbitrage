#!/usr/bin/env python3
"""Update work manifest with all 20 completed combinations"""
import json
from pathlib import Path
from datetime import datetime

manifest_file = Path('data/work_manifest.json')

# All 20 completed combinations
completed = [
    ["Turkey", "Fleet Management"],
    ["India", "Accounting Software"],
    ["Serbia", "Warehouse Management (WMS)"],
    ["South Korea", "Applicant Tracking (ATS)"],
    ["Serbia", "Business Intelligence"],
    ["Philippines", "Facility Management"],
    ["Norway", "Invoicing & Billing"],
    ["Colombia", "Help Desk Software"],
    ["Sweden", "Invoicing & Billing"],
    ["Croatia", "Maintenance Management (CMMS)"],
    ["Austria", "Performance Management"],
    ["Germany", "Manufacturing Software (MES)"],
    ["United States", "Salon Management"],
    ["Colombia", "CRM Software"],
    ["Czech Republic", "Identity Management"],
    ["Norway", "Reporting Tools"],
    ["South Korea", "Lead Generation"],
    ["Japan", "Facility Management"],
    ["Lithuania", "Warehouse Management (WMS)"],
    ["Poland", "Construction Management"]
]

# Save manifest
manifest_data = {
    "last_updated": datetime.now().isoformat(),
    "total_completed": len(completed),
    "completed": completed
}

manifest_file.parent.mkdir(exist_ok=True)
with open(manifest_file, 'w') as f:
    json.dump(manifest_data, f, indent=2)

print(f"✅ Updated work manifest: {len(completed)} combinations completed")
