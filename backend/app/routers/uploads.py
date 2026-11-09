import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..auth import get_current_user
from ..models import User

router = APIRouter(tags=["uploads"])

UPLOAD_ROOT = Path(__file__).resolve().parent.parent.parent / "uploads"
ALLOWED = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 10 * 1024 * 1024
MAX_FILES = 20


@router.post("/uploads/property-images")
async def upload_property_images(
    user: Annotated[User, Depends(get_current_user)],
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(400, "No files provided")
    if len(files) > MAX_FILES:
        raise HTTPException(400, f"Maximum {MAX_FILES} images allowed")

    batch_id = uuid.uuid4().hex[:12]
    dest = UPLOAD_ROOT / "property" / batch_id
    dest.mkdir(parents=True, exist_ok=True)

    urls: list[dict[str, str]] = []
    for uf in files:
        ext = Path(uf.filename or "image.jpg").suffix.lower()
        if ext not in ALLOWED:
            raise HTTPException(400, f"Unsupported file type: {ext}")
        data = await uf.read()
        if len(data) > MAX_BYTES:
            raise HTTPException(400, f"{uf.filename} exceeds 10MB limit")
        safe_name = f"{uuid.uuid4().hex[:8]}{ext}"
        path = dest / safe_name
        path.write_bytes(data)
        urls.append(
            {
                "url": f"/api/uploads/property/{batch_id}/{safe_name}",
                "name": uf.filename or safe_name,
            }
        )

    return {"batchId": batch_id, "images": urls}
