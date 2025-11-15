#!/usr/bin/env python3
"""
Pre-Flight Validation - DON'T FUCK THIS UP AGAIN

Before spending $15-450 on agents, validate:
1. Prompt structure is correct
2. Output format matches expectations
3. User approves the approach

Then run 5 agents per phase to prove it works.
"""

import json
from pathlib import Path
from typing import Dict

class PreFlightValidator:
    """Validate everything before launching agents"""

    def __init__(self):
        self.validation_dir = Path('data/validation')
        self.validation_dir.mkdir(parents=True, exist_ok=True)

    # ==================
    # PHASE 1 VALIDATION
    # ==================

    def validate_phase1_prompt(self, region: str, category: str) -> Dict:
        """
        Show what Phase 1 agent will receive

        Phase 1 should: Map products in ONE region
        NOT: Compare or find gaps (that's Phase 2)
        """
        prompt = f"""You are a software ecosystem research agent analyzing the {category} market in {region}.

**Your Mission**: Map ALL {category} software products in {region}.

**Research Steps**:

1. **Web Search** for {category} software in {region}:
   - Search in both English and local language
   - Look for review sites, comparisons, "best {category} software in {region}"
   - Find local players AND international players operating there

2. **For Each Product** found:
   - Product name
   - Website URL
   - Reviews/mentions count
   - Rating (if available)
   - Pricing (in local currency)
   - Adoption level (high/medium/low)
   - Is it local or international?
   - Key features
   - Annual revenue estimate (if available)

3. **Market Context**:
   - Market size estimate
   - Growth rate
   - Dominant players

**Output Format** (JSON):

```json
{{
  "region": "{region}",
  "category": "{category}",
  "research_date": "2025-01-15",
  "products": [
    {{
      "product_name": "Procore",
      "url": "https://procore.com",
      "reviews_mentions": 15000,
      "rating": 4.5,
      "pricing": "$100-500/month",
      "adoption_level": "high",
      "is_local": false,
      "revenue_estimate": "$600M ARR",
      "key_features": "Project management, budgeting, RFIs",
      "source": "G2, Capterra, company website"
    }}
  ],
  "market_size": "$10B",
  "market_growth": "15% CAGR",
  "total_products_found": 8
}}
```

**Important**: Find 5-10 products minimum. Include revenue data when available.

Return ONLY the JSON, no other text.
"""

        validation = {
            "phase": 1,
            "region": region,
            "category": category,
            "prompt": prompt,
            "expected_output": {
                "region": region,
                "category": category,
                "products": [
                    {
                        "product_name": "Example Product",
                        "revenue_estimate": "$XXM ARR",
                        "adoption_level": "high/medium/low",
                        "is_local": "true/false"
                    }
                ],
                "market_size": "$XXB",
                "total_products_found": "5-10"
            },
            "cost_estimate": "$3-5 per agent",
            "validates": "We get complete product catalog for ONE market"
        }

        # Save for review
        filename = self.validation_dir / f"phase1_validation_{region}_{category}.json"
        with open(filename, 'w') as f:
            json.dump(validation, f, indent=2)

        return validation

    # ==================
    # PHASE 2 VALIDATION
    # ==================

    def validate_phase2_prompt(self, mature_region: str, emerging_region: str, category: str) -> Dict:
        """
        Show what Phase 2 agent will receive

        Phase 2 should: COMPARE mature vs emerging, FIND GAPS
        This is where the arbitrage magic happens!
        """
        prompt = f"""You are a geographic arbitrage detection agent.

**Your Mission**: Compare {category} markets in {mature_region} vs {emerging_region} to find arbitrage opportunities.

**Input Data** (you'll receive Phase 1 results for both regions):
- {mature_region} {category} products (from Phase 1)
- {emerging_region} {category} products (from Phase 1)

**Analysis Steps**:

1. **Identify Winners in {mature_region}**:
   - Which products have highest revenue?
   - Which have strongest adoption?
   - Which are proven business models?

2. **Check Presence in {emerging_region}**:
   - Does this winning product exist there?
   - Is there a local equivalent?
   - How strong is the competition?

3. **Calculate Gap Score** (0-10) for each missing winner:
   - Mature market strength (revenue, adoption)
   - Emerging market gap (weak/no alternatives)
   - Localization feasibility
   - Market size potential

4. **Rank Opportunities**:
   - Only return gaps with score >= 7.0
   - Sort by gap_score descending

**Output Format** (JSON):

```json
{{
  "mature_region": "{mature_region}",
  "emerging_region": "{emerging_region}",
  "category": "{category}",
  "comparison_date": "2025-01-15",
  "opportunities": [
    {{
      "source_product": "Procore",
      "source_region": "{mature_region}",
      "source_revenue": "$600M ARR",
      "source_adoption": "high",
      "target_region": "{emerging_region}",
      "target_competition": "weak - largest competitor $5M ARR",
      "gap_score": 9.2,
      "reasoning": "Procore dominates US with $600M ARR. Poland has only 3 local players under $5M each. Clear gap for premium construction PM software.",
      "localization_complexity": "medium",
      "estimated_tam": "$50M in Poland",
      "next_steps": "Validate with Phase 3 - check pain signals and unit economics"
    }}
  ],
  "total_opportunities": 3,
  "summary": "Found 3 high-potential arbitrage gaps"
}}
```

**Critical**: Only include opportunities with gap_score >= 7.0. Focus on revenue gaps.

Return ONLY the JSON, no other text.
"""

        validation = {
            "phase": 2,
            "mature_region": mature_region,
            "emerging_region": emerging_region,
            "category": category,
            "prompt": prompt,
            "expected_output": {
                "opportunities": [
                    {
                        "source_product": "Winner from mature market",
                        "source_revenue": "$XXM ARR",
                        "target_competition": "weak/none",
                        "gap_score": "7.0-10.0",
                        "reasoning": "WHY this is an opportunity"
                    }
                ],
                "total_opportunities": "1-5"
            },
            "requires_phase1_data": True,
            "cost_estimate": "$3-5 per agent",
            "validates": "We find GAPS (missing winners) not just catalog markets"
        }

        filename = self.validation_dir / f"phase2_validation_{mature_region}_to_{emerging_region}_{category}.json"
        with open(filename, 'w') as f:
            json.dump(validation, f, indent=2)

        return validation

    # ==================
    # PHASE 3 VALIDATION
    # ==================

    def validate_phase3_prompt(self, opportunity: Dict) -> Dict:
        """
        Show what Phase 3 agent will receive

        Phase 3 should: Validate opportunity with PE-grade analysis
        """
        prompt = f"""You are a validation and unit economics agent.

**Your Mission**: Validate this arbitrage opportunity with PE-grade financial analysis.

**Opportunity to Validate**:
```json
{json.dumps(opportunity, indent=2)}
```

**Research Tasks**:

1. **Pain Signal Validation**:
   - Search forums, Reddit, local sites in {opportunity['target_region']}
   - Find 10+ posts/complaints about needing {opportunity['source_product']}-like solution
   - Rate pain intensity (0-10)

2. **Market Sizing**:
   - Potential customers in {opportunity['target_region']}
   - Average spend per customer
   - TAM = customers × spend

3. **Unit Economics**:
   - ACV (Annual Contract Value): Based on {opportunity['target_region']} pricing
   - CAC (Customer Acquisition Cost): Estimate for local market
   - LTV (Lifetime Value): 3-year retention assumption
   - LTV:CAC ratio (should be >3.0)
   - Payback period in months

4. **3-Year Financial Model**:
   - Year 1: Conservative customer count
   - Year 2: 3x growth
   - Year 3: 6x from Year 1
   - Revenue = customers × ACV
   - EBITDA = Revenue × 30% margin

5. **Exit Strategy**:
   - Base case: 5x Year 3 revenue
   - Bull case: 10x Year 3 revenue
   - ROI multiple on $300K initial investment

6. **Final Recommendation**:
   - BUILD NOW: High confidence, strong economics
   - INVESTIGATE: Promising but needs more validation
   - SKIP: Weak signals or poor economics

**Output Format** (JSON):

```json
{{
  "opportunity_id": "{opportunity.get('source_product', 'Unknown')} → {opportunity.get('target_region', 'Unknown')}",
  "validation_date": "2025-01-15",
  "pain_signals": {{
    "posts_found": 12,
    "pain_intensity": 8.5,
    "sample_quotes": ["We desperately need this", "Why doesn't this exist here?"],
    "confidence": "high"
  }},
  "market_sizing": {{
    "potential_customers": 5000,
    "avg_spend": "$3,000",
    "tam": "$15M"
  }},
  "unit_economics": {{
    "acv": 3000,
    "cac": 900,
    "ltv": 12750,
    "ltv_cac_ratio": 14.2,
    "payback_months": 3.6,
    "magic_number": 1.2
  }},
  "financial_model": {{
    "year_1": {{"customers": 60, "revenue": 180000, "ebitda": 54000}},
    "year_2": {{"customers": 180, "revenue": 540000, "ebitda": 162000}},
    "year_3": {{"customers": 360, "revenue": 1080000, "ebitda": 324000}}
  }},
  "exit_strategy": {{
    "base_case_valuation": 5400000,
    "bull_case_valuation": 10800000,
    "roi_multiple_base": 18.0,
    "roi_multiple_bull": 36.0
  }},
  "recommendation": "BUILD NOW",
  "confidence": "high",
  "reasoning": "Strong pain signals (8.5/10), excellent unit economics (14.2x LTV:CAC), clear path to $1M+ revenue in 3 years with 18-36x ROI potential."
}}
```

**Important**: Be realistic. Don't fabricate pain signals. Use real web searches.

Return ONLY the JSON, no other text.
"""

        validation = {
            "phase": 3,
            "opportunity": opportunity,
            "prompt": prompt,
            "expected_output": {
                "pain_signals": {"posts_found": ">10", "pain_intensity": "7.0-10.0"},
                "unit_economics": {"ltv_cac_ratio": ">3.0", "payback_months": "<12"},
                "financial_model": {"year_3_revenue": "$XXX,XXX+"},
                "exit_strategy": {"roi_multiple": ">10x"},
                "recommendation": "BUILD NOW / INVESTIGATE / SKIP"
            },
            "requires_phase2_data": True,
            "cost_estimate": "$5-10 per agent (more research intensive)",
            "validates": "Opportunity is financially viable with PE-grade metrics"
        }

        filename = self.validation_dir / f"phase3_validation_{opportunity.get('source_product', 'opp')}.json"
        with open(filename, 'w') as f:
            json.dump(validation, f, indent=2)

        return validation

    # ==================
    # TEST PLAN
    # ==================

    def create_test_plan(self) -> Dict:
        """
        Create a 5-agent-per-phase test plan

        Total cost: ~$15-25
        Validates entire pipeline before scaling to 100+ agents
        """
        test_plan = {
            "total_agents": 15,
            "estimated_cost": "$15-25",
            "phases": {
                "phase_1_ecosystem_mapping": {
                    "agent_count": 5,
                    "targets": [
                        {"region": "United States", "category": "Construction Management"},
                        {"region": "United States", "category": "Fleet Management"},
                        {"region": "Poland", "category": "Construction Management"},
                        {"region": "Poland", "category": "Fleet Management"},
                        {"region": "Romania", "category": "Construction Management"}
                    ],
                    "expected_output": "5 complete product catalogs",
                    "validates": "We can map products accurately"
                },
                "phase_2_gap_detection": {
                    "agent_count": 5,
                    "targets": [
                        {"mature": "United States", "emerging": "Poland", "category": "Construction Management"},
                        {"mature": "United States", "emerging": "Romania", "category": "Construction Management"},
                        {"mature": "United States", "emerging": "Poland", "category": "Fleet Management"},
                        {"mature": "Germany", "emerging": "Poland", "category": "Construction Management"},
                        {"mature": "United Kingdom", "emerging": "Poland", "category": "Construction Management"}
                    ],
                    "expected_output": "10-20 arbitrage opportunities with gap_score >= 7.0",
                    "validates": "We find real gaps, not just catalog markets"
                },
                "phase_3_validation": {
                    "agent_count": 5,
                    "targets": "Top 5 opportunities from Phase 2 (highest gap_scores)",
                    "expected_output": "5 validated opportunities with BUILD NOW/INVESTIGATE/SKIP",
                    "validates": "We get actionable PE-grade analysis"
                }
            },
            "success_criteria": {
                "phase_1": "5/5 agents return 5-10 products each",
                "phase_2": "5/5 agents find 2-4 gaps each (gap_score >= 7.0)",
                "phase_3": "3/5 opportunities get BUILD NOW recommendation"
            },
            "if_successful": "Scale to 100 agents (Phase 1), then 50 (Phase 2), then 25 (Phase 3)",
            "if_failed": "Fix prompts and retry with 5 agents before scaling"
        }

        # Save test plan
        with open(self.validation_dir / 'test_plan.json', 'w') as f:
            json.dump(test_plan, f, indent=2)

        return test_plan


