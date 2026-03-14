# Substack Email Intro

> Paste this BEFORE the full blog post content in Substack editor. This is the email-specific hook that appears in inbox previews.

---

If you've ever triaged vulnerabilities using CVSS scores, you know the feeling: a "Critical 9.8" sits unpatched for months because your team knows it's not actually exploitable in your environment, while a "High 7.5" gets weaponized next week.

CVSS scores severity, not exploitability. They're a static formula from 2005.

I trained an ML model on 338,000 real CVEs to find out what actually predicts exploitation. The results surprised me — and they'll change how you think about vulnerability prioritization.

Read on for the full analysis, SHAP explainability, and an adversarial robustness test that validates why this model is hard to game.
