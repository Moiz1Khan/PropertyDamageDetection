"""Gemini vision: room type, visible damage, and review of YOLO boxes for one property photo.

Free tier limits (flash-lite): ~15 requests/minute, ~500/day. We pace calls, cache results by
image hash, and never fail the analysis because of Gemini - callers fall back to YOLO only.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import logging
import threading
import time
from collections import deque
from pathlib import Path
from typing import Any

import httpx
from PIL import Image
from sqlalchemy.orm import Session

from ..config import settings
from ..models import ImageAnalysisCache

logger = logging.getLogger(__name__)

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
PROMPT_VERSION = "v1"
MAX_SIDE = 1280

ROOMS = [
    "kitchen", "bathroom", "bedroom", "living_room", "dining_room", "hallway", "basement",
    "attic", "garage", "laundry", "utility", "exterior", "roof", "yard", "unknown",
]
CATEGORIES = [
    "crack", "structural", "water_damage", "mold", "peeling_paint", "wall_damage", "ceiling_damage",
    "roof_damage", "window_damage", "door_damage", "flooring_damage", "plumbing", "electrical",
    "fire_damage", "other",
]

RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "is_property_photo": {"type": "BOOLEAN"},
        "scene": {"type": "STRING", "enum": ["interior", "exterior", "unknown"]},
        "room": {"type": "STRING", "enum": ROOMS},
        "room_confidence": {"type": "NUMBER"},
        "summary": {"type": "STRING"},
        "damages": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "category": {"type": "STRING", "enum": CATEGORIES},
                    "label": {"type": "STRING"},
                    "severity": {"type": "STRING", "enum": ["low", "medium", "high"]},
                    "extent_sqft": {"type": "NUMBER"},
                    "description": {"type": "STRING"},
                    "box_2d": {"type": "ARRAY", "items": {"type": "INTEGER"}},
                },
                "required": ["category", "label", "severity", "extent_sqft", "description"],
            },
        },
        "yolo_review": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "index": {"type": "INTEGER"},
                    "verdict": {"type": "STRING", "enum": ["confirmed", "rejected"]},
                    "reason": {"type": "STRING"},
                },
                "required": ["index", "verdict"],
            },
        },
    },
    "required": ["is_property_photo", "scene", "room", "room_confidence", "summary", "damages"],
}

PROMPT = """You are a licensed home inspector reviewing ONE photo for a real-estate investment analysis.

1. is_property_photo: true only if this is a photo of a building interior or exterior (rooms, walls, ceilings, roofs, facades, yards). False for products, people, documents, screenshots, vehicles, etc.
2. scene and room: what the photo actually shows. Use "unknown" for room when the photo is a close-up (e.g. just a wall or ceiling patch) and the room type cannot be determined. Do not guess. room_confidence is 0-1.
3. damages: every VISIBLE defect needing repair. Do not invent damage that is not visible; return an empty list for a clean photo. Normal wear that needs no repair is not damage.
   - severity: low = cosmetic/small, medium = needs a proper repair, high = large area, active leak, structural, or health risk.
   - extent_sqft: your best estimate of the affected area in square feet (windows/doors: 1 per item).
   - box_2d: [ymin, xmin, ymax, xmax] on a 0-1000 scale around the damage.
