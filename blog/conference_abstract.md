# Conference Abstract — BSides / DEF CON AI Village

> **Title:** Why CVSS Gets It Wrong: ML-Powered Vulnerability Prioritization with Explainable Features and Adversarial Robustness
> **Speaker:** Rex Coleman
> **Track:** AI Security / ML for Cybersecurity
> **Length:** 20-30 minutes

## Abstract

CVSS is the industry standard for vulnerability scoring, but it was designed to measure severity — not exploitability. We demonstrate that CVSS predicts real-world exploitation with an AUC of only 0.66 (barely better than random), while a simple ML model trained on public data achieves 0.90.

We train Random Forest, XGBoost, and Logistic Regression classifiers on 338,000 CVEs from the National Vulnerability Database, using 25,000 known exploits from ExploitDB as ground truth labels. Using temporal train/test splits to prevent data leakage, we compare ML predictions against CVSS thresholds and EPSS (the Exploit Prediction Scoring System).

Key findings:
1. **ML crushes CVSS** (+24 AUC points) using only public data
2. **SHAP explainability** reveals the top predictors of exploitation: vendor CVE history, vulnerability age, and practitioner-identifiable keywords (SQL injection, RCE) — none of which CVSS weighs appropriately
3. **Feature controllability analysis** shows the model is naturally robust to adversarial manipulation (0% evasion) because its top features are defender-observable, not attacker-controllable
4. **Cross-project validation**: the feature controllability methodology was independently validated on a network intrusion detection system, proving it transfers across security domains

We release the full pipeline as open source with govML governance (reproducible experiments, documented decisions, SHAP visualizations).

## Bio (100 words)

Rex Coleman is a security architect building at the intersection of AI and cybersecurity. He spent 15 years in cybersecurity at FireEye and Mandiant, advising enterprise security teams defending against nation-state adversaries. He is now completing his MS in Computer Science at Georgia Tech (Machine Learning specialization), where he builds governed ML pipelines and researches AI security — adversarial evaluation of ML systems, agent exploitation, and ML governance tooling. He is the creator of govML, an open-source governance framework for ML projects. He holds the CISSP and CFA certifications.

## Why This Talk Matters

Every SOC in the world prioritizes vulnerabilities using CVSS. This research provides concrete, reproducible evidence that CVSS is a poor exploitability predictor and demonstrates a transparent, explainable alternative. The adversarial robustness analysis (using a novel feature controllability methodology) is directly relevant to the AI security community — it answers "can an attacker game this model?" with a clear "no, and here's why."

## Outline

1. **The Problem** (3 min): CVSS scores severity ≠ exploitability. Real-world examples from 15yr of triage.
2. **The Data** (3 min): NVD + ExploitDB + EPSS. Temporal split methodology.
3. **The Results** (8 min): AUC comparison table. SHAP feature importance. Live demo of SHAP waterfall plot.
4. **Feature Controllability** (5 min): Which features can an attacker manipulate? Why the model is robust. Cross-domain validation (IDS + CVE).
5. **Implications** (3 min): What this means for vulnerability management programs. What CVSS should learn from ML.
6. **Demo / Q&A** (5 min): GitHub repo walkthrough. govML governance.