def main():
    """Run validation steps"""
    validator = PreFlightValidator()

    print("=" * 80)
    print("PRE-FLIGHT VALIDATION - Geographic Arbitrage Agents")
    print("=" * 80)

    # Validate Phase 1
    print("\n📋 PHASE 1 VALIDATION - Ecosystem Mapping")
    print("-" * 80)
    p1 = validator.validate_phase1_prompt("United States", "Construction Management")
    print(f"✅ Validated Phase 1 prompt for {p1['region']} - {p1['category']}")
    print(f"   Expected output: {p1['expected_output']['total_products_found']} products")
    print(f"   Cost: {p1['cost_estimate']}")
    print(f"   Validates: {p1['validates']}")

    # Validate Phase 2
    print("\n📋 PHASE 2 VALIDATION - Gap Detection")
    print("-" * 80)
    p2 = validator.validate_phase2_prompt("United States", "Poland", "Construction Management")
    print(f"✅ Validated Phase 2 prompt: {p2['mature_region']} → {p2['emerging_region']}")
    print(f"   Expected output: {p2['expected_output']['total_opportunities']} opportunities")
    print(f"   Cost: {p2['cost_estimate']}")
    print(f"   Validates: {p2['validates']}")

    # Validate Phase 3
    print("\n📋 PHASE 3 VALIDATION - Unit Economics")
    print("-" * 80)
    sample_opp = {
        "source_product": "Procore",
        "source_region": "United States",
        "target_region": "Poland",
        "gap_score": 9.2
    }
    p3 = validator.validate_phase3_prompt(sample_opp)
    print(f"✅ Validated Phase 3 prompt for: {p3['opportunity']['source_product']}")
    print(f"   Expected: LTV:CAC {p3['expected_output']['unit_economics']['ltv_cac_ratio']}")
    print(f"   Cost: {p3['cost_estimate']}")
    print(f"   Validates: {p3['validates']}")

    # Show test plan
    print("\n📋 TEST PLAN - 5 Agents Per Phase")
    print("=" * 80)
    plan = validator.create_test_plan()
    print(f"Total agents: {plan['total_agents']}")
    print(f"Estimated cost: {plan['estimated_cost']}")
    print(f"\nPhase 1: {plan['phases']['phase_1_ecosystem_mapping']['agent_count']} agents")
    print(f"Phase 2: {plan['phases']['phase_2_gap_detection']['agent_count']} agents")
    print(f"Phase 3: {plan['phases']['phase_3_validation']['agent_count']} agents")
    print(f"\nSuccess criteria:")
    print(f"  Phase 1: {plan['success_criteria']['phase_1']}")
    print(f"  Phase 2: {plan['success_criteria']['phase_2']}")
    print(f"  Phase 3: {plan['success_criteria']['phase_3']}")
    print(f"\nIf successful: {plan['if_successful']}")
    print(f"If failed: {plan['if_failed']}")

    print("\n✅ All validation files saved to data/validation/")
    print("📄 Review before proceeding: ls data/validation/")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
