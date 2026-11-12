#!/usr/bin/env python3
"""One-off server smoke test for YOLO — scp to server and run in backend venv."""
from pathlib import Path

from ultralytics import YOLO

from app.services.damage_inference import detect_damages_yolo, model_available

print("model_available:", model_available())
m = YOLO("models/damage_yolov8n/best.pt")
print("loaded:", type(m).__name__)
p = Path("/tmp/yolo_test.jpg")
if p.is_file():
    damages, note = detect_damages_yolo([p])
    print("note:", note)
    print("damages:", damages)
else:
    print("missing", p)
