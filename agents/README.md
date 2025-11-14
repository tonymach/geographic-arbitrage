# PE-Grade Analysis Agents

This directory contains the agent framework for complete arbitrage opportunity analysis with PE-grade metrics.

## Flow

```
Phase 0: Platform Discovery (ClaudeOrchestrator)
    ↓
Phase 1: Ecosystem Mapping (agent_runner.py)
    ↓
Phase 2: Gap Detection (agent_runner.py)
    ↓
Phase 3: Validation & Unit Economics (agent_runner.py)
```

## Files

- `agent_runner.py` - Main agent orchestration logic
- `prompts/` - Prompt templates for each phase
  - `phase1_ecosystem_mapping.txt` - Find products in each market
  - `phase2_gap_detection.txt` - Identify arbitrage gaps
  - `phase3_validation.txt` - Validate with unit economics

## Usage

```python
from claude_orchestrator import ClaudeOrchestrator
from agents.agent_runner import AgentRunner

# Initialize
orch = ClaudeOrchestrator()
runner = AgentRunner(orch)

# Run phases
ecosystem_map = await runner.run_phase1_ecosystem_mapping(['Poland'], ['Construction'])
opportunities = await runner.run_phase2_gap_detection(ecosystem_map)
validated = await runner.run_phase3_validation(opportunities)
```

Or use the complete flow script:

```bash
python run_complete_flow.py
```

## Database Schema

All data is saved to Turso:

1. **software_products** - Products discovered in Phase 1
2. **arbitrage_opportunities** - Gaps detected in Phase 2, extended with Phase 3 data
3. **pain_signals** - Demand validation from Phase 3

## Output Metrics

Each validated opportunity includes:

- **Unit Economics:** ACV, CAC, LTV, LTV:CAC ratio, payback period
- **Financial Model:** 3-year revenue/EBITDA projections
- **Market Size:** TAM calculation
- **Exit Strategy:** Base/bull case valuations, ROI multiple
- **Risk Analysis:** Top risks with probability/impact/mitigation
- **Moat Analysis:** Defensibility scores

## Next Steps

1. Run schema update: `python update_schema.py`
2. Run complete flow: `python run_complete_flow.py`
3. View results: Open `explorer_turso.html`

## TODO

Replace mock functions in `agent_runner.py` with actual Claude Task agents:
- `_mock_ecosystem_research` → Spawn real WebSearch agent
- `_mock_gap_detection` → Spawn real analysis agent
- `_mock_validation` → Spawn real validation agent
