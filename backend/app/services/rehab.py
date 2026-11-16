"""Itemised rehab estimate from detected damage.

Unit costs are rough US national averages for planning (contractor labour + materials).
They are deliberately simple and visible so every number on the report can be explained.
"""

from __future__ import annotations

from typing import Any

# category -> (fixed cost per repair, cost per affected sqft)
UNIT_COSTS: dict[str, tuple[float, float]] = {
    "crack": (300, 15),
    "structural": (3000, 60),
    "water_damage": (500, 12),
    "mold": (600, 25),
    "peeling_paint": (150, 4),
    "wall_damage": (250, 8),
    "ceiling_damage": (400, 10),
    "roof_damage": (1500, 10),
    "window_damage": (450, 0),
    "door_damage": (350, 0),
    "flooring_damage": (300, 9),
    "plumbing": (800, 0),
    "electrical": (1000, 0),
    "fire_damage": (2500, 30),
    "other": (500, 8),
}
# Per-item categories: area is a count of items (windows, doors), not sqft
PER_ITEM = {"window_damage", "door_damage"}
SEVERITY_MULT = {"low": 0.75, "medium": 1.0, "high": 1.6}
DEFAULT_AREA = {"low": 5.0, "medium": 15.0, "high": 40.0}
COSMETIC_PER_SQFT = 2.5  # paint touch-ups, cleaning, fixtures on any purchase
CONTINGENCY = 0.10
SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2}


def _repair_cost(category: str, severity: str, area: float | None) -> float:
    fixed, per_sqft = UNIT_COSTS.get(category, UNIT_COSTS["other"])
    mult = SEVERITY_MULT.get(severity, 1.0)
    if category in PER_ITEM:
        count = max(1.0, round(area or 1))
        return fixed * count * mult
    area = area if area and area > 0 else DEFAULT_AREA.get(severity, 15.0)
    return (fixed + per_sqft * area) * mult


def estimate(findings: list[dict], sqft: int, photos_assessed: bool) -> dict[str, Any]:
    """Group findings by (category, room) so the same damage seen in two photos is paid for once."""
    groups: dict[tuple[str, str], dict] = {}
    for f in findings:
        key = (f["category"], f["room"])
        g = groups.get(key)
        if g is None:
            groups[key] = {**f}
            continue
        if SEVERITY_RANK[f["severity"]] > SEVERITY_RANK[g["severity"]]:
            g["severity"] = f["severity"]
        g["areaSqft"] = max(g.get("areaSqft") or 0, f.get("areaSqft") or 0) or None

    items: list[dict] = []
    for (category, room), g in sorted(groups.items()):
        cost = _repair_cost(category, g["severity"], g.get("areaSqft"))
        area_txt = (
            f"{int(round(g['areaSqft'] or 1))} item(s)" if category in PER_ITEM
            else f"~{g['areaSqft']:g} sqft" if g.get("areaSqft") else "area estimated from severity"
        )
        items.append(
            {
                "label": f"{g['type']} — {room}",
                "category": category,
                "severity": g["severity"],
                "detail": area_txt,
                "cost": round(cost / 50) * 50,
            }
        )

    cosmetic = round(sqft * COSMETIC_PER_SQFT / 50) * 50
    items.append(
        {
            "label": "General cosmetic refresh (paint, cleaning, fixtures)",
            "category": "cosmetic",
            "severity": "low",
            "detail": f"{sqft:,} sqft × ${COSMETIC_PER_SQFT}/sqft",
            "cost": cosmetic,
        }
    )
    subtotal = sum(i["cost"] for i in items)
    contingency = round(subtotal * CONTINGENCY / 50) * 50
    items.append(
        {
            "label": "Contingency (10%)",
            "category": "contingency",
            "severity": "low",
            "detail": "unknowns found during work",
            "cost": contingency,
        }
    )
    repairs = sum(i["cost"] for i in items if i["category"] not in ("cosmetic", "contingency"))
    total = subtotal + contingency
    return {
        "items": items,
        "total": float(round(total / 500) * 500),
        "repairs": float(repairs),
        "note": "" if photos_assessed else "No photos assessed — rehab covers cosmetic refresh only. Upload photos for a damage-based estimate.",
    }
