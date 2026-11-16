import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Property, User
from ..schemas import AnalysisResult, DashboardStats, PhotoRoomsIn, PropertyCreate, PropertyOut, property_to_out
from ..services.analysis import pick_image, run_full_analysis
from ..services.image_cv import path_from_upload_url
from .uploads import user_upload_prefix
from ..services.pdf_report import build_property_pdf

router = APIRouter(tags=["properties"])


def _owner_filter(query, user: User):
    if user.role == "admin":
        return query
    return query.filter(Property.owner_id == user.id)


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    q = _owner_filter(db.query(Property), user)
    props = q.all()
    complete = [p for p in props if p.status == "complete"]
    avg_roi = sum(p.roi for p in complete) / len(complete) if complete else 0
    return DashboardStats(
        totalProperties=len(props),
        avgRoi=round(avg_roi, 1),
        totalProfit=round(sum(p.profit for p in complete), 0),
        activeAnalyses=len([p for p in props if p.status == "analyzing"]),
    )


@router.get("/properties", response_model=list[PropertyOut])
def list_properties(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    props = _owner_filter(db.query(Property), user).order_by(Property.created_at.desc()).all()
    return [property_to_out(p) for p in props]


@router.delete("/properties/{property_id}", status_code=204)
def delete_property(
    property_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    if user.role != "admin" and prop.owner_id != user.id:
        raise HTTPException(403, "Not allowed")
    photo_urls = list(prop.gallery_images or [])
    db.delete(prop)
    db.commit()
    still_used = {u for p in db.query(Property).all() for u in (p.gallery_images or [])}
    for url in photo_urls:
        path = path_from_upload_url(url)
        if path is not None and url not in still_used:
            path.unlink(missing_ok=True)


@router.get("/properties/{property_id}", response_model=PropertyOut)
def get_property(
    property_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    if user.role != "admin" and prop.owner_id != user.id:
        raise HTTPException(403, "Not allowed")
    return property_to_out(prop)


RESULT_FIELDS = [
    "rehab_cost", "arv", "monthly_rent", "profit", "roi", "max_offer", "strategy", "rank_score",
    "damages", "comps", "neighborhood", "analysis_log", "photo_analyses", "rehab_items", "valuation", "warnings",
]


def _clean_rooms(rooms: list[str] | None, n: int) -> list[str]:
    rooms = [(r or "").strip()[:40] for r in (rooms or [])][:n]
    return rooms + [""] * (n - len(rooms))


def _analyze(prop: Property, db: Session) -> dict:
    return run_full_analysis(
        address=prop.address,
        city=prop.city,
        state=prop.state,
        zip_code=prop.zip_code or "",
        property_type=prop.property_type,
        list_price=prop.list_price,
        sqft=prop.sqft,
        beds=prop.beds,
        baths=prop.baths,
        gallery_urls=list(prop.gallery_images or []),
        image_rooms=list(prop.image_rooms or []),
        db=db,
    )


def _apply(prop: Property, result: dict) -> None:
    for field in RESULT_FIELDS:
        setattr(prop, field, result[field])
    prop.status = "complete"
    if not prop.image_url:
        prop.image_url = (prop.gallery_images or [None])[0] or result["image_url"]


def _get_owned(property_id: str, user: User, db: Session) -> Property:
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    if user.role != "admin" and prop.owner_id != user.id:
        raise HTTPException(403, "Not allowed")
    return prop


@router.post("/properties", response_model=AnalysisResult)
def create_property(
    body: PropertyCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    gallery = [u for u in (body.gallery_image_urls or []) if u]
    prefix = user_upload_prefix(user.id)
    for url in gallery:
        if not url.startswith(prefix) or path_from_upload_url(url) is None:
            raise HTTPException(400, "Photos must be uploaded by you through the upload form.")

    prop = Property(
        id=str(uuid.uuid4()),
        owner_id=user.id,
        address=body.address,
        city=body.city,
        state=body.state,
        zip_code=body.zip_code,
        property_type=body.property_type,
        list_price=body.list_price,
        sqft=body.sqft,
        beds=body.beds,
        baths=body.baths,
        year_built=body.year_built,
        lot_size=body.lot_size,
        notes=body.notes,
        status="draft",
        image_url=gallery[0] if gallery else "",
        gallery_images=gallery,
        image_rooms=_clean_rooms(body.image_rooms, len(gallery)),
        damages=[], comps=[], neighborhood={}, analysis_log=[], photo_analyses=[], rehab_items=[],
        valuation={}, warnings=[],
    )
    stages = ["Property saved as draft"]
    if body.run_analysis:
        result = _analyze(prop, db)
        _apply(prop, result)
        stages = result["stages"]
    elif not prop.image_url:
        prop.image_url = pick_image(prop.address)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return AnalysisResult(property=property_to_out(prop), stages=stages)


@router.post("/properties/{property_id}/analyze", response_model=AnalysisResult)
def reanalyze(
    property_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    prop = _get_owned(property_id, user, db)
    result = _analyze(prop, db)
    _apply(prop, result)
    db.commit()
    db.refresh(prop)
    return AnalysisResult(property=property_to_out(prop), stages=result["stages"])


@router.put("/properties/{property_id}/photo-rooms", response_model=AnalysisResult)
def set_photo_rooms(
    property_id: str,
    body: PhotoRoomsIn,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Correct the room of each photo, then re-run the analysis (AI results are cached, so no extra quota)."""
    prop = _get_owned(property_id, user, db)
    prop.image_rooms = _clean_rooms(body.image_rooms, len(prop.gallery_images or []))
    result = _analyze(prop, db)
    _apply(prop, result)
    db.commit()
    db.refresh(prop)
    return AnalysisResult(property=property_to_out(prop), stages=result["stages"])


@router.get("/properties/{property_id}/report.pdf")
def download_report(
    property_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    if user.role != "admin" and prop.owner_id != user.id:
        raise HTTPException(403, "Not allowed")
    data = property_to_out(prop).model_dump()
    pdf = build_property_pdf(data)
    filename = f"OffmarketStream_{prop.address.replace(' ', '_')}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/rankings", response_model=list[PropertyOut])
def rankings(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    props = (
        _owner_filter(db.query(Property), user)
        .filter(Property.status == "complete")
        .order_by(Property.rank_score.desc())
        .all()
    )
    return [property_to_out(p) for p in props]
