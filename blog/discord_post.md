# For: general security Discord / r/netsec

trained 7 ML models on 338k CVEs to predict real-world exploitation. logistic regression hit 0.903 AUC — beating CVSS by 24 percentage points. but the honest finding is it's mostly just learning to copy EPSS.

```
model               AUC-ROC    vs CVSS
CVSS (best thresh)  0.662      baseline
XGBoost             0.825      +16pp
random forest       0.864      +20pp
logistic regression 0.903      +24pp
EPSS (reference)    0.912      +25pp

without EPSS features: all models collapse to ~0.68
dual ground truth (ExploitDB + KEV): XGB hits 0.928
```

simpler models win because the signal is in vendor metadata and CVE age, not complex feature interactions. logistic regression beats XGBoost and random forest — the opposite of what you'd expect. the features that matter are boring: vendor name, time since publication, EPSS score.

the ground truth lag problem is real. 2024+ test set has 0.3% exploit rate vs 10.5% in training — not because recent CVEs are safer but because ExploitDB hasn't caught up yet. temporal splits are the only honest evaluation; random splits will massively overfit.

the dual ground truth finding is actually useful: combining ExploitDB + KEV as positive labels pushes XGBoost to 0.928, which edges past EPSS. if you have access to both data sources, the ensemble labels are better than either alone.

anyone training exploit prediction models? what ground truth sources are you using beyond ExploitDB?
