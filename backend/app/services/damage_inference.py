"""YOLOv8n damage detector (trained in ml/). Weights: backend/models/damage_yolov8n/best.pt."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# YOLO class name -> damage category used across the app
YOLO_TO_CATEGORY: dict[str, str] = {
    "crack": "crack",
    "stairstep_crack": "structural",
    "stain": "water_damage",
    "damp": "water_damage",
    "dampness": "water_damage",
    "water_seepage": "water_damage",
    "mold": "mold",
    "peeling_paint": "peeling_paint",
    # numeric aliases some Roboflow exports use
    "0": "crack",
    "1": "water_damage",
}

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "models" / "damage_yolov8n" / "best.pt"
CONF_THRESHOLD = 0.35
_IOU = 0.45

_model = None
_load_failed = False


def _get_model():
    global _model, _load_failed
    if _model is not None or _load_failed:
        return _model
    if not MODEL_PATH.is_file():
        return None
    try:
        from ultralytics import YOLO

        _model = YOLO(str(MODEL_PATH))
    except Exception as exc:  # ImportError, corrupt weights, ...
        logger.warning("YOLO model could not be loaded: %s", exc)
        _load_failed = True
        return None
    return _model


def model_available() -> bool:
    return _get_model() is not None


def detect_boxes(path: Path) -> list[dict]:
    """Return detections for one image: category, confidence and a box in 0-1 coordinates [x1, y1, x2, y2]."""
    model = _get_model()
    if model is None:
        return []
    try:
        results = model.predict(source=str(path), conf=CONF_THRESHOLD, iou=_IOU, verbose=False, device="cpu")
    except Exception as exc:
        logger.warning("YOLO inference failed on %s: %s", path.name, exc)
        return []
    if not results:
        return []
    res = results[0]
    names = res.names or {}
    out: list[dict] = []
    for box in res.boxes or []:
        cls_name = str(names.get(int(box.cls[0]), int(box.cls[0]))).strip().lower().replace(" ", "_")
        category = YOLO_TO_CATEGORY.get(cls_name)
        if not category:
            continue
        x1, y1, x2, y2 = (float(v) for v in box.xyxyn[0].tolist())
        out.append(
            {
                "category": category,
                "yoloClass": cls_name,
                "confidence": round(float(box.conf[0]), 2),
                "box": [round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4)],
            }
        )
    out.sort(key=lambda d: -d["confidence"])
    return out
