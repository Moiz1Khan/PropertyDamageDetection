"""Hit production API: login, upload damage photo, run analysis — expect YOLOv8n in log."""
import json
import sys
from pathlib import Path

import httpx

BASE = "http://3.14.42.168/api"
IMAGE = Path(__file__).resolve().parent.parent / "ml/data/building-damage-insurance-v2/valid/images"
if not IMAGE.parent.is_dir():
    print("No local test images; skip upload test")
    sys.exit(1)
imgs = sorted(IMAGE.glob("*.*"))
if not imgs:
    sys.exit(1)
img = imgs[0]

with httpx.Client(base_url=BASE, timeout=120.0) as c:
    r = c.post("/auth/login", json={"email": "demo@offmarketstream.com", "password": "demo123"})
    r.raise_for_status()
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with img.open("rb") as f:
        up = c.post(
            "/uploads/property-images",
            headers=headers,
            files=[("files", (img.name, f, "image/jpeg"))],
        )
    up.raise_for_status()
    urls = [u["url"] for u in up.json().get("images", [])]
    if not urls:
        print("upload failed:", up.text)
        sys.exit(1)

    body = {
        "address": "123 YOLO Test St",
        "city": "Austin",
        "state": "TX",
        "zip_code": "78701",
        "property_type": "Single Family",
        "list_price": 250000,
        "sqft": 1600,
        "beds": 3,
        "baths": 2,
        "run_analysis": True,
        "gallery_image_urls": urls,
    }
    r = c.post("/properties", headers=headers, json=body)
    r.raise_for_status()
    data = r.json()
    print("response keys:", sorted(data.keys()))
    prop = data.get("property") or {}
    log = prop.get("analysisLog") or data.get("analysis_log") or []
    stages = data.get("stages") or []
    cv_lines = [x for x in log if "CV" in x or "YOLO" in x or "yolo" in x.lower()]
    print("stages:", stages)
    print("CV-related log lines:")
    for line in cv_lines:
        print(" ", line)
    damages = prop.get("damages") or []
    print("damages:", json.dumps(damages[:5], indent=2))
    if not any("YOLOv8n" in str(x) for x in log):
        print("FAIL: no YOLOv8n in analysis_log")
        sys.exit(1)
    print("OK: production YOLO path verified")
