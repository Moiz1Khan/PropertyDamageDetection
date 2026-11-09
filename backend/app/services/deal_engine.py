"""Pure business logic — no ML. Used by the analysis pipeline."""

from __future__ import annotations


def compute_total_investment(list_price: float, rehab_cost: float, closing_pct: float = 0.03) -> float:
    closing = list_price * closing_pct
    return list_price + rehab_cost + closing


def compute_profit(arv: float, list_price: float, rehab_cost: float, selling_cost_pct: float = 0.06) -> float:
    selling = arv * selling_cost_pct
    total_in = compute_total_investment(list_price, rehab_cost)
    return round(arv - selling - total_in, 0)


def compute_roi(profit: float, list_price: float, rehab_cost: float) -> float:
    invested = compute_total_investment(list_price, rehab_cost)
    if invested <= 0:
        return 0.0
    return round((profit / invested) * 100, 1)


def compute_max_offer(
    arv: float,
    rehab_cost: float,
    target_margin_pct: float = 0.20,
    closing_pct: float = 0.03,
) -> float:
    """
    Classic investor formula:
    Max Offer = ARV * (1 - margin) - rehab - estimated closing on purchase
    """
    offer = arv * (1 - target_margin_pct) - rehab_cost
    # leave room for purchase closing costs
    offer = offer / (1 + closing_pct)
    return max(0, round(offer / 1000) * 1000)


def recommend_strategy(
    roi: float,
    monthly_rent: float,
    list_price: float,
    appreciation: float,
    rehab_cost: float,
) -> str:
    rent_yield = (monthly_rent * 12 / list_price) * 100 if list_price else 0
    rehab_ratio = rehab_cost / list_price if list_price else 0

    if roi >= 20 and rehab_ratio >= 0.08:
        return "flip"
    if rent_yield >= 7.5 and appreciation >= 3.5:
        return "rent"
    if appreciation >= 4.5 and roi >= 12:
        return "hold"
    if roi < 12 and rehab_ratio < 0.05:
        return "wholesale"
    if rent_yield >= 6:
        return "rent"
    return "flip"


def compute_rank_score(
    roi: float,
    profit: float,
    appreciation: float,
    crime_index: float,
    school_rating: float,
    damage_severity_avg: float,
) -> float:
    """Weighted 0–100 score matching the design doc weights."""
    roi_score = min(roi / 30 * 100, 100)  # 30% ROI = max
    margin_score = min(max(profit, 0) / 80000 * 100, 100)
    market_score = min(appreciation / 6 * 100, 100) * 0.6 + (school_rating / 10 * 100) * 0.4
    risk_score = max(0, 100 - damage_severity_avg * 100 - crime_index)

    score = (
        roi_score * 0.35
        + margin_score * 0.25
        + market_score * 0.20
        + risk_score * 0.20
    )
    return round(min(max(score, 0), 100), 0)
