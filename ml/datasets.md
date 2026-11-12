# Damage-detection datasets (OffmarketStream / YOLOv8n)

Use **one** primary dataset for the first training run (~1–2 hours on a GPU). Add others later only if you need more classes (e.g. roof/exterior).

## Primary (recommended for tonight)

| Dataset | Images | Classes | Format | Link |
|--------|--------|---------|--------|------|
| **building-damage-insurance** | ~5.2k | crack, stain, mold, damp, stairstep_crack (+ numeric aliases in export) | YOLOv8 | [Roboflow Universe](https://universe.roboflow.com/tennis-jbaz6/building-damage-insurance) |

**Why this one:** Matches your rehab taxonomy (crack, water stain, mold, dampness) in a single YOLO export. Size is enough for a solid **YOLOv8n** fine-tune in one GPU session.

**License / ethics:** Universe datasets are third-party; cite the dataset URL in your FYP report. Do not redistribute the zip in your repo.

## Fast backup (smaller, ~45–60 min train)

| Dataset | Images | Classes | Link |
|--------|--------|---------|------|
| **AV-Water Damage** | ~1.9k | crack, stain, mold, damp, dampness | [Roboflow](https://universe.roboflow.com/assuralabs/av-water-damage) |

## Supplement later (not required for v1)

| Dataset | Images | Focus | Link |
|--------|--------|--------|------|
| Damaged Building Detection v2 | ~1.3k | General building damage boxes | [Roboflow](https://universe.roboflow.com/damaged-building-detection/damaged-building-detection-zenbx/dataset/2) |
| Building defect on walls | ~472 | crack, mold, peeling_paint, water_seepage | [Roboflow](https://universe.roboflow.com/builddef2/building-defect-on-walls) |
| Building Crack detection (Akash Roy v3) | ~3.6k | crack-focused | [Roboflow](https://universe.roboflow.com/akash-roy-edivz/building-crack-detection-ys4zf/dataset/3) |

## Kaggle (needs `kaggle.json`; good if you prefer Kaggle over Roboflow)

| Dataset | Notes | Link |
|--------|--------|------|
| crack.v2i.yolov8 | Roboflow mirror, YOLOv8 ready | [Kaggle](https://www.kaggle.com/datasets/michaelhamonangan/crack-v2i-yolov8) |
| Wall Crack Hole Normal | crack, hole, normal | [Kaggle](https://www.kaggle.com/datasets/erkandevvecii/wall-crack-hole-normal-dataset) |

## What we do *not* use for property photos

- Road/pavement-only crack sets (high false positives on interior drywall).
- “Car body” / PCB domains from multi-domain Kaggle packs unless you filter folders.

## Roboflow API key (one-time, free)

1. Sign up at [roboflow.com](https://roboflow.com).
2. [Settings → API keys](https://app.roboflow.com/settings/api) → copy private key.
3. Save locally (never commit):

```powershell
cd c:\Users\Moiz Khan\realEstate\ml
copy .env.ml.example .env.ml
# Edit .env.ml and set ROBOFLOW_API_KEY=...
```

## Download + train (local GPU)

```powershell
cd c:\Users\Moiz Khan\realEstate\ml
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python download_dataset.py
python train_yolov8.py
python export_to_backend.py
```

Weights land in `backend/models/damage_yolov8n/best.pt` (gitignored).

## Google Colab (no local GPU)

Open `ml/colab_train.ipynb`, paste `ROBOFLOW_API_KEY`, run all cells, download `best.pt`, place in `backend/models/damage_yolov8n/best.pt`.
