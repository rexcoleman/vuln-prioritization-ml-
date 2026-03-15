# ML-Powered Vulnerability Prioritization: Why CVSS Isn't Enough

I trained ML models on 338K CVEs to predict which vulnerabilities have real exploits. Logistic Regression achieved 0.903 AUC-ROC — beating CVSS by 24 percentage points. But the most important finding wasn't the model performance. It was what SHAP told us about which features actually predict exploitability, and why temporal splits reveal a ground truth problem nobody talks about.

## What I Built

An ML pipeline that ingests CVEs from three public sources (NVD, ExploitDB, EPSS), engineers 49 features, and predicts real-world exploitability. The target variable: does this CVE have a known exploit in ExploitDB?

Three data sources, three baselines, three ML models, SHAP explainability, and adversarial evaluation with feature controllability analysis.

Built with [govML](https://github.com/rexcoleman/govML) v2.4. 11 architecture decision records documenting every tradeoff.

## Why CVSS Fails at Prioritization

CVSS scores what a vulnerability CAN do (impact + exploitability vectors). But security teams need to know what WILL be exploited. A CVSS 9.8 in an obscure library nobody uses is lower priority than a CVSS 7.0 in Apache with a Metasploit module.

Best CVSS threshold (≥9.0) achieves only 0.662 AUC-ROC. Random would be 0.5. CVSS is barely better than a coin flip at predicting actual exploitation.

## Key Findings

### 1. ML Crushes CVSS (+24pp AUC)

| Model | AUC-ROC | vs CVSS Baseline |
|---|---|---|
| Best CVSS Threshold (≥9.0) | 0.662 | baseline |
| XGBoost | 0.825 | +16.3pp |
| Random Forest | 0.864 | +20.2pp |
| **Logistic Regression** | **0.903** | **+24.1pp** |
| EPSS (for reference) | 0.912 | +25.1pp |

Logistic Regression wins — simpler models outperform on this task because the signal is in vendor metadata and CVE age, not complex feature interactions.

EPSS (0.912) slightly beats our model (0.903), but EPSS is a black box trained on proprietary data. Our model is open, explainable, and built on public data only.

### 2. Vendor History Is the #1 Predictor

SHAP analysis reveals that `vendor_cve_count` (how many CVEs a vendor has historically) is the dominant predictor — by a factor of 35x over the next feature. Vendors with high CVE counts (Microsoft, Linux kernel, Chrome) have more exploited vulnerabilities because attackers target what's widely deployed.

The practitioner-relevant features are:
- `kw_sql_injection` — strongest keyword signal
- `kw_remote_code_execution` — second strongest
- `has_exploit_ref` — CVE references mentioning "exploit" or "PoC"

These are the features a security practitioner would use intuitively. The model validates practitioner judgment.

### 3. The Ground Truth Lag Problem

We used a temporal split: train on pre-2024 CVEs (10.5% exploited), test on 2024+ CVEs (0.3% exploited). The massive drop isn't because 2024 CVEs are less exploitable — it's because ExploitDB hasn't caught up yet. Exploits exist but haven't been catalogued.

This is a finding, not a flaw. Any production vuln prioritization system faces this: **your ground truth is always lagging**. Models trained on historical data look great on historical test sets and terrible on recent data — not because they're wrong, but because the labels are incomplete.

### 4. Feature Controllability Analysis (2nd Domain)

Applying the controllability methodology from FP-01:

| Feature Type | Count | Controllability |
|---|---|---|
| Text/description features | 13 | Attacker-influenced (can craft descriptions) |
| Vendor/temporal metadata | 11 | Environment-determined (not controllable) |
| CVSS/EPSS scores | 5 | Third-party-controlled |
| Reference features | 8 | Partially attacker-influenced |

The adversarial risk: an attacker who knows the model could craft CVE descriptions to manipulate priority scoring. Mitigation: weight non-textual features (vendor history, EPSS) higher than text features.

## What I Learned

**Simplicity wins.** Logistic Regression beat XGBoost and Random Forest. The signal is linear — vendor size and CVE age predict exploitation without complex interactions.

**Temporal splits expose reality.** Random splits give flattering numbers (AUC 0.95+). Temporal splits give honest numbers (AUC 0.90). Always use temporal splits for time-dependent data.

**EPSS is hard to beat.** Our model (0.903) came close to EPSS (0.912) but didn't beat it. The value of our approach isn't raw performance — it's explainability (SHAP) and openness (public data, open code).

The pipeline is open source. Built with [govML](https://github.com/rexcoleman/govML) v2.4 governance.

---

*Rex Coleman is an MS Computer Science student (Machine Learning) at Georgia Tech, building at the intersection of AI security and ML systems engineering. Previously 15 years in cybersecurity (FireEye/Mandiant — analytics, enterprise sales, cross-functional leadership). CFA charterholder. Creator of [govML](https://github.com/rexcoleman/govML).*
