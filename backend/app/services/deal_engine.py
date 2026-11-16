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
    profit: float,
    monthly_rent: float,
    list_price: float,
    appreciation: float | None,
) -> str:
    """
    flip      - strong resale margin: ROI >= 15% and at least $25k profit
    rent      - gross rental yield >= 8% a year
    hold      - market appreciating >= 4%/yr with a positive deal
    wholesale - weak margin and weak yield: assign the contract instead of buying
    """
    rent_yield = (monthly_rent * 12 / list_price) * 100 if list_price else 0
    appr = appreciation if appreciation is not None else 0

    if roi >= 15 and profit >= 25000:
        return "flip"
    if rent_yield >= 8:
        return "rent"
    if appr >= 4 and roi >= 5:
        return "hold"
    if roi < 8 and rent_yield < 6:
        return "wholesale"
    if rent_yield >= 6:
        return "rent"
    return "flip" if roi >= 8 else "wholesale"


# Neutral values used in the rank score when neighborhood data is missing
NEUTRAL_APPRECIATION = 3.0
NEUTRAL_SCHOOL = 5.0
NEUTRAL_CRIME = 30.0


def compute_rank_score(
    roi: float,
    profit: float,
    appreciation: float | None,
    crime_index: float | None,
    school_rating: float | None,
    damage_severity_max: float,
) -> float:
    """Weighted 0-100 score: ROI 35%, profit 25%, market 20%, risk 20%."""
    appreciation = NEUTRAL_APPRECIATION if appreciation is None else appreciation
    school_rating = NEUTRAL_SCHOOL if school_rating is None else school_rating
    crime_index = NEUTRAL_CRIME if crime_index is None else crime_index

    roi_score = min(max(roi, 0) / 30 * 100, 100)  # 30% ROI = max
    margin_score = min(max(profit, 0) / 80000 * 100, 100)
    market_score = min(max(appreciation, 0) / 6 * 100, 100) * 0.6 + (school_rating / 10 * 100) * 0.4
    risk_score = max(0, 100 - damage_severity_max * 60 - crime_index)

    score = roi_score * 0.35 + margin_score * 0.25 + market_score * 0.20 + risk_score * 0.20
    return round(min(max(score, 0), 100), 0)
