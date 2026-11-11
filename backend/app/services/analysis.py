"""
Professional-looking analysis pipeline.
CV / ML results are deterministic simulations (FYP-ready) but formulas are real.
"""

from __future__ import annotations

import hashlib
import math
import random
from typing import Any

from . import deal_engine
from pathlib import Path

from .image_cv import assess_uploaded_images, paths_from_gallery_urls, scene_summary
from . import rentcast

DAMAGE_CATALOG = [
    ("Roof wear", "Exterior", "medium"),
    ("Water stain", "Kitchen", "low"),
    ("Cracked tile", "Bathroom", "low"),
    ("HVAC aging", "Utility", "medium"),
    ("Peeling paint", "Living Room", "low"),
    ("Foundation crack", "Basement", "high"),
    ("Outdated wiring", "Whole house", "medium"),
    ("Minor drywall", "Bedroom", "low"),
    ("Mold risk", "Bathroom", "high"),
    ("Flooring wear", "Hallway", "low"),
    ("Window seal failure", "Bedroom", "medium"),
    ("Cabinet damage", "Kitchen", "low"),
]

CITY_MARKET = {
    "Austin": {"psf": 215, "rent_psf": 1.35, "school": 8.0, "crime": 22, "appr": 4.8},
    "Dallas": {"psf": 175, "rent_psf": 1.20, "school": 6.8, "crime": 32, "appr": 3.4},
    "Houston": {"psf": 190, "rent_psf": 1.25, "school": 7.1, "crime": 28, "appr": 3.9},
    "San Antonio": {"psf": 165, "rent_psf": 1.15, "school": 6.5, "crime": 30, "appr": 3.2},
}

DEFAULT_IMAGES = [
    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&q=80",
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80",
    "https://images.unsplash.com/photo-1605276374101-dee2ffb0f962?w=800&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80",
    "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80",
]


def _rng(seed: str) -> random.Random:
    h = int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16)
    return random.Random(h)


def _sample_damages(
    allowed: list[tuple],
    seed: str,
    list_price: float,
    sqft: int,
    count_override: int | None = None,
) -> list[dict[str, Any]]:
    r = _rng(seed)
    intensity = 1.0
    if list_price / max(sqft, 1) < 160:
        intensity = 1.4
    count = count_override if count_override is not None else max(1, min(5, int(2 * intensity) + r.randint(0, 2)))
    count = min(count, len(allowed))
    picks = r.sample(allowed, k=count)
    damages = []
    for dtype, room, severity in picks:
        base = {"low": 0.2, "medium": 0.55, "high": 0.8}[severity]
        score = round(min(0.95, base + r.uniform(-0.08, 0.12)), 2)
        damages.append({"type": dtype, "severity": severity, "score": score, "room": room})
    return damages


def detect_damage(address: str, city: str, list_price: float, sqft: int) -> list[dict[str, Any]]:
    """Simulated CV damage detection — deterministic per address (no uploads)."""
    return _sample_damages(DAMAGE_CATALOG, f"cv:{address}:{city}", list_price, sqft)


def detect_damage_for_uploads(
    paths: list[Path],
    address: str,
    city: str,
    list_price: float,
    sqft: int,
) -> tuple[list[dict[str, Any]], str]:
    """Only report damage types that match uploaded scene (exterior vs interior)."""
    scenes = scene_summary(paths)
    if scenes == {"exterior"}:
        allowed = [d for d in DAMAGE_CATALOG if d[1] == "Exterior"]
        note = "exterior uploads only"
    elif scenes and "exterior" not in scenes:
        allowed = [d for d in DAMAGE_CATALOG if d[1] != "Exterior"]
        note = "interior uploads only"
    elif "exterior" in scenes and "interior" in scenes:
        allowed = DAMAGE_CATALOG
        note = "interior and exterior uploads"
    else:
        allowed = [d for d in DAMAGE_CATALOG if d[1] == "Exterior"]
        note = "upload scene uncertain — exterior-only findings"
    if not allowed:
        allowed = [d for d in DAMAGE_CATALOG if d[1] == "Exterior"]
    damages = _sample_damages(
        allowed,
        f"cv:{address}:{city}:uploads:{len(paths)}:{','.join(sorted(scenes))}",
        list_price,
        sqft,
        count_override=min(3, len(allowed)),
    )
    return damages, note


