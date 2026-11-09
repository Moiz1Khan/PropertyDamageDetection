from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="investor")
    status: Mapped[str] = mapped_column(String(32), default="Active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    properties: Mapped[list["Property"]] = relationship(back_populates="owner")


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    address: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(8))
    zip_code: Mapped[str] = mapped_column(String(16), default="")
    property_type: Mapped[str] = mapped_column(String(64), default="Single Family")
    list_price: Mapped[float] = mapped_column(Float)
    sqft: Mapped[int] = mapped_column(Integer)
    beds: Mapped[int] = mapped_column(Integer)
    baths: Mapped[float] = mapped_column(Float)
    year_built: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lot_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    image_url: Mapped[str] = mapped_column(String(512), default="")

    # Analysis outputs
    rehab_cost: Mapped[float] = mapped_column(Float, default=0)
    arv: Mapped[float] = mapped_column(Float, default=0)
    monthly_rent: Mapped[float] = mapped_column(Float, default=0)
    profit: Mapped[float] = mapped_column(Float, default=0)
    roi: Mapped[float] = mapped_column(Float, default=0)
    max_offer: Mapped[float] = mapped_column(Float, default=0)
    strategy: Mapped[str] = mapped_column(String(32), default="flip")
    rank_score: Mapped[float] = mapped_column(Float, default=0)
    damages: Mapped[dict | list] = mapped_column(JSON, default=list)
    comps: Mapped[dict | list] = mapped_column(JSON, default=list)
    neighborhood: Mapped[dict] = mapped_column(JSON, default=dict)
    analysis_log: Mapped[list] = mapped_column(JSON, default=list)
    gallery_images: Mapped[list] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner: Mapped["User"] = relationship(back_populates="properties")
