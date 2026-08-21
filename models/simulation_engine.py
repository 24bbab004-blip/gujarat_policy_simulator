from dataclasses import dataclass, asdict
import numpy as np

@dataclass
class PolicyInput:
    name: str
    category: str
    districts: list[str]
    current_benefit: float
    proposed_benefit: float
    current_beneficiaries: int
    proposed_beneficiaries: int
    current_threshold: float
    proposed_threshold: float
    duration_years: float

    def to_dict(self):
        return asdict(self)

CATEGORY_CONFIG = {
    "Education": ("Scholarship / student support (₹)", "Eligible students", "Participation & retention"),
    "Healthcare": ("Annual health support (₹)", "Covered people", "Service utilisation & access"),
    "Transport": ("Annual subsidy per rider (₹)", "Regular riders", "Affordable mobility"),
    "Housing": ("Housing assistance (₹)", "Eligible households", "Housing security"),
    "Water": ("Annual water subsidy (₹)", "Covered households", "Reliable water access"),
    "Employment & Skill Development": ("Training support (₹)", "Trainees", "Training completion & employability"),
    "Agriculture": ("Farmer / input support (₹)", "Eligible farmers", "Farm resilience & input access"),
}

def calculate(inp: PolicyInput, district_data, draws=1000, seed=17):
    """Deterministic core calculation plus transparent scenario-range simulation."""
    current_cost = inp.current_benefit * inp.current_beneficiaries * inp.duration_years
    proposed_cost = inp.proposed_benefit * inp.proposed_beneficiaries * inp.duration_years
    additional_cost = proposed_cost - current_cost
    cost_change = (additional_cost / current_cost * 100) if current_cost else 0
    beneficiary_change = inp.proposed_beneficiaries - inp.current_beneficiaries
    beneficiary_change_pct = (beneficiary_change / inp.current_beneficiaries * 100) if inp.current_beneficiaries else 0
    benefit_change_pct = ((inp.proposed_benefit / inp.current_benefit - 1) * 100) if inp.current_benefit else 100
    threshold_change_pct = ((inp.proposed_threshold / inp.current_threshold - 1) * 100) if inp.current_threshold else 0

    # Proxy impact: reach and benefit changes have diminishing returns; district readiness moderates delivery.
    readiness = float(district_data["capacity_index"].mean()) if len(district_data) else 0.6
    reach = min(100, 50 + 0.35 * beneficiary_change_pct)
    affordability = min(100, 50 + 0.30 * benefit_change_pct + 0.10 * threshold_change_pct)
    access = min(100, 30 + 0.45 * reach + 20 * readiness)
    impact = round(np.clip(0.35 * reach + 0.35 * affordability + 0.30 * access, 0, 100), 1)

    rng = np.random.default_rng(seed)
    # Assumption range: +/- 8% uptake and +/- 5% unit cost (explicitly not a confidence interval).
    modeled_costs = (inp.proposed_benefit * rng.normal(1, .05, draws) *
                     inp.proposed_beneficiaries * rng.normal(1, .08, draws) * inp.duration_years)
    low, high = np.percentile(modeled_costs, [10, 90])
    district_rows = []
    total_pop = max(float(district_data.population.sum()), 1)
    for _, d in district_data.iterrows():
        share = d.population / total_pop
        capacity = float(d.capacity_index)
        district_rows.append({
            "district": d.district, "beneficiaries": round(inp.proposed_beneficiaries * share),
            "cost": proposed_cost * share, "impact": round(np.clip(impact * (0.8 + .2 * capacity), 0, 100), 1),
            "risk": round(np.clip(100 - (capacity * 55 + (100-impact)*.35), 0, 100), 1),
            "efficiency": round(np.clip((impact * (0.8 + .2*capacity)) - max(0, cost_change)*.08, 0, 100), 1),
        })
    return {
        "financial": {"current_cost": current_cost, "proposed_cost": proposed_cost, "additional_cost": additional_cost,
                      "cost_change_pct": cost_change, "cost_per_beneficiary": proposed_cost / max(inp.proposed_beneficiaries, 1),
                      "range_low": float(low), "range_high": float(high)},
        "beneficiaries": {"current": inp.current_beneficiaries, "proposed": inp.proposed_beneficiaries,
                            "additional": beneficiary_change, "change_pct": beneficiary_change_pct},
        "impact": {"score": impact, "reach": round(reach,1), "affordability": round(affordability,1), "access": round(access,1),
                   "readiness": readiness},
        "changes": {"benefit_pct": benefit_change_pct, "threshold_pct": threshold_change_pct},
        "districts": district_rows,
        "assumptions": ["Unit benefit is delivered to each proposed beneficiary for the selected duration.",
                        "Impact is an explainable proxy score, moderated by synthetic district capacity data.",
                        "Range varies unit cost by ±5% and take-up by ±8% across 1,000 deterministic-seeded runs."],
    }
