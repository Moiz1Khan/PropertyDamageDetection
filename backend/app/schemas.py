from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    status: str = "Active"

    class Config:
        from_attributes = True


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: Literal["investor", "agent", "lender"] = "investor"


class DamageOut(BaseModel):
    type: str
    severity: Literal["low", "medium", "high"]
    score: float
    room: str


class CompOut(BaseModel):
    id: str
    address: str
    salePrice: float
    distance: float
    sqft: int
    soldDate: str


class NeighborhoodOut(BaseModel):
    medianPrice: float
    medianRent: float
    crimeIndex: float
    schoolRating: float
    appreciation: float


class PropertyCreate(BaseModel):
    address: str
    city: str
    state: str = "TX"
    zip_code: str = ""
    property_type: str = "Single Family"
    list_price: float
    sqft: int
    beds: int
    baths: float
    year_built: int | None = None
    lot_size: int | None = None
    notes: str | None = None
    image_url: str | None = None
    run_analysis: bool = True


class PropertyOut(BaseModel):
    id: str
    address: str
    city: str
    state: str
    zip_code: str = ""
    type: str
    listPrice: float
    sqft: int
    beds: int
    baths: float
    status: str
    imageUrl: str
    rehabCost: float
    arv: float
    monthlyRent: float
    profit: float
    roi: float
    maxOffer: float
    strategy: str
    rankScore: float
    damages: list[DamageOut]
    comps: list[CompOut]
    neighborhood: NeighborhoodOut
    analysisLog: list[str] = []
    createdAt: str
    yearBuilt: int | None = None
    notes: str | None = None


class DashboardStats(BaseModel):
    totalProperties: int
    avgRoi: float
    totalProfit: float
    activeAnalyses: int


class AnalysisResult(BaseModel):
    property: PropertyOut
    stages: list[str]


def property_to_out(p) -> PropertyOut:
    nb = p.neighborhood or {}
    return PropertyOut(
        id=p.id,
        address=p.address,
        city=p.city,
        state=p.state,
        zip_code=p.zip_code or "",
        type=p.property_type,
        listPrice=p.list_price,
        sqft=p.sqft,
        beds=p.beds,
        baths=p.baths,
        status=p.status,
        imageUrl=p.image_url or "",
        rehabCost=p.rehab_cost,
        arv=p.arv,
        monthlyRent=p.monthly_rent,
        profit=p.profit,
        roi=p.roi,
        maxOffer=p.max_offer,
        strategy=p.strategy,
        rankScore=p.rank_score,
        damages=[DamageOut(**d) for d in (p.damages or [])],
        comps=[CompOut(**c) for c in (p.comps or [])],
        neighborhood=NeighborhoodOut(
            medianPrice=nb.get("medianPrice", 0),
            medianRent=nb.get("medianRent", 0),
            crimeIndex=nb.get("crimeIndex", 0),
            schoolRating=nb.get("schoolRating", 0),
            appreciation=nb.get("appreciation", 0),
        ),
        analysisLog=p.analysis_log or [],
        createdAt=p.created_at.strftime("%Y-%m-%d") if isinstance(p.created_at, datetime) else str(p.created_at),
        yearBuilt=p.year_built,
        notes=p.notes,
    )
