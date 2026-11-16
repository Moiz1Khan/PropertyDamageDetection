import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


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
    score: float | None = None  # YOLO confidence when the detector found it
    room: str
    category: str = "other"
    source: str = "legacy"  # ai | yolo | ai+yolo | legacy (old simulated data)
    imageIndex: int | None = None
    areaSqft: float | None = None
    description: str = ""
    box: list[float] | None = None
    yoloBox: list[float] | None = None


class CompOut(BaseModel):
    id: str
    address: str
    salePrice: float
    distance: float
    sqft: int
    soldDate: str


class NeighborhoodOut(BaseModel):
    medianPrice: float | None = None
    medianRent: float | None = None
    crimeIndex: float | None = None
    schoolRating: float | None = None
    appreciation: float | None = None


class PropertyCreate(BaseModel):
    address: str = Field(min_length=3, max_length=255)
    city: str = Field(min_length=2, max_length=120)
    state: str = Field(default="TX", min_length=2, max_length=8)
    zip_code: str = Field(default="", max_length=16)
    property_type: str = "Single Family"
    list_price: float = Field(gt=1000, le=100_000_000)
    sqft: int = Field(ge=100, le=100_000)
    beds: int = Field(ge=0, le=50)
    baths: float = Field(ge=0, le=50)
    year_built: int | None = Field(default=None, ge=1700, le=2100)
    lot_size: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=5000)
    image_url: str | None = None
    gallery_image_urls: list[str] | None = Field(default=None, max_length=20)
    # Room tag per gallery image (same order); "" = let the AI decide
    image_rooms: list[str] | None = Field(default=None, max_length=20)
    run_analysis: bool = True

    @field_validator("address", "city", "state", "zip_code")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()


class PhotoRoomsIn(BaseModel):
    image_rooms: list[str] = Field(max_length=20)


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
    galleryImages: list[str] = []
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
    imageRooms: list[str] = []
    photoAnalyses: list[dict[str, Any]] = []
    rehabItems: list[dict[str, Any]] = []
    valuation: dict[str, Any] = {}
    warnings: list[str] = []
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


_LEGACY_LOG = [
    (re.compile(r" using .*?Gemini vision \(\d+ photo\(s\)\)"), " using YOLOv8 damage model"),
    (re.compile(r'AI rejected a YOLO "([^"]+)" box'), r'filtered out a false "\1" detection'),
    (re.compile(r"AI vision[^\n]*"), "Detailed scan unavailable for this photo — base detection only"),
]


def _public_log_line(line: str) -> str:
    for pattern, repl in _LEGACY_LOG:
        line = pattern.sub(repl, line)
    return line


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
        galleryImages=list(p.gallery_images or []),
        rehabCost=p.rehab_cost,
        arv=p.arv,
        monthlyRent=p.monthly_rent,
        profit=p.profit,
        roi=p.roi,
        maxOffer=p.max_offer,
        strategy=p.strategy,
        rankScore=p.rank_score,
        damages=[DamageOut(**{k: v for k, v in d.items() if k in DamageOut.model_fields}) for d in (p.damages or [])],
        comps=[CompOut(**c) for c in (p.comps or [])],
        neighborhood=NeighborhoodOut(**{k: nb.get(k) for k in NeighborhoodOut.model_fields}),
        analysisLog=[_public_log_line(line) for line in (p.analysis_log or [])],
        imageRooms=list(p.image_rooms or []),
        photoAnalyses=list(p.photo_analyses or []),
        rehabItems=list(p.rehab_items or []),
        valuation=dict(p.valuation or {}),
        warnings=list(p.warnings or []),
        createdAt=p.created_at.strftime("%Y-%m-%d") if isinstance(p.created_at, datetime) else str(p.created_at),
        yearBuilt=p.year_built,
        notes=p.notes,
    )
