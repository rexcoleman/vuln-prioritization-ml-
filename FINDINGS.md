# FINDINGS — ML-Powered Vulnerability Prioritization Engine

> **Status:** DRAFT — awaiting experiment results
> **Project:** FP-05 (Vulnerability Prioritization)
> **Thesis:** An ML model trained on public vulnerability data can outperform CVSS-based triage at predicting real-world exploitability.

---

## Key Results

*(Fill after experiments complete)*

### RQ1: ML vs CVSS

| Model | AUC-ROC | AUC-PR | F1 | vs Best CVSS Threshold |
|-------|---------|--------|----|-----------------------|
| Random Forest | | | | |
| XGBoost | | | | |
| Logistic Regression | | | | |
| **Best CVSS Threshold** | | | | baseline |
| **Best EPSS Threshold** | | | | |
| Random (majority) | | | | |

**RQ1 verdict:** *(ML model AUC > CVSS threshold AUC by ≥5pp?)*

### RQ2: Feature Importance (SHAP)

**Top 10 features by mean |SHAP value|:**

| Rank | Feature | Mean |SHAP| | Category | Practitioner Keyword? |
|------|---------|-------------|----------|----------------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Practitioner keyword features in top 20:** _/11

**RQ2 verdict:** *(Which features matter most? Do practitioner keywords outperform generic NLP?)*

### RQ3: ML vs EPSS

| Metric | Best ML Model | EPSS | Difference |
|--------|--------------|------|------------|
| AUC-ROC | | | |
| AUC-PR | | | |

**Disagreement analysis:** *(Where does our model predict high risk but EPSS says low, and vice versa? Are these interesting CVEs?)*

### RQ4: Adversarial Robustness

| Attack | Evasion Rate | F1 Drop | Controllable Features Affected |
|--------|-------------|---------|-------------------------------|
| Synonym swap | | | Text-derived |
| Field injection | | | Text-derived |
| Noise perturbation | | | Text-derived |

**Feature controllability insight:** *(What % of model importance comes from attacker-controllable vs defender-observable features? Is a defender-only model viable?)*

---

## Architecture

*(Insert Mermaid or Excalidraw diagram here)*

---

## Key Decisions (from DECISION_LOG)

| ADR | Decision | Impact on Results |
|-----|----------|-------------------|
| ADR-0001 | Temporal split (pre-2024 / 2024+) | |
| ADR-0005 | TF-IDF over BERT | |
| ADR-0006 | Practitioner keyword features | |

---

## Limitations

- *(Fill after experiments)*

---

## Blog Post Angle

**Title:** "Why CVSS Gets It Wrong: ML-Powered Vulnerability Prioritization with Explainable Features"

**Key insight for readers:** *(The one thing they walk away with)*

**Hook:** *(2-3 sentences for the blog post opening)*
