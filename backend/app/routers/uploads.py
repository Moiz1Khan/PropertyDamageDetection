import io
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from ..auth import get_current_user
from ..config import UPLOAD_ROOT
from ..models import User

router = APIRouter(tags=["uploads"])

ALLOWED = {".jpg", ".jpeg", ".png", ".webp"}
FORMAT_EXT = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
MAX_BYTES = 10 * 1024 * 1024
MAX_FILES = 20


def user_upload_prefix(user_id: str) -> str:
    return f"/api/uploads/property/{user_id}/"


def _check_image(name: str, data: bytes) -> str:
    """Return the file extension matching the real image format, or raise 400."""
    try:
        with Image.open(io.BytesIO(data)) as img:
            fmt = img.format
            img.verify()
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        raise HTTPException(400, f"{name} is not a valid image file.")
    ext = FORMAT_EXT.get(fmt or "")
    if not ext:
        raise HTTPException(400, f"{name}: unsupported image format {fmt}. Use JPG, PNG or WebP.")
    return ext


@router.post("/uploads/property-images")
async def upload_property_images(
    user: Annotated[User, Depends(get_current_user)],
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(400, "No files provided")
    if len(files) > MAX_FILES:
        raise HTTPException(400, f"Maximum {MAX_FILES} images allowed")

    # Validate every file before writing anything, so a bad file never leaves a half-saved batch.
    checked: list[tuple[str, bytes, str]] = []
    for uf in files:
        name = uf.filename or "image"
        if Path(name).suffix.lower() not in ALLOWED:
            raise HTTPException(400, f"Unsupported file type: {name}")
        data = await uf.read()
        if len(data) > MAX_BYTES:
            raise HTTPException(400, f"{name} exceeds 10MB limit")
        checked.append((name, data, _check_image(name, data)))

    batch_id = uuid.uuid4().hex[:12]
    dest = UPLOAD_ROOT / "property" / user.id / batch_id
    dest.mkdir(parents=True, exist_ok=True)

    images: list[dict[str, str]] = []
    for name, data, ext in checked:
        safe_name = f"{uuid.uuid4().hex[:12]}{ext}"
        (dest / safe_name).write_bytes(data)
        images.append({"url": f"{user_upload_prefix(user.id)}{batch_id}/{safe_name}", "name": name})

    return {"batchId": batch_id, "images": images}
