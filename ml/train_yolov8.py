"""
Fine-tune YOLOv8n on downloaded Roboflow data (~1–2h on consumer GPU).

Reads dataset path from ml/latest_dataset.txt (written by download_dataset.py)
or pass --data path/to/data.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parent


def _cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except ImportError:
        return False


def resolve_data_yaml(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise FileNotFoundError(p)
        return p
    stamp = ML_ROOT / "latest_dataset.txt"
    if not stamp.is_file():
        raise FileNotFoundError(
            "No dataset registered. Run: python download_dataset.py\n"
            "Or pass --data path/to/data.yaml"
        )
    root = Path(stamp.read_text(encoding="utf-8").strip())
    yaml_path = root / "data.yaml"
    if not yaml_path.is_file():
        yaml_path = root / "train" / "data.yaml"
    if not yaml_path.is_file():
        raise FileNotFoundError(f"data.yaml not found under {root}")
    return yaml_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=None, help="Path to data.yaml")
    parser.add_argument("--epochs", type=int, default=35, help="35–50 for primary dataset on GPU")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default="", help="0 for CUDA GPU, cpu for CPU")
    parser.add_argument("--name", default="damage_yolov8n")
    args = parser.parse_args()

    try:
        from ultralytics import YOLO
    except ImportError:
        print("pip install -r ml/requirements.txt", file=sys.stderr)
        return 1

    data_yaml = resolve_data_yaml(args.data)
    device = args.device
    if not device:
        device = "0" if _cuda_available() else "cpu"
    if device == "cpu":
        print("WARNING: Training on CPU can take many hours. Use GPU or Colab.", file=sys.stderr)

    runs = ML_ROOT / "runs"
    runs.mkdir(parents=True, exist_ok=True)

    model = YOLO("yolov8n.pt")
    model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        project=str(runs),
        name=args.name,
        patience=12,
        plots=True,
        exist_ok=True,
        workers=0,  # Windows: avoid dataloader + checkpoint races
        save=True,
    )
    best = runs / args.name / "weights" / "best.pt"
    print(f"Training complete. best.pt → {best}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
