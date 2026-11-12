"""YOLOv8 damage inference when backend/models/damage_yolov8n/best.pt exists."""

from __future__ import annotations

from pathlib import Path

from .image_cv import classify_scene

# Repo-local class map (no ml package import required on server)
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

MODEL_PATH = (
    Path(__file__).resolve().parent.parent.parent / "models" / "damage_yolov8n" / "best.pt"
)
CONF_THRESHOLD = 0.35
_IOU = 0.45

_model = None


def model_available() -> bool:
    return MODEL_PATH.is_file()


def _confidence_to_severity(conf: float) -> str:
    if conf >= 0.72:
        return "high"
    if conf >= 0.45:
        return "medium"
    return "low"


def _get_model():
    global _model
    if _model is not None:
        return _model
    if not MODEL_PATH.is_file():
        return None
    try:
        from ultralytics import YOLO
    except ImportError:
        return None
    _model = YOLO(str(MODEL_PATH))
    return _model


def _map_box(class_name: str, conf: float, scene: str, image_index: int) -> dict | None:
    key = (class_name or "").strip().lower().replace(" ", "_")
    row = YOLO_TO_DAMAGE.get(key)
    if not row:
        return None
    dtype, room = row
    if scene == "exterior" and room == "Bathroom" and dtype == "Mold risk":
        room = "Exterior"
    if scene == "interior" and room == "Exterior":
        room = "Interior"
    return {
        "type": dtype,
        "severity": _confidence_to_severity(conf),
        "score": round(min(0.98, max(0.15, conf)), 2),
        "room": room,
        "source": "yolov8",
        "image_index": image_index,
        "cv_class": key,
    }


def detect_damages_yolo(paths: list[Path]) -> tuple[list[dict], str]:
    model = _get_model()
    if model is None:
        return [], "yolo model or ultralytics not available"

    merged: dict[tuple[str, str], dict] = {}
    for idx, path in enumerate(paths):
        scene = classify_scene(path)
        results = model.predict(
            source=str(path),
            conf=CONF_THRESHOLD,
            iou=_IOU,
            verbose=False,
            device="cpu",
        )
        if not results:
            continue
        names = results[0].names or {}
        for box in results[0].boxes or []:
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cname = names.get(cls_id, str(cls_id))
            row = _map_box(cname, conf, scene, idx)
            if not row:
                continue
            key = (row["type"], row["room"])
            existing = merged.get(key)
            if existing is None or row["score"] > existing["score"]:
                merged[key] = row

    damages = sorted(merged.values(), key=lambda d: -d["score"])
    if damages:
        return damages, f"YOLOv8n — {len(damages)} defect type(s) across {len(paths)} image(s)"
    return [], "YOLOv8n — no damage detected above confidence threshold"
