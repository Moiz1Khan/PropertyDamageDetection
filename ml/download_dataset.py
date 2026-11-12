"""
Download YOLOv8-formatted damage dataset from Roboflow Universe.

Requires ROBOFLOW_API_KEY in ml/.env.ml or environment.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ML_ROOT = Path(__file__).resolve().parent
load_dotenv(ML_ROOT / ".env.ml")

PRESETS = {
    "primary": {
        "workspace": "tennis-jbaz6",
        "project": "building-damage-insurance",
        "version": 1,
        "label": "building-damage-insurance (~5.2k images)",
    },
    "av_water": {
        "workspace": "assuralabs",
        "project": "av-water-damage",
        "version": 1,
        "label": "AV-Water Damage (~1.9k images)",
    },
    "damaged_building": {
        "workspace": "damaged-building-detection",
        "project": "damaged-building-detection-zenbx",
        "version": 2,
        "label": "Damaged Building Detection v2 (~1.3k images)",
    },
}


def main() -> int:
    api_key = os.environ.get("ROBOFLOW_API_KEY", "").strip()
    if not api_key:
        print(
            "Missing ROBOFLOW_API_KEY.\n"
            "1) Create free key: https://app.roboflow.com/settings/api\n"
            "2) Copy ml/.env.ml.example → ml/.env.ml and paste the key.\n"
            "See ml/datasets.md for dataset links.",
            file=sys.stderr,
        )
        return 1

    preset_name = os.environ.get("DATASET_PRESET", "primary").strip().lower()
    preset = PRESETS.get(preset_name)
    if not preset:
        print(f"Unknown DATASET_PRESET={preset_name!r}. Choose: {', '.join(PRESETS)}", file=sys.stderr)
        return 1

    try:
        from roboflow import Roboflow
    except ImportError:
        print("Install deps: pip install -r ml/requirements.txt", file=sys.stderr)
        return 1

    out_dir = ML_ROOT / "data" / preset["project"]

    print(f"Downloading {preset['label']} …")
    rf = Roboflow(api_key=api_key)
    project = rf.workspace(preset["workspace"]).project(preset["project"])
    dataset = project.version(preset["version"]).download("yolov8", location=str(out_dir))

    yaml_path = Path(dataset.location) / "data.yaml"
    if not yaml_path.is_file():
        print(f"ERROR: download finished but {yaml_path} is missing.", file=sys.stderr)
        return 1
    print(f"Done. Dataset root: {dataset.location}")
    print(f"data.yaml: {yaml_path}")
    (ML_ROOT / "latest_dataset.txt").write_text(str(Path(dataset.location).resolve()), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
