# PROJECT BRIEF — ML-Powered Vulnerability Prioritization Engine

<!-- version: 1.0 -->
<!-- created: 2026-03-14 -->

> **Authority Hierarchy**
>
> | Priority | Document | Role |
> |----------|----------|------|
> | Tier 1 | `docs/PROJECT_BRIEF.md` | Primary spec — highest authority |
> | Tier 2 | — | No external FAQ (self-directed research) |
> | Tier 3 | `docs/ADVERSARIAL_EVALUATION.md` | Advisory — adversarial robustness methodology |
> | Contract | This document | Implementation detail — subordinate to all tiers above |
>
> **Conflict rule:** When a higher-tier document and this contract disagree, the higher tier wins.

### Companion Contracts

**Upstream (this contract depends on):**
- None — this is the foundational project definition document.

**Downstream (depends on this contract):**
- See [HYPOTHESIS_CONTRACT](HYPOTHESIS_CONTRACT.md) for research questions → testable hypotheses
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.md) for experiment design derived from thesis
- See [DATA_CONTRACT](DATA_CONTRACT.md) for dataset definition
- See [PUBLICATION_PIPELINE](PUBLICATION_PIPELINE.md) for blog post governance
- See [IMPLEMENTATION_PLAYBOOK](IMPLEMENTATION_PLAYBOOK.md) for phase execution
- See [DECISION_LOG](DECISION_LOG.md) for architectural decisions

---

## 1) Thesis Statement

**An ML model trained on public vulnerability data (NVD + ExploitDB + EPSS) can outperform CVSS-based triage at predicting real-world exploitability, and the model's decision factors reveal what makes vulnerabilities actually dangerous — knowledge that CVSS's static formula misses.**

This is the "practitioner vs formula" bet: 15 years of watching which vulnerabilities actually get exploited gives you ground truth intuition that a static scoring formula can't capture. The ML model encodes that intuition into features.

---

## 2) Research Questions

| # | Question | How You'll Answer It | Success Criteria |
|---|----------|---------------------|-----------------|
| RQ1 | Can ML features (description NLP, temporal patterns, vendor metadata, exploit availability) predict exploitability better than CVSS base score? | Train classifier on NVD+ExploitDB labels; compare AUC/F1 against CVSS-threshold baseline | ML model AUC > CVSS-threshold AUC by ≥5pp |
| RQ2 | Which features matter most for real-world exploitability prediction? | SHAP/permutation importance on trained model | Top-5 features identified with interpretable rationale |
| RQ3 | How does the model compare to EPSS (Exploit Prediction Scoring System)? | Benchmark on same test set; analyze disagreements | Characterize where model agrees/disagrees with EPSS and why |
| RQ4 | Can adversarial perturbation of CVE descriptions evade the model? | Apply text perturbation attacks (synonym swap, field injection) | Measure evasion rate; propose defenses (from FP-01 controllability lens) |

---

## 3) Scope Definition

### In Scope
- NVD CVE data ingestion and feature engineering (description NLP, CWE type, vendor, temporal features)
- ExploitDB cross-reference for ground truth labels (exploited vs not-exploited)
- EPSS score ingestion as baseline/comparison
- Multi-model comparison: Random Forest, XGBoost, logistic regression, simple NN
- Explainability layer (SHAP values)
- Adversarial evaluation (text perturbation attacks on CVE descriptions)
- Feature controllability analysis (which CVE fields can an attacker manipulate?)
- FINDINGS.md with key results
- Architecture diagram

### Out of Scope
- Real-time CVE monitoring dashboard (P3+ scope — future project)
- Integration with vulnerability scanners (Nessus, Qualys)
- Proprietary threat intelligence data
- Deep learning on full CVE text (BERT/LLM fine-tuning — stretch goal only)

### Stretch Goals (only if core scope complete)
- BERT/transformer embedding of CVE descriptions (compare against TF-IDF)
- Temporal analysis: does model accuracy change across CVE years?
- huntr submission if model reveals systematically mislabeled CVEs

---

## 4) Data / Workload Definition

| Property | Value |
|----------|-------|
| **Primary dataset** | NVD (National Vulnerability Database) — NIST |
| **Source** | https://nvd.nist.gov/vuln/data-feeds (JSON feeds) + NVD API 2.0 |
| **Download method** | API (NVD REST API, rate-limited to 50 req/30s with API key) |
| **Size** | ~230,000+ CVEs (2002–present), ~250MB JSON |
| **License** | Public domain (US Government work) |
| **Known issues** | API rate limits; older CVEs have sparse descriptions; CVSS v2 vs v3 transition; some CVEs lack CWE classification |

