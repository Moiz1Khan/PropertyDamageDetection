# Train YOLOv8n damage model (1–2 hours)

## Pick datasets

See **[datasets.md](./datasets.md)**. Default: **building-damage-insurance** (~5.2k images, crack/stain/mold/damp).

## Prerequisites

- NVIDIA GPU recommended (you have CUDA locally).
- Free [Roboflow API key](https://app.roboflow.com/settings/api).

## Steps

```powershell
cd "c:\Users\Moiz Khan\realEstate\ml"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.ml.example .env.ml
# Edit .env.ml → ROBOFLOW_API_KEY=...

python download_dataset.py
python train_yolov8.py --epochs 35 --batch 16
python export_to_backend.py
```

Install CV deps on API (once):

```powershell
cd ..\backend
pip install -r requirements-cv.txt
```

Restart backend. Upload property photos → analysis uses **real boxes**, not address-based bathroom labels.

## Faster train (smaller data)

```powershell
$env:DATASET_PRESET="av_water"
python download_dataset.py
python train_yolov8.py --epochs 25
```

## Colab

If local disk/GPU is busy, open `colab_train.ipynb` in Google Colab (T4), paste API key, run all, download `best.pt`, run `export_to_backend.py` with path to downloaded file.
