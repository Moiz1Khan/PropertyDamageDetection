"""Lightweight upload checks before simulated / trained CV."""

from __future__ import annotations

import statistics
from pathlib import Path

from PIL import Image

UPLOAD_ROOT = Path(__file__).resolve().parent.parent.parent / "uploads"

PROPERTY_SCORE_THRESHOLD = 0.42


def paths_from_gallery_urls(urls: list[str]) -> list[Path]:
    paths: list[Path] = []
    for url in urls:
        if not url:
            continue
        if url.startswith("/api/uploads/"):
            rel = url.removeprefix("/api/uploads/").lstrip("/")
            p = UPLOAD_ROOT / rel
        elif url.startswith("http") and "/api/uploads/" in url:
            rel = url.split("/api/uploads/", 1)[1]
            p = UPLOAD_ROOT / rel
        else:
            continue
        if p.is_file():
            paths.append(p)
    return paths


def property_photo_score(path: Path) -> float:
    """0–1 likelihood of interior/exterior property photo (heuristic)."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    img = img.resize((256, 256))
    px = list(img.getdata())

    def bright(r: int, g: int, b: int) -> bool:
        return r > 228 and g > 228 and b > 228

    border: list[tuple[int, int, int]] = []
    for y in range(256):
        for x in range(256):
            if x < 24 or x > 231 or y < 24 or y > 231:
                border.append(px[y * 256 + x])
    center = [px[y * 256 + x] for y in range(72, 184) for x in range(72, 184)]

    border_bright = sum(1 for r, g, b in border if bright(r, g, b)) / max(len(border), 1)
    center_bright = sum(1 for r, g, b in center if bright(r, g, b)) / max(len(center), 1)
    variance = (
        statistics.pvariance([p[0] for p in px])
        + statistics.pvariance([p[1] for p in px])
        + statistics.pvariance([p[2] for p in px])
    )

    score = 0.48
    # product / catalog shot on white (e.g. bag, furniture cutout)
    if border_bright > 0.62 and center_bright < 0.42:
        score -= 0.38
    if variance > 1400:
        score += 0.22
    if variance < 700 and border_bright > 0.5:
        score -= 0.15
    aspect = w / max(h, 1)
    if aspect > 1.25:
        score += 0.12

    return round(max(0.0, min(1.0, score)), 2)


def classify_scene(path: Path) -> str:
    """Guess exterior vs interior from color layout (heuristic until YOLOv8n)."""
    img = Image.open(path).convert("RGB").resize((256, 256))
    top = [img.getpixel((x, y)) for y in range(0, 80) for x in range(256)]
    bottom = [img.getpixel((x, y)) for y in range(176, 256) for x in range(256)]

    def sky_ratio(samples: list[tuple[int, int, int]]) -> float:
        return sum(
            1 for r, g, b in samples if b > r + 12 and b >= g and (r + g + b) / 3 > 90
        ) / max(len(samples), 1)

    def grass_ratio(samples: list[tuple[int, int, int]]) -> float:
        return sum(1 for r, g, b in samples if g > r + 8 and g > b and g > 70) / max(len(samples), 1)

    sky = sky_ratio(top)
    grass = grass_ratio(bottom)
    if sky > 0.08 or (sky > 0.04 and grass > 0.06):
        return "exterior"
    if sky < 0.03:
        return "interior"
    return "unknown"


def scene_summary(paths: list[Path]) -> set[str]:
    scenes: set[str] = set()
    for p in paths:
        scenes.add(classify_scene(p))
    scenes.discard("unknown")
    return scenes


def assess_uploaded_images(paths: list[Path]) -> dict:
    if not paths:
        return {"property_like": False, "scores": [], "message": "No image files found"}
    scores = [property_photo_score(p) for p in paths]
    avg = sum(scores) / len(scores)
    prop_like = avg >= PROPERTY_SCORE_THRESHOLD and max(scores) >= PROPERTY_SCORE_THRESHOLD
    if prop_like:
        return {
            "property_like": True,
            "scores": scores,
            "message": "Uploaded images appear to be property photos.",
        }
    return {
        "property_like": False,
        "scores": scores,
        "message": (
            "Uploaded images do not look like interior or exterior property photos. "
            "Please upload room, kitchen, bathroom, or building exterior images."
        ),
    }
