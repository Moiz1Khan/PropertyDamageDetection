"""Per-photo damage analysis: YOLO boxes + Gemini room/damage review + the user's room tag.

Nothing here is random. If neither model can run, the photo is reported as "not assessed".
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from ..config import settings
from . import damage_inference, gemini_vision
from .image_cv import PROPERTY_SCORE_THRESHOLD, classify_scene, path_from_upload_url, property_photo_score

logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "crack": "Crack",
    "structural": "Structural / foundation crack",
    "water_damage": "Water damage / stain",
    "mold": "Mold",
    "peeling_paint": "Peeling paint",
    "wall_damage": "Wall damage",
    "ceiling_damage": "Ceiling damage",
    "roof_damage": "Roof damage",
    "window_damage": "Window damage",
    "door_damage": "Door damage",
    "flooring_damage": "Flooring damage",
    "plumbing": "Plumbing issue",
    "electrical": "Electrical issue",
    "fire_damage": "Fire / smoke damage",
    "other": "Other damage",
}

ROOM_LABELS = {
    "kitchen": "Kitchen", "bathroom": "Bathroom", "bedroom": "Bedroom", "living_room": "Living Room",
    "dining_room": "Dining Room", "hallway": "Hallway", "basement": "Basement", "attic": "Attic",
    "garage": "Garage", "laundry": "Laundry", "utility": "Utility", "exterior": "Exterior",
    "roof": "Roof", "yard": "Yard",
}
ROOM_CONFIDENCE_MIN = 0.5
NOT_SPECIFIED = "Room not specified"


def _severity_from_box(box: list[float]) -> str:
    x1, y1, x2, y2 = box
    frac = max(0.0, (x2 - x1) * (y2 - y1))
    if frac >= 0.15:
        return "high"
    if frac >= 0.04:
        return "medium"
    return "low"


def _resolve_room(user_room: str, ai: dict | None) -> tuple[str, str]:
    if user_room:
        return user_room, "user"
    if ai and ai["room"] != "unknown" and ai["room_confidence"] >= ROOM_CONFIDENCE_MIN:
        return ROOM_LABELS.get(ai["room"], ai["room"].replace("_", " ").title()), "ai"
    return NOT_SPECIFIED, "none"


def _build_photo(index: int, url: str, path: Path, user_room: str, yolo: list[dict], ai: dict | None, ai_note: str) -> dict[str, Any]:
    if ai is not None:
        is_property = ai["is_property_photo"]
        scene = ai["scene"]
    else:
        is_property = property_photo_score(path) >= PROPERTY_SCORE_THRESHOLD
        scene = classify_scene(path)

    room, room_source = _resolve_room(user_room, ai)
    findings: list[dict] = []
    rejected: list[dict] = []

    if is_property:
        if ai is not None:
            for d in ai["damages"]:
                findings.append(
                    {
                        "category": d["category"],
                        "type": d["label"][:1].upper() + d["label"][1:],
                        "severity": d["severity"],
                        "areaSqft": d["extentSqft"] or None,
                        "description": d["description"],
                        "box": d["box"],
                        "yoloBox": None,
                        "score": None,
                        "source": "ai",
                    }
                )
            for i, y in enumerate(yolo):
                review = ai["yolo_review"].get(i)
                match = next((f for f in findings if f["category"] == y["category"] and f["yoloBox"] is None), None)
                if review and review["verdict"] == "rejected" and match is None:
                    rejected.append({**y, "reason": review["reason"]})
                    continue
                if match is not None:
                    match["yoloBox"] = y["box"]
                    match["score"] = y["confidence"]
                    match["source"] = "ai+yolo"
                else:
                    confirmed = bool(review and review["verdict"] == "confirmed")
                    findings.append(_yolo_finding(y, "ai+yolo" if confirmed else "yolo"))
        else:
            findings = [_yolo_finding(y, "yolo") for y in yolo]

    for f in findings:
        f["room"] = room
        f["imageIndex"] = index

    if not is_property:
        status = "not_property"
    elif ai is None and not damage_inference.model_available():
        status = "not_assessed"
    else:
        status = "assessed"

    return {
        "index": index,
        "url": url,
        "status": status,
        "isPropertyPhoto": is_property,
        "scene": scene,
        "room": room,
        "roomSource": room_source,
        "aiRoom": ai["room"] if ai else None,
        "aiRoomConfidence": ai["room_confidence"] if ai else None,
        "summary": ai["summary"] if ai else "",
        "findings": findings,
        "yoloBoxes": yolo,
        "rejectedDetections": rejected,
        "aiUsed": ai is not None,
        "aiCached": bool(ai and ai.get("cached")),
        "aiNote": ai_note,
    }


def _yolo_finding(y: dict, source: str) -> dict:
    return {
        "category": y["category"],
        "type": CATEGORY_LABELS.get(y["category"], "Damage"),
        "severity": _severity_from_box(y["box"]),
        "areaSqft": None,
        "description": f'Detected by YOLOv8 model ("{y["yoloClass"]}")',
        "box": None,
        "yoloBox": y["box"],
        "score": y["confidence"],
        "source": source,
    }


def _missing(i: int, url: str, user_room: str) -> dict[str, Any]:
    return {
        "index": i, "url": url, "status": "missing", "isPropertyPhoto": False, "scene": "unknown",
        "room": user_room or NOT_SPECIFIED, "roomSource": "user" if user_room else "none",
        "aiRoom": None, "aiRoomConfidence": None, "summary": "", "findings": [], "yoloBoxes": [],
        "rejectedDetections": [], "aiUsed": False, "aiCached": False, "aiNote": "Image file not found",
    }


def analyze_photos(urls: list[str], rooms: list[str], db: Session) -> list[dict]:
    """YOLO on every photo, then Gemini on up to gemini_max_images photos (cached first, the rest in parallel)."""
    ai_on = gemini_vision.configured()
    jobs: list[dict] = []
    for i, url in enumerate(urls):
        jobs.append(
            {
                "i": i, "url": url, "path": path_from_upload_url(url),
                "room": (rooms[i] if i < len(rooms) else "") or "",
                "yolo": [], "ai": None, "note": "", "key": None,
            }
        )

    for j in jobs:
        if j["path"] is None:
            continue
        j["yolo"] = damage_inference.detect_boxes(j["path"])
        if not ai_on:
            j["note"] = "AI vision not configured"
        elif j["i"] >= settings.gemini_max_images:
            j["note"] = f"AI vision skipped (limit of {settings.gemini_max_images} photos per analysis)"
        else:
            j["key"] = gemini_vision.cache_key(j["path"])
            j["ai"] = gemini_vision.get_cached(j["key"], db)

    todo = [j for j in jobs if j["key"] and j["ai"] is None]
    if todo:
        with ThreadPoolExecutor(max_workers=min(4, len(todo))) as pool:
            futures = {pool.submit(gemini_vision.fetch, j["path"], j["yolo"]): j for j in todo}
            for fut in as_completed(futures):
                j = futures[fut]
                try:
                    j["ai"] = fut.result()
                except gemini_vision.VisionUnavailable as exc:
                    j["note"] = str(exc)
                except Exception as exc:  # never let the AI step break the analysis
                    logger.exception("Gemini analysis failed")
                    j["note"] = f"AI vision failed ({type(exc).__name__})"
        for j in todo:
            if j["ai"] is not None:
                gemini_vision.store(j["key"], j["ai"], db)

    return [
        _missing(j["i"], j["url"], j["room"]) if j["path"] is None
        else _build_photo(j["i"], j["url"], j["path"], j["room"], j["yolo"], j["ai"], j["note"])
        for j in jobs
    ]
