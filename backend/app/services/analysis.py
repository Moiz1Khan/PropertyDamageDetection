"""
Property analysis pipeline.

Every number is either measured (photos, RentCast) or a clearly labelled estimate.
Nothing is random. Each figure records its source in `valuation` so the UI and report can show it.
"""

from __future__ import annotations

import hashlib
import random
import statistics
from typing import Any

from sqlalchemy.orm import Session

from . import damage_inference, deal_engine, gemini_vision, rehab, rentcast
from .damage_pipeline import analyze_photos

# Regional estimate tables (Texas metros only). Used only when live data is missing, and labelled as such.
CITY_MARKET = {
    "austin": {"psf": 215, "rent_psf": 1.35, "school": 8.0, "crime": 22, "appr": 4.8},
    "dallas": {"psf": 175, "rent_psf": 1.20, "school": 6.8, "crime": 32, "appr": 3.4},
    "houston": {"psf": 190, "rent_psf": 1.25, "school": 7.1, "crime": 28, "appr": 3.9},
    "san antonio": {"psf": 165, "rent_psf": 1.15, "school": 6.5, "crime": 30, "appr": 3.2},
}

# Placeholder cover photos for properties without uploads (display only, never analysed)
DEFAULT_IMAGES = [
    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&q=80",
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80",
    "https://images.unsplash.com/photo-1605276374101-dee2ffb0f962?w=800&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80",
    "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80",
]

# A market value outside this ratio of the list price is treated as a bad lookup
VALUE_RATIO_MIN, VALUE_RATIO_MAX = 0.5, 2.0
# Monthly rent as a share of price; outside this band the estimate is treated as a bad lookup
RENT_RATIO_MIN, RENT_RATIO_MAX = 0.003, 0.025
RULE_OF_THUMB_RENT = 0.007


def pick_image(address: str) -> str:
    seed = int(hashlib.sha256(f"img:{address}".encode()).hexdigest()[:16], 16)
    return random.Random(seed).choice(DEFAULT_IMAGES)


def _market_table(city: str) -> dict | None:
    return CITY_MARKET.get((city or "").strip().lower())


def _value_ok(value: float | None, list_price: float) -> bool:
    return bool(value) and list_price > 0 and VALUE_RATIO_MIN <= value / list_price <= VALUE_RATIO_MAX


def _money(v: float) -> str:
    return f"${v:,.0f}"


def _as_is_value(
    list_price: float, sqft: int, city: str, avm: float | None, comps: list[dict], warnings: list[str]
) -> tuple[float, str]:
    candidates: list[tuple[str, float | None]] = [("RentCast valuation (AVM)", avm)]
    if comps:
        psf = statistics.median(c["salePrice"] / c["sqft"] for c in comps if c.get("sqft"))
        candidates.append((f"{len(comps)} comparable sales (median ${psf:,.0f}/sqft)", psf * sqft))
    table = _market_table(city)
    if table:
        candidates.append((f"regional estimate table (${table['psf']}/sqft, {city.title()})", table["psf"] * sqft))

    for source, value in candidates:
        if value is None:
            continue
        if _value_ok(value, list_price):
            return float(value), source
        warnings.append(
            f"{source} gives {_money(value)}, which is far from your list price {_money(list_price)}. "
            "Ignored it — check the address, ZIP and square footage."
        )
    warnings.append("No reliable market value found, so your list price is used as the current value.")
    return float(list_price), "your list price (no reliable market data)"


def _rent(
    list_price: float, sqft: int, beds: int, baths: float, city: str, rc_rent: float | None, warnings: list[str]
) -> tuple[float, str]:
    def ok(v: float | None) -> bool:
        return bool(v) and list_price > 0 and RENT_RATIO_MIN <= v / list_price <= RENT_RATIO_MAX

    if ok(rc_rent):
        return float(rc_rent), "RentCast rent estimate"
    if rc_rent:
        warnings.append(f"RentCast rent {_money(rc_rent)}/mo looks wrong for this price; ignored it.")
    table = _market_table(city)
    if table:
        est = round((sqft * table["rent_psf"] + beds * 80 + baths * 40) / 25) * 25
        if ok(est):
            return float(est), f"regional estimate table ({city.title()})"
    return float(round(list_price * RULE_OF_THUMB_RENT / 25) * 25), "rule of thumb (0.7% of price per month)"


def _neighborhood(city: str, zip_code: str) -> tuple[dict[str, Any], dict[str, str]]:
    market = rentcast.fetch_market_stats(zip_code) if zip_code else None
    table = _market_table(city)
    nb: dict[str, Any] = {"medianPrice": None, "medianRent": None, "appreciation": None, "schoolRating": None, "crimeIndex": None}
    src: dict[str, str] = {}
    if market:
        for k in ("medianPrice", "medianRent", "appreciation"):
            if market.get(k) is not None:
                nb[k] = market[k]
                src[k] = f"RentCast ZIP {zip_code}"
    if table:
        if nb["appreciation"] is None:
            nb["appreciation"] = table["appr"]
            src["appreciation"] = "regional estimate table"
        nb["schoolRating"] = table["school"]
        nb["crimeIndex"] = table["crime"]
        src["schoolRating"] = src["crimeIndex"] = "regional estimate table"
    return nb, src


