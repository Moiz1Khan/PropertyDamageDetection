"""Map YOLO class names → OffmarketStream damage catalog fields."""

from __future__ import annotations

# severity from confidence
def confidence_to_severity(conf: float) -> str:
    if conf >= 0.72:
        return "high"
    if conf >= 0.45:
        return "medium"
    return "low"


YOLO_TO_DAMAGE: dict[str, tuple[str, str]] = {
    "crack": ("Cracked tile", "Interior"),
    "stairstep_crack": ("Foundation crack", "Basement"),
    "stain": ("Water stain", "Kitchen"),
    "damp": ("Water stain", "Kitchen"),
    "dampness": ("Water stain", "Kitchen"),
    "mold": ("Mold risk", "Bathroom"),
    "peeling_paint": ("Peeling paint", "Living Room"),
    "water_seepage": ("Water stain", "Bathroom"),
    "0": ("Cracked tile", "Interior"),
    "1": ("Water stain", "Interior"),
}

EXTERIOR_ALLOWED_TYPES = {
    "Roof wear",
    "Foundation crack",
    "Peeling paint",
    "Water stain",
    "Cracked tile",
}


def normalize_class_name(name: str) -> str:
    return (name or "").strip().lower().replace(" ", "_")


def map_detection(
    class_name: str,
    confidence: float,
    scene: str,
    image_index: int,
) -> dict | None:
    key = normalize_class_name(class_name)
    if key not in YOLO_TO_DAMAGE:
        return None
    dtype, default_room = YOLO_TO_DAMAGE[key]
    if scene == "exterior" and dtype not in EXTERIOR_ALLOWED_TYPES:
        # Still report crack/stain on exterior walls; skip mold-heavy labels tagged Bathroom
        if default_room == "Bathroom" and dtype == "Mold risk":
            default_room = "Exterior"
    elif scene == "interior" and default_room == "Exterior":
        default_room = "Interior"
    return {
        "type": dtype,
        "severity": confidence_to_severity(confidence),
        "score": round(min(0.98, max(0.15, confidence)), 2),
        "room": default_room,
        "source": "yolov8",
        "image_index": image_index,
        "cv_class": key,
    }
