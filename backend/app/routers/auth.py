import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import LoginIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    return TokenOut(
        access_token=token,
        user=UserOut(id=user.id, name=user.name, email=user.email, role=user.role, status=user.status),
    )


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, db: Annotated[Session, Depends(get_db)]):
    email = body.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        name=body.name,
        email=email,
        hashed_password=hash_password(body.password),
        role=body.role,
        status="Active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return TokenOut(
        access_token=token,
        user=UserOut(id=user.id, name=user.name, email=user.email, role=user.role, status=user.status),
    )


@router.get("/me", response_model=UserOut)
def me(user: Annotated[User, Depends(get_current_user)]):
    return UserOut(id=user.id, name=user.name, email=user.email, role=user.role, status=user.status)
