# Adversarial ML on Network Intrusion Detection — Claude Code Context

> **Template version:** v2.1 | **Source:** ml-governance-templates
> **Customization:** Fill in all `{{PLACEHOLDER}}` values, then delete this block.

## Project Purpose

{{ONE_SENTENCE_PROJECT_DESCRIPTION}}

- **Course / Context:** {{COURSE_OR_CONTEXT}}
- **Profile:** {{PROFILE}} (from ml-governance-templates)
- **Python:** 3.11 | **Env:** {{CONDA_ENV}}

## Authority Hierarchy

When requirements conflict, higher tiers win. Always.

| Tier | Source | Path |
|------|--------|------|
| 1 (highest) | {{TIER1_DESCRIPTION}} | `{{TIER1_PATH}}` |
| 2 | {{TIER2_DESCRIPTION}} | `{{TIER2_PATH}}` |
| 3 | {{TIER3_DESCRIPTION}} | `{{TIER3_PATH}}` |
| Contracts | Governance docs | `docs/*.md` |

## Current Phase

**Phase:** {{CURRENT_PHASE_NUMBER}} — {{CURRENT_PHASE_NAME}}

### Phase Commands

```bash
# Verify current phase gate
bash scripts/check_phase_{{CURRENT_PHASE_NUMBER}}.sh

# Run all gates up to current phase
bash scripts/check_all_gates.sh

# Run experiment sweep
bash scripts/sweep.sh --parts all

# Verify artifact integrity
python scripts/verify_manifests.py
```

### Phase Progression

| Phase | Name | Gate Script | Status |
|-------|------|-------------|--------|
{{PHASE_TABLE_ROWS}}

> Update the Status column as you progress. Do not advance to Phase N+1 until Phase N gate passes.

## Key Files

| File | Purpose |
|------|---------|
| `project.yaml` | Structured config driving generators and scripts |
| `docs/ENVIRONMENT_CONTRACT.md` | Environment lock (Python, deps, platform) |
| `docs/DATA_CONTRACT.md` | Data paths, splits, leakage prevention |
| `docs/EXPERIMENT_CONTRACT.md` | Experiment matrix, budgets, seeding |
| `docs/METRICS_CONTRACT.md` | Metric definitions, thresholds, sanity checks |
| `scripts/sweep.sh` | Master experiment orchestrator |
| `scripts/verify_manifests.py` | Artifact integrity checker |
| `scripts/check_phase_*.sh` | Phase gate scripts |

## AI Division of Labor

### Permitted

- Code generation, refactoring, debugging
- Test generation and execution
- Script execution (sweep, gates, verification)
- Governance audit (cross-reference docs against code)
- Configuration file generation

### Prohibited

- Report prose authorship (human writes all narrative)
- Hypothesis formulation (human intellectual contribution)
- Figure interpretation or results discussion
- Modifying Tier 1/2 requirement documents
- Accessing test split before Phase {{FINAL_EVAL_PHASE}}

### Anti-Ghostwriting Rule

AI may generate code that produces figures/tables, but the **interpretation, analysis, and written discussion** of results must be human-authored. This is a hard constraint for academic integrity.

## Conventions

- **Seeds:** Use only seeds defined in `project.yaml` — never invent new ones
- **Outputs:** All experiment outputs go to `outputs/` with structure matching `project.yaml` output_dir patterns
- **Config:** Never override locked keys defined in `project.yaml` config section
- **Changes:** Follow CONTRACT_CHANGE protocol: Decision Log → Change → Changelog → `CONTRACT_CHANGE:` commit
- **Tests:** Run `pytest` before committing. Leakage and determinism tests must always pass.
- **Artifacts:** Run `python scripts/verify_manifests.py` after any experiment run

## Workflow

1. Before starting work: check current phase with `bash scripts/check_phase_{{CURRENT_PHASE_NUMBER}}.sh`
2. Do work within the current phase scope
3. Run relevant tests: `python -m pytest tests/ -v`
4. Verify gate: `bash scripts/check_phase_{{CURRENT_PHASE_NUMBER}}.sh`
5. If gate passes, update phase status above and advance
6. Commit with descriptive message (use `CONTRACT_CHANGE:` prefix if modifying contracts)
