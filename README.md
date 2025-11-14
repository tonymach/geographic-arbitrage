# Global Software Arbitrage

**Discover software opportunities across global markets by finding what's HUGE in one region but missing in another.**

## The Core Insight

Markets digitalize at different speeds. Software that dominates mature markets (US, UK, Germany) often doesn't exist yet in emerging markets (Eastern Europe, Southeast Asia) - even when those markets show clear demand signals.

**Example:**
- Coworking software (Nexudus) has 847 reviews in UK
- Romania has <3 coworking solutions with 12 total reviews
- But Romania opened 47 coworking spaces in the last 2 years
- **= Arbitrage Opportunity**

This system finds these opportunities automatically across:
- **30+ regions globally**
- **25+ software categories**
- **Validated with government contracts and pain signals**

## What Makes This Different

### Traditional Approach (US-Centric)
- Scrape G2 and Capterra
- Assume global platform coverage
- Miss local market dynamics

### This System (Globally Intelligent)
1. **Discovers local platforms first** (Phase 0)
   - Romania: Lista Firmelor, Startarium
   - Japan: ITreview, Boxil
   - Germany: OMR Reviews
   - Every region has platforms locals actually use

2. **Maps regional ecosystems** (Phases 1-2)
   - What companies are thriving?
   - What software do they use?
   - What categories dominate?

3. **Cross-references for gaps** (Phase 3)
   - Software strong in Region A, weak in Region B
   - But Region B shows demand signals

4. **Validates opportunities** (Phase 4)
   - Government contracts
   - Reddit/forum pain signals
   - Company needs
   - Job market signals

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER ORCHESTRATOR                       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐      ┌──────────────┐
│   PHASE 0    │    │   PHASE 1    │      │   PHASE 2    │
│   Platform   │───▶│   Company    │─────▶│   Software   │
│  Discovery   │    │   Mapping    │      │   Mapping    │
└──────────────┘    └──────────────┘      └──────────────┘
                                                   │
                    ┌──────────────────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │      PHASE 3         │
        │  Cross-Reference     │
        │   Gap Detection      │
        └──────────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │      PHASE 4         │
        │    Validation        │
        │ (Contracts + Pain)   │
        └──────────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │   OPPORTUNITIES      │
        │   Ranked & Exported  │
        └──────────────────────┘
```

## Phases

### Phase 0: Platform Discovery
**Discovers local platforms per region**

For each region:
- Searches for local review sites, directories, tech media
- Finds platforms that locals actually use
- Validates accessibility and scrapeability
- Stores in database

**Output:** Platform map
```json
{
  "Romania": [
    {"name": "Lista Firmelor", "type": "business_directory", "language": "Romanian"},
    {"name": "Startarium", "type": "startup_directory"}
  ],
  "Japan": [
    {"name": "ITreview", "type": "software_reviews", "language": "Japanese"},
    {"name": "Boxil", "type": "saas_comparison"}
  ]
}
```

### Phase 1: Company Mapping
**Maps successful companies per region**

For each region:
- Searches for top companies (revenue, growth, funding)
- Identifies industries and verticals
- Infers software needs based on company size/industry
- Stores in database

**Output:** Company map with tech needs

### Phase 2: Software Ecosystem Mapping
**Maps software products per region**

For each region and category:
- Searches global platforms (G2, Capterra) filtered by region
- Searches local platforms discovered in Phase 0
- Calculates adoption scores
- Stores in database

**Output:** Software ecosystem map
```json
{
  "Romania": {
    "popular_products": {
      "Coworking & Space Management": [
        {"name": "Nexudus", "reviews": 847, "rating": 4.6, "adoption_score": 9.2},
        {"name": "Local Tool", "reviews": 12, "rating": 4.0, "adoption_score": 1.5}
      ]
    }
  }
}
```

### Phase 3: Cross-Region Gap Detection
**Finds arbitrage opportunities**

For each region pair:
- Compares software ecosystems
- Identifies gaps (strong in A, weak in B)
- Calculates gap scores
- Ranks opportunities

**Output:** Ranked opportunities
```json
{
  "opportunity": "Coworking Management Software",
  "source_region": "United Kingdom",
  "source_product": "Nexudus",
  "source_reviews": 847,
  "target_region": "Romania",
  "target_competition_level": 1,
  "gap_score": 8.7,
  "opportunity_score": 9.1
}
```

### Phase 4: Validation (TODO)
**Validates opportunities with demand signals**

For each opportunity:
- Searches government contracts
- Analyzes Reddit/forum pain signals
- Checks job postings
- Validates company needs

## Quick Start

### Installation

```bash
# Clone repo
git clone https://github.com/yourusername/global-software-arbitrage.git
cd global-software-arbitrage

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from utils.db import init_database; init_database()"
```

### Run Pipeline

```bash
# Test run on Romania and Japan
python main.py --test