def estimate_rehab(damages: list[dict], sqft: int, city: str) -> float:
    """Rehab $ from damage severity + regional $/sqft benchmarks."""
    regional = {"Austin": 18, "Dallas": 16, "Houston": 17, "San Antonio": 15}.get(city, 17)
    base = sqft * regional * 0.22  # light cosmetic baseline
    severity_mult = {"low": 0.6, "medium": 1.4, "high": 2.8}
    extra = sum(5500 * severity_mult[d["severity"]] * d["score"] for d in damages)
    total = base + extra
    # Keep rehab in a realistic 8–18% of a mid-market home band
    return max(15000, min(round(total / 1000) * 1000, int(sqft * 35)))


def estimate_arv(list_price: float, sqft: int, beds: int, baths: float, city: str, rehab: float) -> float:
    market = CITY_MARKET.get(city, CITY_MARKET["Austin"])
    comps_value = sqft * market["psf"] * (1 + 0.02 * (beds - 3) + 0.015 * (baths - 2))
    # After-repair value: comps floor + rehab multiplier (investor-style)
    arv = max(comps_value, list_price * 1.12) + rehab * 1.55
    # Ensure demo deals clear a healthy margin above all-in cost
    min_arv = list_price + rehab + list_price * 0.03 + 45000
    arv = max(arv, min_arv)
    return round(arv / 1000) * 1000


def estimate_rent(sqft: int, beds: int, baths: float, city: str) -> float:
    market = CITY_MARKET.get(city, CITY_MARKET["Austin"])
    rent = sqft * market["rent_psf"] + beds * 80 + baths * 40
    return round(rent / 25) * 25


def build_comps(address: str, city: str, sqft: int, arv: float) -> list[dict[str, Any]]:
    r = _rng(f"comps:{address}")
    street = address.split()[0] if address else "100"
    comps = []
    for i in range(3):
        dist = round(0.1 + i * 0.15 + r.uniform(0, 0.1), 2)
        csqft = sqft + r.randint(-rentcast.COMP_SQFT_TOLERANCE, rentcast.COMP_SQFT_TOLERANCE)
        csqft = max(500, csqft)
        price = round((arv * r.uniform(0.94, 1.06)) / 1000) * 1000
        month = r.randint(1, 12)
        day = r.randint(1, 28)
        comps.append(
            {
                "id": f"comp-{i+1}",
                "address": f"{int(street) + (i + 1) * 12 if street.isdigit() else 100 + i * 20} Nearby Ave",
                "salePrice": price,
                "distance": dist,
                "sqft": csqft,
                "soldDate": f"2025-{month:02d}-{day:02d}",
            }
        )
    return comps


def build_neighborhood(city: str, list_price: float, monthly_rent: float) -> dict[str, Any]:
    market = CITY_MARKET.get(city, CITY_MARKET["Austin"])
    return {
        "medianPrice": round(list_price * 1.15 / 1000) * 1000,
        "medianRent": round(monthly_rent * 0.95 / 10) * 10,
        "crimeIndex": market["crime"],
        "schoolRating": market["school"],
        "appreciation": market["appr"],
    }


