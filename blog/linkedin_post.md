# LinkedIn Post — Vulnerability Prioritization

> Paste as native LinkedIn text. Add blog link as FIRST COMMENT (not in post body — LinkedIn algorithm deprioritizes external links).

---

I spent 15 years at Mandiant watching CISOs prioritize vulnerabilities using CVSS scores. It never worked well.

So I built an ML model to find out why.

Trained on 338,000 CVEs from NVD, with ground truth from 25,000 known exploits (ExploitDB):

→ CVSS predicts exploitability with AUC 0.66. Barely better than a coin flip.
→ ML model: AUC 0.90. A 24-percentage-point improvement.
→ EPSS (already ML-based): AUC 0.91. Nearly identical to our model.

What SHAP explainability reveals about what actually predicts exploitation:

• #1 predictor: how many CVEs a vendor has (not severity)
• #2: how old the vulnerability is (attackers need time)
• Practitioner keywords (SQL injection, RCE) rank #8-#12
• CVSS score? Only #5.

The model is also naturally robust to adversarial manipulation — 0% evasion across 3 attack types — because its top features are things attackers can't control.

Built with govML (open-source ML governance framework) and published with full reproducibility.

#AISecurity #MachineLearning #Cybersecurity #VulnerabilityManagement

---

> First comment: "Full write-up with code, architecture diagram, and SHAP visualizations: [blog URL]"
> Second comment: "Code: github.com/rexcoleman/vuln-prioritization-ml-"
