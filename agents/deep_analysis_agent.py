"""
Deep Analysis Agent - Consultant-Grade Market Intelligence

This agent performs McKinsey/Bain-level deep dives on opportunities:
- Market sizing (TAM/SAM/SOM)
- Competitive landscape analysis
- Pain signal quantification
- Go-to-market strategy
- Risk assessment
- Financial projections

Output: 50-page consultant-grade report per opportunity
"""


def create_deep_market_analysis_prompt(opportunity: dict) -> str:
    """
    Creates prompt for DEEP market analysis

    This is the kind of analysis a top consulting firm would charge $500k+ for
    """

    return f"""
You are a Senior Strategy Consultant performing a DEEP DIVE market analysis.

## Opportunity to Analyze:

{opportunity}

## Your Mission:

Produce a COMPREHENSIVE market analysis at the level of McKinsey, Bain, or BCG.
This should be the kind of report a client would pay $500,000+ for.

## Analysis Framework:

### 1. MARKET SIZING (TAM/SAM/SOM)

**Research and calculate:**

A. **Total Addressable Market (TAM)**
   - How many potential customers exist in {opportunity['target_region']}?
   - Use WebSearch to find:
     * Number of companies in relevant industry
     * Industry statistics and reports
     * Government data on business registrations
     * Trade association membership numbers
   - Calculate total market size if all potential customers adopted

B. **Serviceable Available Market (SAM)**
   - What % of TAM would realistically consider this software?
   - Filter by:
     * Company size (employees, revenue)
     * Industry segment
     * Digital maturity
     * Budget capacity
   - Calculate addressable market size

C. **Serviceable Obtainable Market (SOM)**
   - What market share could realistically be captured in Years 1-3?
   - Consider:
     * Competitive intensity
     * Market entry barriers
     * Sales/marketing capacity
     * Product-market fit timeline
   - Calculate realistic capture: Year 1, Year 2, Year 3

**Output:** Detailed TAM/SAM/SOM calculations with sources

---

### 2. COMPETITIVE LANDSCAPE ANALYSIS

**Research ALL competitors thoroughly:**

A. **Identify ALL Players**
   - Use WebSearch to find:
     * Direct competitors (same category)
     * Indirect competitors (adjacent solutions)
     * Substitutes (manual processes, spreadsheets)
   - Search in local language on local platforms

B. **Competitive Intelligence Per Competitor**
   For EACH competitor, research:
   - Pricing (if public)
   - Feature set
   - Customer reviews (quantity and sentiment)
   - Market positioning
   - Target customer segment
   - Strengths and weaknesses
   - Recent funding/growth signals

C. **Market Share Estimation**
   - Based on review counts, web traffic, social media
   - Estimate each player's market share
   - Identify market leader and challengers

D. **Competitive Gaps**
   - What features do competitors lack?
   - What customer pain do they NOT address?
   - Where is there white space?

**Output:** Competitive positioning map with detailed player profiles

---

### 3. PAIN SIGNAL QUANTIFICATION

**Quantify demand with DATA:**

A. **Forum/Reddit Analysis**
   - Search local forums for pain signals
   - Use WebSearch with local language keywords:
     * "[category] software [country]"
     * "need [category] tool [language]"
     * "[category] problem [country]"
   - For EACH pain signal found:
     * URL and quote
     * Posted date
     * Engagement (upvotes, comments)
     * Pain intensity (1-10)
     * Specific feature requests

B. **Quantify Volume**
   - How many unique pain mentions?
   - Over what time period?
   - Trending up or down?
   - Engagement levels?

C. **Categorize Pain Types**
   - Group pain signals by theme
   - Identify most common frustrations
   - Map to product features that could solve them

**Output:** Pain signal database with 50+ validated signals

---

### 4. GO-TO-MARKET STRATEGY

**Develop actionable GTM plan:**

A. **Product Strategy**
   - Build vs. Localize vs. White-label vs. Partner?
   - Localization requirements:
     * Language translation
     * Currency/tax handling
     * Local integrations
     * Compliance requirements
   - MVP vs. Full feature set?
   - Timeline to market

B. **Pricing Strategy**
   - What would the market pay?
   - Compare to:
     * Competitor pricing (if available)
     * Alternative solution costs
     * Customer budget capacity
   - Recommended pricing: $XX/month/user
   - Freemium vs. Trial vs. Demo?

C. **Distribution Channels**
   - How to acquire customers?
   - Digital marketing (Google Ads, SEO, content)
   - Partnerships (local integrators, consultants)
   - Direct sales?
   - Platform/marketplace listing?

D. **Launch Strategy**
   - Pilot customers (10-20 companies)
   - Industry vertical focus
   - Geographic sub-market (e.g., start in capital city)
   - Timeline: 6 months to pilot, 12 months to scale

**Output:** Detailed GTM playbook

---

### 5. RISK ASSESSMENT

**Identify and quantify risks:**

A. **Market Risks**
   - Economic conditions
   - Currency fluctuations
   - Regulatory changes
   - Market maturity (too early vs. too late)

B. **Competitive Risks**
   - Incumbent response
   - New entrants
   - Price wars
   - Feature parity

C. **Execution Risks**
   - Product-market fit
   - Localization quality
   - Customer acquisition cost
   - Churn/retention

D. **Mitigation Strategies**
   - How to address each risk
   - Contingency plans

**Output:** Risk matrix with mitigation plans

---

### 6. FINANCIAL PROJECTIONS

**Model the opportunity:**

A. **Revenue Model**
   - Year 1-3 customer acquisition
   - Average contract value
   - Revenue projections
   - Growth assumptions

B. **Cost Structure**
   - Product development/localization
   - Sales & marketing
   - Customer support
   - Infrastructure

C. **Unit Economics**
   - CAC (Customer Acquisition Cost)
   - LTV (Lifetime Value)
   - LTV/CAC ratio
   - Payback period

D. **Investment Required**
   - Capital needed to execute
   - Break-even timeline
   - Expected ROI

**Output:** 3-year financial model

---

## Output Format:

Return a COMPREHENSIVE JSON structure:

```json
{{
  "opportunity_summary": {{
    "source_product": "...",
    "source_region": "...",
    "target_region": "...",
    "category": "...",
    "overall_score": 9.2,
    "recommendation": "PURSUE|INVESTIGATE|PASS"
  }},

  "market_sizing": {{
    "tam": {{
      "value_usd": 500000000,
      "methodology": "...",
      "sources": ["...", "..."],
      "confidence": "high|medium|low"
    }},
    "sam": {{
      "value_usd": 150000000,
      "percentage_of_tam": 30,
      "methodology": "...",
      "confidence": "high|medium|low"
    }},
    "som": {{
      "year_1_usd": 500000,
      "year_2_usd": 2000000,
      "year_3_usd": 8000000,
      "market_share_year_3": 5.3,
      "methodology": "...",
      "confidence": "medium|low"
    }},
    "key_assumptions": ["...", "..."],
    "data_sources": ["...", "..."]
  }},

  "competitive_landscape": {{
    "total_competitors": 5,
    "market_concentration": "fragmented|consolidated",
    "competitors": [
      {{
        "name": "...",
        "market_share_estimate": 15.0,
        "pricing": "$XX/month",
        "strengths": ["...", "..."],
        "weaknesses": ["...", "..."],
        "customer_reviews": {{
          "count": 45,
          "avg_rating": 4.0,
          "sentiment": "positive|neutral|negative"
        }},
        "positioning": "...",
        "founded": "2018",
        "funding": "$XM",
        "threat_level": "high|medium|low"
      }}
    ],
    "competitive_gaps": ["...", "..."],
    "barriers_to_entry": ["...", "..."]
  }},

  "pain_signals": {{
    "total_signals_found": 73,
    "search_queries_used": ["...", "..."],
    "platforms_searched": ["...", "..."],
    "signals": [
      {{
        "source": "Wykop",
        "url": "...",
        "posted_date": "2024-11-15",
        "title": "...",
        "quote": "...",
        "pain_type": "missing_feature|poor_usability|high_cost|lack_of_localization",
        "pain_intensity": 8.5,
        "engagement": {{
          "upvotes": 45,
          "comments": 23
        }},
        "feature_request": "..."
      }}
    ],
    "pain_themes": [
      {{
        "theme": "Lack of local language support",
        "frequency": 34,
        "avg_intensity": 7.8
      }}
    ],
    "demand_score": 8.5,
    "confidence": "high"
  }},

  "go_to_market": {{
    "recommended_approach": "build|localize|partner|white_label",
    "product_strategy": {{
      "approach": "...",
      "localization_requirements": ["...", "..."],
      "mvp_features": ["...", "..."],
      "timeline_months": 6
    }},
    "pricing_strategy": {{
      "recommended_price_monthly": 99,
      "currency": "USD",
      "pricing_model": "per_user|flat_rate|usage_based",
      "justification": "...",
      "competitor_comparison": "20% below market average"
    }},
    "distribution_channels": [
      {{
        "channel": "Content Marketing + SEO",
        "cost_estimate": 5000,
        "expected_cac": 200,
        "notes": "..."
      }}
    ],
    "launch_strategy": {{
      "pilot_phase": {{
        "target_customers": 10,
        "duration_months": 3,
        "geography": "Warsaw metro area"
      }},
      "scale_phase": {{
        "year_1_target": 50,
        "year_2_target": 200,
        "year_3_target": 500
      }}
    }}
  }},

  "risk_assessment": {{
    "risks": [
      {{
        "category": "market|competitive|execution|regulatory",
        "risk": "...",
        "probability": "high|medium|low",
        "impact": "high|medium|low",
        "severity_score": 7.5,
        "mitigation": "...",
        "contingency": "..."
      }}
    ],
    "overall_risk_level": "high|medium|low"
  }},

  "financial_projections": {{
    "revenue_model": {{
      "year_1": {{
        "customers": 50,
        "avg_contract_value": 1200,
        "total_revenue": 60000,
        "growth_rate": null
      }},
      "year_2": {{
        "customers": 200,
        "avg_contract_value": 1200,
        "total_revenue": 240000,
        "growth_rate": 300
      }},
      "year_3": {{
        "customers": 500,
        "avg_contract_value": 1300,
        "total_revenue": 650000,
        "growth_rate": 170
      }}
    }},
    "cost_structure": {{
      "year_1": {{
        "product_dev": 50000,
        "sales_marketing": 30000,
        "support_ops": 15000,
        "total": 95000
      }}
    }},
    "unit_economics": {{
      "cac": 200,
      "ltv": 3600,
      "ltv_cac_ratio": 18.0,
      "payback_months": 6,
      "gross_margin": 85
    }},
    "investment_required": 150000,
    "breakeven_month": 18,
    "year_3_roi": 433
  }},

  "strategic_recommendations": [
    "Priority 1: ...",
    "Priority 2: ...",
    "Priority 3: ..."
  ],

  "next_steps": [
    "Immediate (Week 1): ...",
    "Short-term (Month 1): ...",
    "Medium-term (Quarter 1): ..."
  ],

  "confidence_assessment": {{
    "overall_confidence": "high",
    "data_quality": "Strong market data, moderate competitive intelligence",
    "key_uncertainties": ["...", "..."],
    "recommended_validation": ["Interview 20 potential customers", "..."]
  }},

  "executive_summary": "3-4 paragraph summary suitable for CEO/investor presentation"
}}
```

## Instructions:

1. Use WebSearch EXTENSIVELY - this requires REAL research
2. Search in both English and local language
3. Quantify everything - use numbers not adjectives
4. Cite sources for all data
5. Be realistic and data-driven, not optimistic
6. If data isn't available, state assumptions clearly
7. This should be COMPREHENSIVE - think 50-page consultant report

Start your deep analysis now. Use WebSearch to gather real data.
"""


def create_validation_agent_prompt(opportunity: dict, target_region: str) -> str:
    """
    Creates prompt for validation agent that does PRIMARY RESEARCH
    """

    return f"""
You are a Market Validation Analyst doing PRIMARY RESEARCH.

## Opportunity:
{opportunity}

## Your Mission:

Validate this opportunity by ACTUALLY researching the target market.
Don't just theorize - gather REAL data.

### 1. SCRAPE LOCAL PLATFORMS

Use WebFetch to:
- Visit the platforms we discovered
- Find actual product listings
- Count competitors
- Read real reviews
- Get pricing data

### 2. ANALYZE FORUMS DEEPLY

Use WebSearch to:
- Find discussions about this category
- Read actual user pain points
- Count mentions over time
- Assess pain intensity from engagement
- Identify specific feature requests

### 3. QUANTIFY DEMAND

Find real numbers:
- How many companies exist in this vertical?
- How many job postings mention this software?
- What's the search volume for related terms?
- What's the Google Trends data?

### 4. ASSESS COMPETITION

For each competitor:
- Count their reviews
- Read sentiment
- Find their pricing (if public)
- Check their website traffic (SimilarWeb if available)
- Assess product maturity

Return QUANTIFIED validation with sources.
"""

