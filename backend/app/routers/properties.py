import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Property, User
from ..schemas import AnalysisResult, DashboardStats, PropertyCreate, PropertyOut, property_to_out
from ..services.analysis import run_full_analysis
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
    db.delete(prop)
    db.commit()


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


@router.post("/properties", response_model=AnalysisResult)
def create_property(
    body: PropertyCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    prop_id = str(uuid.uuid4())
    result = None
    status = "draft"
    if body.run_analysis:
        result = run_full_analysis(
            address=body.address,
            city=body.city,
            state=body.state,
            list_price=body.list_price,
            sqft=body.sqft,
            beds=body.beds,
            baths=body.baths,
            gallery_urls=body.gallery_image_urls,
        )
        status = "complete"

    prop = Property(
        id=prop_id,
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
        status=status,
        image_url=body.image_url
        or ((body.gallery_image_urls or [None])[0])
        or (result["image_url"] if result else ""),
        gallery_images=body.gallery_image_urls or [],
        rehab_cost=result["rehab_cost"] if result else 0,
        arv=result["arv"] if result else 0,
        monthly_rent=result["monthly_rent"] if result else 0,
        profit=result["profit"] if result else 0,
        roi=result["roi"] if result else 0,
        max_offer=result["max_offer"] if result else 0,
        strategy=result["strategy"] if result else "flip",
        rank_score=result["rank_score"] if result else 0,
        damages=result["damages"] if result else [],
        comps=result["comps"] if result else [],
        neighborhood=result["neighborhood"] if result else {},
        analysis_log=result["analysis_log"] if result else [],
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return AnalysisResult(
        property=property_to_out(prop),
        stages=result["stages"] if result else ["Property saved as draft"],
    )


@router.post("/properties/{property_id}/analyze", response_model=AnalysisResult)
def reanalyze(
    property_id: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    if user.role != "admin" and prop.owner_id != user.id:
        raise HTTPException(403, "Not allowed")

    prop.status = "analyzing"
    db.commit()

    result = run_full_analysis(
        address=prop.address,
        city=prop.city,
        state=prop.state,
        list_price=prop.list_price,
        sqft=prop.sqft,
        beds=prop.beds,
        baths=prop.baths,
        gallery_urls=list(prop.gallery_images or []),
    )
    prop.status = "complete"
    prop.image_url = prop.image_url or result["image_url"]
    prop.rehab_cost = result["rehab_cost"]
    prop.arv = result["arv"]
    prop.monthly_rent = result["monthly_rent"]
    prop.profit = result["profit"]
    prop.roi = result["roi"]
    prop.max_offer = result["max_offer"]
    prop.strategy = result["strategy"]
    prop.rank_score = result["rank_score"]
    prop.damages = result["damages"]
    prop.comps = result["comps"]
    prop.neighborhood = result["neighborhood"]
    prop.analysis_log = result["analysis_log"]
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
