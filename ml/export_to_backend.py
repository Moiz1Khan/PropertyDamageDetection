"""Copy best.pt from latest training run into backend/models for FastAPI inference."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parent
REPO = ML_ROOT.parent
DEFAULT_RUN = ML_ROOT / "runs" / "damage_yolov8n" / "weights" / "best.pt"
BACKEND_MODEL_DIR = REPO / "backend" / "models" / "damage_yolov8n"
BACKEND_WEIGHTS = BACKEND_MODEL_DIR / "best.pt"


def main() -> int:
    src = DEFAULT_RUN
    if len(sys.argv) > 1:
        src = Path(sys.argv[1])
    if not src.is_file():
        print(f"Missing weights: {src}\nTrain first: python train_yolov8.py", file=sys.stderr)
        return 1
    BACKEND_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, BACKEND_WEIGHTS)
    print(f"Copied → {BACKEND_WEIGHTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
