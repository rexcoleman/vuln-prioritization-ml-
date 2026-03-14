# LinkedIn Post — Vulnerability Prioritization

> Paste as native LinkedIn text. Add blog link as FIRST COMMENT (not in post body — LinkedIn algorithm deprioritizes external links).

---

After 15 years at Mandiant, I watched security teams burn hours patching CVSS 9.8s that never got exploited — while CVSS 7.5s got weaponized and led to breaches.

CVSS measures severity. Attackers measure opportunity.

I trained an ML model on 338,000 real CVEs to find out what actually predicts exploitation. Here's what the data says:

CVSS predicts exploitability with AUC 0.66. Barely better than a coin flip.
ML model: AUC 0.90. A 24-point improvement.

But the real insight is WHY. SHAP explainability reveals:

1. The #1 predictor is how many CVEs a vendor has — not severity. Attackers invest where deployment is highest. They maintain toolkits for high-value targets and add new CVEs to existing exploit chains.

2. #2 is vulnerability age. Weaponization isn't instant — it follows a lifecycle from disclosure to PoC to exploit kit to active exploitation. A 2-year-old CVE is more dangerous than a 2-day-old one.

3. Practitioner keywords (SQL injection, RCE) rank #8-#12. They matter — but less than where the vuln is and how long it's been available.

4. CVSS score? Only #5. The formula everyone uses for prioritization is the fifth most important feature.

The model is also naturally robust to adversarial manipulation — 0% evasion across 3 attack types. Why? Because its top features are things attackers can't control (vendor history, publication date, EPSS score). You can rewrite a CVE description to hide an RCE, but you can't change the vendor's CVE count.

This is the same "feature controllability" principle I validated on network intrusion detection. Build ML security systems on features the adversary cannot manipulate.

Full code, data pipeline, and SHAP visualizations are open source.

#AISecurity #MachineLearning #Cybersecurity #VulnerabilityManagement #BuildInPublic

---

> First comment: "Full write-up with architecture diagram and SHAP plots: [blog URL]"
> Second comment: "Code + governed pipeline: github.com/rexcoleman/vuln-prioritization-ml-"
> Third comment: "Built with govML — open-source ML governance framework: github.com/rexcoleman/govML"