| Property | Value |
|----------|-------|
| **Ground truth labels** | ExploitDB (Offensive Security) |
| **Source** | https://gitlab.com/exploit-database/exploitdb (Git repo, CSV index) |
| **Download method** | `git clone` (direct, ~1GB including exploit code) or CSV-only via API |
| **Size** | ~45,000 exploits mapped to CVEs |
| **License** | Public (GPLv2 for the database) |

| Property | Value |
|----------|-------|
| **Baseline comparison** | EPSS (First.org Exploit Prediction Scoring System) |
| **Source** | https://api.first.org/data/v1/epss |
| **Download method** | API (REST, no auth required) + daily CSV dumps |
| **Size** | Scores for all active CVEs (~200K entries, updated daily) |

| Property | Value |
|----------|-------|
| **Supplementary** | GitHub Advisory Database |
| **Source** | https://github.com/advisories (API via `gh api`) |
| **Download method** | GitHub API |
| **Size** | ~15,000 reviewed advisories |

---

## 5) Skill Cluster Targets

| Cluster | Current Level | Target After Project | How This Project Advances It |
|---------|-------------|---------------------|---------------------------|
| **L** (AI System) | L3+ | L3→L4 | NLP feature pipeline + structured prediction + SHAP explainability = AI-native product |
| **S** (AI Security) | S1-S2 | S2→S3 | Novel findings on what makes vulns exploitable; adversarial evaluation of CVE-based ML; practitioner-grounded feature engineering |
| **P** (Product Eng.) | P2++ | P2→P3-adj | Full pipeline with data API ingestion, multi-source joins, reproducible experiments |
| **D** (Tech Depth) | D3 solid | D3→D4 | Documented tradeoffs: feature engineering decisions, model selection rationale, CVSS vs ML comparison methodology |
| **V** (Distribution) | V1 | V1→V2 (inventory) | Blog post drafted; published when brand infra ready. Content pillar: AI Security Architecture. |

---

## 6) Publication Target

| Property | Value |
|----------|-------|
| **Blog post title (working)** | "Why CVSS Gets It Wrong: ML-Powered Vulnerability Prioritization with Explainable Features" |
| **Content pillar** | AI Security Architecture (40% pillar) |
| **Conference CFP** | BSides / DEF CON AI Village (after blog establishes credibility) |
| **Target publish date** | Deferred — build artifact now, publish when Hugo + Substack are live |

---

## 7) Technical Approach

### Architecture Overview

```
NVD API ──→ CVE ingestion ──→ Feature engineering ──→ Model training ──→ Evaluation
                │                     │                                      │
ExploitDB ──→ Label join         NLP features                    SHAP explainability
                │                 (TF-IDF/embeddings)                       │
EPSS API ──→ Baseline                                          Comparison vs CVSS/EPSS
                │                                                           │
GitHub Adv ──→ Supplementary                                 Adversarial evaluation
              labels                                          (text perturbation)
                                                                           │
                                                                    FINDINGS.md
```

### Key Technical Decisions (pre-project)

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| NLP features | TF-IDF, Word2Vec, BERT embeddings | TF-IDF (primary), BERT (stretch) | TF-IDF is interpretable + fast. BERT is stretch goal. Start simple. |
| Label definition | Binary (exploited/not) vs ordinal (exploit maturity) | Binary — has ExploitDB match or not | Cleaner ground truth. Exploit maturity requires subjective judgment. |
| Train/test split strategy | Random, temporal, CVE-year stratified | Temporal (train on pre-2024, test on 2024+) | Prevents data leakage from future information. Mirrors real-world deployment. |
| Smoke testing | Full data vs sample | 1% sample first (from FP-01 WIN-011) | Catches bugs 10x faster |

---

## 8) Definition of Done

- [ ] All 4 research questions answered with evidence
- [ ] All code in version-controlled repo (GitHub: rexcoleman/vuln-prioritization-ml)
- [ ] FINDINGS.md written with key results
- [ ] Architecture diagram created (Mermaid or Excalidraw)
- [ ] DECISION_LOG has all tradeoff decisions from every phase
- [ ] PUBLICATION_PIPELINE.md filled and blog draft started
- [ ] LESSONS_LEARNED.md in govML updated with FP-05 issues and wins
- [ ] govML templates improved based on FP-05 friction
- [ ] Comparison table: ML model vs CVSS vs EPSS (the money chart)
- [ ] SHAP feature importance visualization (the explainability artifact)
- [ ] Adversarial evaluation: text perturbation evasion rates documented
