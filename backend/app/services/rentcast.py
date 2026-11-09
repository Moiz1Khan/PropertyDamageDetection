"""RentCast market data — comps, AVM, rent (US addresses)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ..config import settings

logger = logging.getLogger(__name__)

BASE = "https://api.rentcast.io/v1"

PROP_TYPE_MAP = {
    "Single Family": "Single Family",
    "Duplex": "Multi-Family",
    "Townhouse": "Townhouse",
    "Multi-family": "Multi-Family",
    "Condo": "Condo",
}


def _headers() -> dict[str, str]:
    return {"Accept": "application/json", "X-Api-Key": settings.rentcast_api_key}


def format_full_address(address: str, city: str, state: str, zip_code: str) -> str:
    z = (zip_code or "").strip()
    return f"{address.strip()}, {city.strip()}, {state.strip()}" + (f", {z}" if z else "")


def fetch_value_and_comps(
    *,
    full_address: str,
    property_type: str,
    beds: int,
    baths: float,
    sqft: int,
) -> dict[str, Any] | None:
    if not settings.rentcast_api_key:
        return None
    params: dict[str, Any] = {
        "address": full_address,
        "propertyType": PROP_TYPE_MAP.get(property_type, "Single Family"),
        "bedrooms": beds,
        "bathrooms": baths,
        "squareFootage": sqft,
        "compCount": 8,
        "maxRadius": 2.0,
        "daysOld": 365,
        "lookupSubjectAttributes": True,
    }
    try:
        with httpx.Client(timeout=25.0) as client:
            r = client.get(f"{BASE}/avm/value", headers=_headers(), params=params)
            if r.status_code != 200:
                logger.warning("RentCast value API %s: %s", r.status_code, r.text[:300])
                return None
            return r.json()
    except Exception as exc:
        logger.warning("RentCast value request failed: %s", exc)
        return None


def fetch_rent_estimate(
    *,
    full_address: str,
    property_type: str,
    beds: int,
    baths: float,
    sqft: int,
) -> float | None:
    if not settings.rentcast_api_key:
        return None
    params: dict[str, Any] = {
        "address": full_address,
        "propertyType": PROP_TYPE_MAP.get(property_type, "Single Family"),
        "bedrooms": beds,
        "bathrooms": baths,
        "squareFootage": sqft,
        "compCount": 5,
    }
    try:
        with httpx.Client(timeout=25.0) as client:
            r = client.get(f"{BASE}/avm/rent/long-term", headers=_headers(), params=params)
            if r.status_code != 200:
                logger.warning("RentCast rent API %s: %s", r.status_code, r.text[:300])
                return None
            data = r.json()
            rent = data.get("rent") or data.get("rentEstimate") or data.get("price")
            return float(rent) if rent else None
    except Exception as exc:
        logger.warning("RentCast rent request failed: %s", exc)
        return None


def normalize_comps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("comparables") or payload.get("comps") or []
    comps: list[dict[str, Any]] = []
    for i, c in enumerate(raw[:8]):
        addr = c.get("formattedAddress") or c.get("address") or "Comparable sale"
        if isinstance(addr, dict):
            addr = addr.get("line1") or str(addr)
        sale = c.get("price") or c.get("lastSalePrice") or c.get("soldPrice") or 0
        sqft = int(c.get("squareFootage") or c.get("sqft") or 0)
        sold = c.get("lastSaleDate") or c.get("soldDate") or c.get("removedDate") or ""
        if sold and "T" in str(sold):
            sold = str(sold).split("T", 1)[0]
        dist = c.get("distance") or c.get("correlation")
        if isinstance(dist, (int, float)) and dist > 50:
            dist = round(dist / 5280, 2) if dist > 20 else round(float(dist), 2)
        else:
            dist = round(float(dist or 0.2 + i * 0.1), 2)
        comps.append(
            {
                "id": c.get("id") or f"rc-{i+1}",
                "address": str(addr)[:80],
                "salePrice": float(sale or 0),
                "distance": float(dist),
                "sqft": sqft,
                "soldDate": str(sold)[:10] if sold else "—",
            }
        )
    return [c for c in comps if c["salePrice"] > 0]


def avm_price(payload: dict[str, Any]) -> float | None:
    for key in ("price", "value", "valueEstimate", "avm"):
        val = payload.get(key)
        if val is not None:
            return float(val)
    return None
