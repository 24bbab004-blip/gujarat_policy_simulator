def score(financial, beneficiaries, impact, risk):
    change = max(financial["cost_change_pct"], 0)
    financial_efficiency = max(0, min(100, 92 - change * .45))
    reach = max(0, min(100, 50 + beneficiaries["change_pct"] * .7))
    expected = impact["score"]
    risk_component = 100 - risk["score"]
    total = round(.30*financial_efficiency + .25*reach + .25*expected + .20*risk_component, 1)
    return {"total": total, "financial": round(financial_efficiency,1), "reach": round(reach,1),
            "impact": round(expected,1), "risk": round(risk_component,1)}
