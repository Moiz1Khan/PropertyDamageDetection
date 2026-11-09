import uuid

from sqlalchemy.orm import Session

from .auth import hash_password
from .models import Property, User
from .services.analysis import run_full_analysis

DEMO_USERS = [
    {
        "id": "u1",
        "name": "Alex Morgan",
        "email": "demo@offmarketstream.com",
        "password": "demo123",
        "role": "investor",
    },
    {
        "id": "u2",
        "name": "Sarah Chen",
        "email": "agent@offmarketstream.com",
        "password": "agent123",
        "role": "agent",
    },
    {
        "id": "u4",
        "name": "Admin User",
        "email": "admin@offmarketstream.com",
        "password": "admin123",
        "role": "admin",
    },
]

SEED_PROPERTIES = [
    {
        "id": "p1",
        "owner_id": "u1",
        "address": "1842 Oakwood Drive",
        "city": "Austin",
        "state": "TX",
        "zip_code": "78704",
        "property_type": "Single Family",
        "list_price": 285000,
        "sqft": 1840,
        "beds": 3,
        "baths": 2,
        "year_built": 1998,
        "status": "complete",
    },
    {
        "id": "p2",
        "owner_id": "u1",
        "address": "729 Riverside Blvd",
        "city": "Austin",
        "state": "TX",
        "zip_code": "78701",
        "property_type": "Duplex",
        "list_price": 410000,
        "sqft": 2200,
        "beds": 4,
        "baths": 3,
        "year_built": 2005,
        "status": "complete",
    },
    {
        "id": "p3",
        "owner_id": "u1",
        "address": "3301 Highland Park",
        "city": "Dallas",
        "state": "TX",
        "zip_code": "75205",
        "property_type": "Single Family",
        "list_price": 195000,
        "sqft": 1420,
        "beds": 3,
        "baths": 1,
        "year_built": 1978,
        "status": "complete",
    },
    {
        "id": "p4",
        "owner_id": "u1",
        "address": "512 Commerce St",
        "city": "Houston",
        "state": "TX",
        "zip_code": "77002",
        "property_type": "Townhouse",
        "list_price": 320000,
        "sqft": 1680,
        "beds": 3,
        "baths": 2.5,
        "year_built": 2012,
        "status": "complete",
    },
]


def seed_if_empty(db: Session) -> None:
    if db.query(User).count() > 0:
        return

    for u in DEMO_USERS:
        db.add(
            User(
                id=u["id"],
                name=u["name"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
                status="Active",
            )
        )
    db.flush()

    for raw in SEED_PROPERTIES:
        result = run_full_analysis(
            address=raw["address"],
            city=raw["city"],
            state=raw["state"],
            list_price=raw["list_price"],
            sqft=raw["sqft"],
            beds=raw["beds"],
            baths=raw["baths"],
        )
        db.add(
            Property(
                id=raw["id"],
                owner_id=raw["owner_id"],
                address=raw["address"],
                city=raw["city"],
                state=raw["state"],
                zip_code=raw["zip_code"],
                property_type=raw["property_type"],
                list_price=raw["list_price"],
                sqft=raw["sqft"],
                beds=raw["beds"],
                baths=raw["baths"],
                year_built=raw["year_built"],
                status="complete",
                image_url=result["image_url"],
                rehab_cost=result["rehab_cost"],
                arv=result["arv"],
                monthly_rent=result["monthly_rent"],
                profit=result["profit"],
                roi=result["roi"],
                max_offer=result["max_offer"],
                strategy=result["strategy"],
                rank_score=result["rank_score"],
                damages=result["damages"],
                comps=result["comps"],
                neighborhood=result["neighborhood"],
                analysis_log=result["analysis_log"],
            )
        )
    db.commit()