def run_full_analysis(
    *,
    address: str,
    city: str,
    state: str,
    zip_code: str = "",
    property_type: str = "Single Family",
    list_price: float,
    sqft: int,
    beds: int,
    baths: float,
    gallery_urls: list[str] | None = None,
    image_rooms: list[str] | None = None,
    db: Session | None = None,
) -> dict[str, Any]:
    warnings: list[str] = []
    log: list[str] = ["[done] Property data saved"]
    gallery_urls = list(gallery_urls or [])

    # 1. Photos -> damage
    photos: list[dict] = []
    if gallery_urls and db is not None:
        photos = analyze_photos(gallery_urls, list(image_rooms or []), db)
    findings = [f for p in photos for f in p["findings"]]
    assessed = [p for p in photos if p["status"] == "assessed"]
    ai_used = sum(1 for p in photos if p["aiUsed"])
    engines = []
    if damage_inference.model_available():
        engines.append("YOLOv8 damage model")
    if ai_used:
        engines.append(f"Gemini vision ({ai_used} photo(s))")
    if not gallery_urls:
        log.append("[info] No photos uploaded — damage not assessed")
    elif not assessed:
        log.append("[warning] Photos could not be assessed (no damage model or AI vision available)")
    else:
        log.append(
            f"[done] Damage scan: {len(findings)} finding(s) in {len(assessed)} photo(s) using " + " + ".join(engines)
        )
    for p in photos:
        n = p["index"] + 1
        if p["status"] == "not_property":
            warnings.append(f"Photo {n} does not look like a property photo — skipped.")
        elif p["status"] == "missing":
            warnings.append(f"Photo {n} file is missing on the server.")
        if p["aiNote"] and p["status"] != "missing" and gemini_vision.configured():
            log.append(f"[info] Photo {n}: {p['aiNote']}")
        for r in p["rejectedDetections"]:
            log.append(f"[info] Photo {n}: AI rejected a YOLO \"{r['yoloClass']}\" box — {r['reason']}")

    # 2. Rehab
    rehab_est = rehab.estimate(findings, sqft, photos_assessed=bool(assessed))
    rehab_cost = rehab_est["total"]
    if rehab_est["note"]:
        log.append(f"[info] {rehab_est['note']}")
    log.append(f"[done] Rehab estimate {_money(rehab_cost)} from {len(rehab_est['items'])} line item(s)")

    # 3. Market data
    full_address = rentcast.format_full_address(address, city, state, zip_code)
    rc_value = rentcast.fetch_value_and_comps(
        full_address=full_address, property_type=property_type, beds=beds, baths=baths, sqft=sqft
    )
    comps = rentcast.normalize_comps(rc_value, subject_sqft=sqft) if rc_value else []
    if not rentcast.configured():
        log.append("[info] Comparable sales unavailable — RentCast API key not configured")
    elif rc_value is None:
        log.append("[warning] RentCast lookup failed for this address")
    else:
        log.append(f"[done] {len(comps)} comparable sale(s) from RentCast within ±{rentcast.COMP_SQFT_TOLERANCE} sqft")

    avm = rentcast.avm_price(rc_value) if rc_value else None
    as_is, value_source = _as_is_value(list_price, sqft, city, avm, comps, warnings)
    arv = float(round((as_is + rehab_est["repairs"]) / 1000) * 1000)
    log.append(f"[done] ARV {_money(arv)} = current value ({value_source}) + {_money(rehab_est['repairs'])} of repairs")

    rc_rent = rentcast.fetch_rent_estimate(
        full_address=full_address, property_type=property_type, beds=beds, baths=baths, sqft=sqft
    )
    rent, rent_source = _rent(list_price, sqft, beds, baths, city, rc_rent, warnings)
    log.append(f"[done] Rent {_money(rent)}/mo from {rent_source}")

    neighborhood, nb_sources = _neighborhood(city, zip_code)
    if nb_sources:
        log.append("[done] Neighborhood data: " + ", ".join(sorted(set(nb_sources.values()))))
    else:
        log.append("[info] Neighborhood data unavailable for this location")

    # 4. Deal metrics
    profit = deal_engine.compute_profit(arv, list_price, rehab_cost)
    roi = deal_engine.compute_roi(profit, list_price, rehab_cost)
    max_offer = deal_engine.compute_max_offer(arv, rehab_cost)
    strategy = deal_engine.recommend_strategy(roi, profit, rent, list_price, neighborhood["appreciation"])
    sev = [{"low": 0.25, "medium": 0.55, "high": 0.85}[f["severity"]] for f in findings]
    rank = deal_engine.compute_rank_score(
        roi,
        profit,
        neighborhood["appreciation"],
        neighborhood["crimeIndex"],
        neighborhood["schoolRating"],
        max(sev) if sev else 0.2,
    )
    log.append(f"[done] Deal metrics: profit {_money(profit)}, ROI {roi}%, strategy {strategy}")

    stages = [
        "Property data saved",
        f"Damage scan ({len(findings)} finding(s))" if assessed else "Damage scan skipped (no assessable photos)",
        "Rehab cost itemised",
        "Market value and comps checked",
        "Deal metrics calculated",
        "Strategy recommended",
        "Report ready",
    ]

    return {
        "stages": stages,
        "rehab_cost": rehab_cost,
        "arv": arv,
        "monthly_rent": rent,
        "profit": profit,
        "roi": roi,
        "max_offer": max_offer,
        "strategy": strategy,
        "rank_score": rank,
        "damages": findings,
        "comps": comps,
        "neighborhood": neighborhood,
        "analysis_log": log,
        "photo_analyses": photos,
        "rehab_items": rehab_est["items"],
        "valuation": {
            "asIsValue": as_is,
            "asIsSource": value_source,
            "repairsValue": rehab_est["repairs"],
            "rentcastAvm": avm,
            "rentSource": rent_source,
            "neighborhoodSources": nb_sources,
            "rehabNote": rehab_est["note"],
        },
        "warnings": warnings,
        "image_url": pick_image(address),
    }