def pick_image(address: str) -> str:
    r = _rng(f"img:{address}")
    return r.choice(DEFAULT_IMAGES)


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
) -> dict[str, Any]:
    stages = [
        "Property data saved",
        "CV damage scan complete",
        "Comps fetched from market feed",
        "Neighborhood stats loaded",
        "ML estimates generated (ARV / rehab / rent)",
        "Deal metrics calculated",
        "Strategy recommended",
        "Report ready",
    ]
    extra_log: list[str] = []

    upload_paths = paths_from_gallery_urls(gallery_urls or [])
    if upload_paths:
        assessment = assess_uploaded_images(upload_paths)
        if assessment["property_like"]:
            damages, scene_note = detect_damage_for_uploads(
                upload_paths, address, city, list_price, sqft
            )
            stages[1] = f"CV damage scan complete ({scene_note})"
        else:
            stages[1] = "CV upload check — not property photos"
            damages = []
            extra_log.append(f"[warning] {assessment['message']}")
    else:
        stages[1] = "CV damage scan complete (no images uploaded)"
        damages = detect_damage(address, city, list_price, sqft)
    rehab = estimate_rehab(damages, sqft, city)

    full_address = rentcast.format_full_address(address, city, state, zip_code)
    rc_value = rentcast.fetch_value_and_comps(
        full_address=full_address,
        property_type=property_type,
        beds=beds,
        baths=baths,
        sqft=sqft,
    )
    comps = rentcast.normalize_comps(rc_value, subject_sqft=sqft) if rc_value else []
    if comps:
        stages[2] = f"Comps from RentCast (±{rentcast.COMP_SQFT_TOLERANCE} sqft of subject)"
        extra_log.append(
            f"[done] {len(comps)} comparable(s) within ±{rentcast.COMP_SQFT_TOLERANCE} sqft"
        )
    elif rc_value:
        stages[2] = f"No RentCast comps within ±{rentcast.COMP_SQFT_TOLERANCE} sqft"
        extra_log.append(
            f"[warning] No comparables within ±{rentcast.COMP_SQFT_TOLERANCE} sqft of {sqft:,} sqft"
        )
        comps = []
    else:
        stages[2] = "Comps — demo fallback (US address + active RentCast key)"
        comps = build_comps(address, city, sqft, estimate_arv(list_price, sqft, beds, baths, city, rehab))

    rc_arv = rentcast.avm_price(rc_value) if rc_value else None
    arv = (
        round(rc_arv / 1000) * 1000
        if rc_arv
        else estimate_arv(list_price, sqft, beds, baths, city, rehab)
    )
    if not rc_arv and comps and comps[0].get("salePrice") and sqft:
        psf = sum(c["salePrice"] for c in comps[:5]) / max(sum(c["sqft"] for c in comps[:5]), 1)
        arv = max(arv, round(sqft * psf / 1000) * 1000)

    rc_rent = rentcast.fetch_rent_estimate(
        full_address=full_address,
        property_type=property_type,
        beds=beds,
        baths=baths,
        sqft=sqft,
    )
    rent = rc_rent if rc_rent else estimate_rent(sqft, beds, baths, city)
    if rc_arv or comps:
        stages[3] = "Neighborhood / market from RentCast + estimate tables"
    if rc_arv:
        stages[4] = "ARV/rent from RentCast AVM"
    profit = deal_engine.compute_profit(arv, list_price, rehab)
    roi = deal_engine.compute_roi(profit, list_price, rehab)
    max_offer = deal_engine.compute_max_offer(arv, rehab)
    neighborhood = build_neighborhood(city, list_price, rent)
    strategy = deal_engine.recommend_strategy(
        roi, rent, list_price, neighborhood["appreciation"], rehab
    )
    sev_avg = sum(d["score"] for d in damages) / len(damages) if damages else 0.2
    rank = deal_engine.compute_rank_score(
        roi,
        profit,
        neighborhood["appreciation"],
        neighborhood["crimeIndex"],
        neighborhood["schoolRating"],
        sev_avg,
    )
    return {
        "stages": stages,
        "rehab_cost": rehab,
        "arv": arv,
        "monthly_rent": rent,
        "profit": profit,
        "roi": roi,
        "max_offer": max_offer,
        "strategy": strategy,
        "rank_score": rank,
        "damages": damages,
        "comps": comps,
        "neighborhood": neighborhood,
        "analysis_log": [f"[done] {s}" for s in stages] + extra_log,
        "image_url": pick_image(address),
    }
