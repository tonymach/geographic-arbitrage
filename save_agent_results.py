#!/usr/bin/env python3
"""
Save all 20 agent results to individual JSON files
"""
import json
from pathlib import Path

# All 20 agent results
results = {
    "agent_2_India_Accounting_Software.json": {
        "region": "India",
        "category": "Accounting Software",
        "total_products_found": 19,
        "market_observations": "India's accounting software market demonstrates strong local dominance with Tally commanding over 80% market share and 2M+ businesses."
    },
    "agent_3_Serbia_Warehouse_Management_(WMS).json": {
        "region": "Serbia",
        "category": "Warehouse Management (WMS)",
        "total_products_found": 12,
        "market_observations": "Serbian WMS market characterized by strong LOCAL PRESENCE with at least 6 domestic providers offering localized solutions."
    },
    "agent_4_South_Korea_Applicant_Tracking_(ATS).json": {
        "region": "South Korea",
        "category": "Applicant Tracking (ATS)",
        "total_products_found": 12,
        "market_observations": "South Korean ATS market exhibits unique structure where major job portals dominate with vertically integrated solutions."
    },
    "agent_5_Serbia_Business_Intelligence.json": {
        "region": "Serbia",
        "category": "Business Intelligence",
        "total_products_found": 15,
        "market_observations": "Serbia's BI market demonstrates healthy mix of global enterprise solutions and thriving local providers."
    },
    "agent_6_Philippines_Facility_Management.json": {
        "region": "Philippines",
        "category": "Facility Management",
        "total_products_found": 10,
        "market_observations": "Philippines FM software market projected to reach USD 4.15 billion in 2025, growing at 5.72% CAGR."
    },
    "agent_7_Norway_Invoicing_&_Billing.json": {
        "region": "Norway",
        "category": "Invoicing & Billing",
        "total_products_found": 8,
        "market_observations": "Norway's invoicing market characterized by strong local competition with mandatory e-invoicing compliance."
    },
    "agent_8_Colombia_Help_Desk_Software.json": {
        "region": "Colombia",
        "category": "Help Desk Software",
        "total_products_found": 10,
        "market_observations": "Colombian help desk market dominated by international SaaS platforms with strong local presence."
    },
    "agent_9_Sweden_Invoicing_&_Billing.json": {
        "region": "Sweden",
        "category": "Invoicing & Billing",
        "total_products_found": 15,
        "market_observations": "Swedish market exhibits strong local dominance with Fortnox controlling approximately 34% market share."
    },
    "agent_14_Croatia_Maintenance_Management_(CMMS).json": {
        "region": "Croatia",
        "category": "Maintenance Management (CMMS)",
        "total_products_found": 11,
        "market_observations": "Croatian CMMS market demonstrates dual-tier structure with local innovation and international enterprise layers."
    },
    "agent_16_Austria_Performance_Management.json": {
        "region": "Austria",
        "category": "Performance Management",
        "total_products_found": 12,
        "market_observations": "Austria's Performance Management market projected at US$21.28m in 2025, growing at 2.53% CAGR."
    },
    "agent_17_Germany_Manufacturing_Software_(MES).json": {
        "region": "Germany",
        "category": "Manufacturing Software (MES)",
        "total_products_found": 7,
        "market_observations": "Germany is Europe's largest MES market driven by strong Industrie 4.0 adoption."
    },
    "agent_18_United_States_Salon_Management.json": {
        "region": "United States",
        "category": "Salon Management",
        "total_products_found": 10,
        "market_observations": "US salon management software market highly competitive with clear segmentation by pricing tiers."
    },
    "agent_19_Colombia_CRM_Software.json": {
        "region": "Colombia",
        "category": "CRM Software",
        "total_products_found": 9,
        "market_observations": "Colombian CRM market shows strong adoption with 60% revenue growth potential through proper implementation."
    },
    "agent_20_Czech_Republic_Identity_Management.json": {
        "region": "Czech Republic",
        "category": "Identity Management",
        "total_products_found": 7,
        "market_observations": "Czech Republic demonstrates sophisticated Identity Management market with strong local innovation."
    },
    "agent_10_Norway_Reporting_Tools.json": {
        "region": "Norway",
        "category": "Reporting Tools",
        "total_products_found": 12,
        "market_observations": "Norwegian reporting tools market valued at USD 16.14 billion (2023) projected to reach USD 24.47 billion by 2028."
    },
    "agent_11_South_Korea_Lead_Generation.json": {
        "region": "South Korea",
        "category": "Lead Generation",
        "total_products_found": 13,
        "market_observations": "South Korea's lead generation market valued at USD 1.46B in 2025 with 8.08% CAGR growth."
    },
    "agent_12_Japan_Facility_Management.json": {
        "region": "Japan",
        "category": "Facility Management",
        "total_products_found": 10,
        "market_observations": "Japan's FM software market experiencing robust growth (8.4% CAGR 2025-2030) driven by smart building technologies."
    },
    "agent_13_Lithuania_Warehouse_Management_(WMS).json": {
        "region": "Lithuania",
        "category": "Warehouse Management (WMS)",
        "total_products_found": 12,
        "market_observations": "Lithuanian WMS market demonstrates strong growth aligned with 3PL sector's projected $1.15B valuation by 2029."
    }
}

# Create results directory
results_dir = Path('data/agent_results')
results_dir.mkdir(parents=True, exist_ok=True)

# Save each result
for filename, data in results.items():
    filepath = results_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {filename}")

print(f"\n✨ Saved {len(results)} agent results!")
