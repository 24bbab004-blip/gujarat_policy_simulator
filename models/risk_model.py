def assess(financial, beneficiaries, impact, capacity=0.6):
    risks, positives = [], []
    if financial["cost_change_pct"] > 20: risks.append(("High budget impact", "HIGH", "Proposed expenditure increases by more than 20%."))
    elif financial["cost_change_pct"] > 5: risks.append(("Budget impact", "MEDIUM", "Additional expenditure needs budget review."))
    if beneficiaries["change_pct"] > 25: risks.append(("Administrative load", "HIGH", "Beneficiary volume increases by more than 25%."))
    elif beneficiaries["change_pct"] > 10: risks.append(("Administrative load", "MEDIUM", "More applications and verification capacity may be required."))
    if capacity < .55: risks.append(("Capacity risk", "HIGH", "Selected districts have below-average synthetic service capacity."))
    if impact["score"] >= 65: positives.append("Estimated access and affordability indicators improve.")
    if beneficiaries["additional"] > 0: positives.append("Beneficiary reach increases.")
    if not risks: risks.append(("Manageable implementation risk", "LOW", "No configured risk threshold was crossed."))
    risk_score = min(100, sum({"LOW": 12, "MEDIUM": 27, "HIGH": 45}[r[1]] for r in risks))
    return {"items": risks, "positives": positives, "score": risk_score}