4. summary: one short sentence describing the photo and its condition.
{yolo_block}"""

YOLO_BLOCK = """5. yolo_review: a separate detector model proposed these boxes ([ymin, xmin, ymax, xmax], 0-1000 scale). For each index say "confirmed" if that damage is really there, or "rejected" if it is a false alarm, with a short reason:
{boxes}
"""


def configured() -> bool:
    return bool(settings.gemini_api_key)


class _RateLimiter:
    def __init__(self) -> None:
        self._calls: deque[float] = deque()
        self._lock = threading.Lock()

    def acquire(self, max_wait: float = 20.0) -> bool:
        deadline = time.monotonic() + max_wait
        while True:
            with self._lock:
                now = time.monotonic()
                while self._calls and now - self._calls[0] > 60:
                    self._calls.popleft()
                if len(self._calls) < settings.gemini_rpm_limit:
                    self._calls.append(now)
                    return True
                wait = 60 - (now - self._calls[0]) + 0.1
            if time.monotonic() + wait > deadline:
                return False
            time.sleep(min(wait, 2.0))


_limiter = _RateLimiter()


class VisionUnavailable(Exception):
    """Gemini could not be used for this image; reason is user-facing."""


def _prepare_image(path: Path) -> tuple[bytes, str]:
    with Image.open(path) as img:
        img = img.convert("RGB")
        img.thumbnail((MAX_SIDE, MAX_SIDE))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
    return buf.getvalue(), ""


def _yolo_to_gemini_boxes(yolo: list[dict]) -> str:
    lines = []
    for i, d in enumerate(yolo):
        x1, y1, x2, y2 = d["box"]
        lines.append(
            f'   index {i}: "{d["yoloClass"]}" ({d["confidence"]:.0%}) at '
            f"[{int(y1 * 1000)}, {int(x1 * 1000)}, {int(y2 * 1000)}, {int(x2 * 1000)}]"
        )
    return "\n".join(lines)


def _call(image_jpeg: bytes, prompt: str) -> dict:
    body = {
        "contents": [
            {
                "parts": [
                    {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image_jpeg).decode()}},
                    {"text": prompt},
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
            "temperature": 0.1,
        },
    }
    headers = {"x-goog-api-key": settings.gemini_api_key}
    url = API_URL.format(model=settings.gemini_model)
    last_error = "unknown error"
    for attempt in range(2):
        if not _limiter.acquire():
            raise VisionUnavailable("AI vision busy (per-minute limit) - used detector only")
        try:
            r = httpx.post(url, headers=headers, json=body, timeout=settings.gemini_timeout_seconds)
        except httpx.TimeoutException:
            last_error = "AI vision timed out"
            continue
        except httpx.HTTPError as exc:
            last_error = f"AI vision network error ({type(exc).__name__})"
            continue
        if r.status_code == 200:
            try:
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                data = json.loads(text)
            except (KeyError, IndexError, ValueError) as exc:
                raise VisionUnavailable(f"AI vision returned an unreadable answer ({type(exc).__name__})")
            if isinstance(data, list):  # some models wrap the object in a list
                data = data[0] if data else {}
            return data
        if r.status_code == 429:
            raise VisionUnavailable("AI vision quota reached (free tier limit) - used detector only")
        if r.status_code in (500, 502, 503, 504):
            last_error = f"AI vision temporarily unavailable ({r.status_code})"
            time.sleep(2)
            continue
        logger.warning("Gemini error %s: %s", r.status_code, r.text[:300])
        raise VisionUnavailable(f"AI vision error ({r.status_code})")
    raise VisionUnavailable(last_error)


def _clean(data: dict) -> dict:
    """Normalise the model output: clamp numbers, drop malformed items, convert boxes to 0-1 [x1,y1,x2,y2]."""
    out = {
        "is_property_photo": bool(data.get("is_property_photo", True)),
        "scene": data.get("scene") if data.get("scene") in ("interior", "exterior") else "unknown",
        "room": data.get("room") if data.get("room") in ROOMS else "unknown",
        "room_confidence": max(0.0, min(1.0, float(data.get("room_confidence") or 0))),
        "summary": str(data.get("summary") or "")[:300],
        "damages": [],
        "yolo_review": {},
    }
    for d in data.get("damages") or []:
        if not isinstance(d, dict):
            continue
        cat = d.get("category") if d.get("category") in CATEGORIES else "other"
        sev = d.get("severity") if d.get("severity") in ("low", "medium", "high") else "medium"
        box = None
        b = d.get("box_2d")
        if isinstance(b, list) and len(b) == 4 and all(isinstance(v, (int, float)) for v in b):
            ymin, xmin, ymax, xmax = (max(0.0, min(1000.0, float(v))) / 1000 for v in b)
            if xmax > xmin and ymax > ymin:
                box = [round(xmin, 4), round(ymin, 4), round(xmax, 4), round(ymax, 4)]
        out["damages"].append(
            {
                "category": cat,
                "label": str(d.get("label") or cat.replace("_", " ")).strip()[:60],
                "severity": sev,
                "extentSqft": round(max(0.0, min(5000.0, float(d.get("extent_sqft") or 0))), 1),
                "description": str(d.get("description") or "")[:300],
                "box": box,
            }
        )
    for r in data.get("yolo_review") or []:
        if isinstance(r, dict) and isinstance(r.get("index"), int) and r.get("verdict") in ("confirmed", "rejected"):
            out["yolo_review"][r["index"]] = {"verdict": r["verdict"], "reason": str(r.get("reason") or "")[:200]}
    return out


def cache_key(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashlib.sha256(f"{digest}:{settings.gemini_model}:{PROMPT_VERSION}".encode()).hexdigest()


def get_cached(key: str, db: Session) -> dict | None:
    cached = db.get(ImageAnalysisCache, key)
    if cached is None:
        return None
    result = dict(cached.result)
    result["yolo_review"] = {int(k): v for k, v in (result.get("yolo_review") or {}).items()}
    result["cached"] = True
    return result


def store(key: str, result: dict, db: Session) -> None:
    data = {k: v for k, v in result.items() if k != "cached"}
    db.merge(ImageAnalysisCache(image_hash=key, model=settings.gemini_model, result=data))
    db.commit()


def fetch(path: Path, yolo: list[dict]) -> dict:
    """Call Gemini for one photo (thread-safe, no DB access). Raises VisionUnavailable."""
    if not configured():
        raise VisionUnavailable("AI vision not configured")
    image_jpeg, _ = _prepare_image(path)
    prompt = PROMPT.format(yolo_block=YOLO_BLOCK.format(boxes=_yolo_to_gemini_boxes(yolo)) if yolo else "")
    result = _clean(_call(image_jpeg, prompt))
    result["cached"] = False
    return result