# Run on specific regions
python main.py --regions Romania Poland Germany

# Full run (all regions)
python main.py

# Verbose logging
python main.py --test --verbose
```

### Output

Results are exported to:
- `data/results/opportunities.json` - Full opportunity data
- `data/results/opportunities.txt` - Human-readable summary
- `data/results/pipeline_summary.json` - Pipeline execution summary
- `data/discovered_platforms.json` - Discovered platforms
- `data/companies/company_map.json` - Company data
- `data/software_ecosystems/ecosystem_map.json` - Software ecosystem data

## Configuration

Edit `config.yaml` to customize:

```yaml
# Regions to process
regions:
  eastern_europe:
    - Romania
    - Poland
    - Czech Republic

# Platform discovery settings
platform_discovery:
  max_platforms_per_region: 15
  seed_platforms:
    regional:
      romania:
        - name: "Lista Firmelor"
          url: "https://www.listafirme.ro"

# Gap detection thresholds
gap_detection:
  min_source_reviews: 100
  min_gap_score: 6.0
  max_target_competition_level: 3

# Categories to track
categories:
  - "Project Management"
  - "CRM & Sales"
  - "Coworking & Space Management"
  # ... 20+ more
```

## Database Schema

SQLite database with 8 tables:

1. **local_platforms** - Discovered platforms per region
2. **companies** - Successful companies per region
3. **software_products** - Software products with adoption scores
4. **arbitrage_opportunities** - Detected gaps with scores
5. **contracts** - Government contracts for validation
6. **pain_signals** - Reddit/forum pain signals
7. **tech_stacks** - Company technology usage
8. **job_postings** - Job market signals

## Agents

### Platform Discovery Agent
Discovers local platforms per region using web search and validation.

### Company Mapper Agent
Maps successful companies using local rankings, Crunchbase, LinkedIn, etc.

### Software Mapper Agent
Maps software ecosystems using both global and local platforms.

### Cross Reference Agent
Finds gaps by comparing software adoption across regions.

### Master Orchestrator
Coordinates all agents and manages data flow.

## Example Opportunities

### 1. Coworking Management Software
- **Source:** UK (Nexudus: 847 reviews, 4.6/5)
- **Target:** Romania (1 competitor, 12 reviews)
- **Validation:** 47 new coworking spaces, €450K in government contracts
- **Opportunity Score:** 9.1/10

### 2. Construction Management Software
- **Source:** Germany (PlanRadar: 1200 reviews)
- **Target:** Poland (weak competition)
- **Validation:** Major construction boom, government infrastructure projects
- **Opportunity Score:** 8.5/10

### 3. HR Management Software
- **Source:** Singapore (SmartHR: 800 reviews)
- **Target:** Thailand (minimal solutions)
- **Validation:** Growing startup ecosystem, English proficiency
- **Opportunity Score:** 8.2/10

## Roadmap

### Current (v0.1)
- ✅ Phase 0: Platform Discovery
- ✅ Phase 1: Company Mapping
- ✅ Phase 2: Software Ecosystem Mapping
- ✅ Phase 3: Cross-Region Gap Detection
- ⏳ Phase 4: Validation (partial)

### Next (v0.2)
- [ ] Dynamic scraper generation for discovered platforms
- [ ] Government contract scraping and analysis
- [ ] Reddit/forum pain signal detection
- [ ] Job posting analysis
- [ ] Digitalization lag calculation

### Future (v1.0)
- [ ] Real-time platform scraping
- [ ] API integrations (Crunchbase, BuiltWith, etc.)
- [ ] Machine learning for opportunity scoring
- [ ] Web dashboard for exploring opportunities
- [ ] Alert system for new opportunities

## Contributing

This is an experimental project. Contributions welcome!

Areas for contribution:
- Additional scrapers for regional platforms
- Validation logic improvements
- More data sources
- Better scoring algorithms

## Notes

### Web Search Integration
Many agents use placeholders marked with `TODO` that would integrate with Claude's web search capabilities or external APIs. In production:
- Platform Discovery would execute actual web searches
- Company Mapper would fetch from Crunchbase API
- Software Mapper would scrape G2/Capterra/local platforms
- Validation agents would scrape contracts and forums

### Test Mode
The system includes comprehensive test mode with:
- Limited regions (Romania, Japan)
- Limited companies per region (50)
- Limited products per category (20)
- Faster iteration for development

### Database
Uses SQLite for simplicity. For production:
- Consider PostgreSQL for better concurrency
- Add caching layer (Redis)
- Implement backup strategy

## License

MIT License - See LICENSE file

## Contact

For questions, issues, or opportunities discovered using this system, please open an issue on GitHub.

---

**Built to find the next big software opportunity in emerging markets.**
