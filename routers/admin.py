from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel
from models import Users, Roles

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    role_id: int
    active: bool

@router.get("/roles", status_code=status.HTTP_200_OK)
async def return_all_roles(db: db_dependency):
    return db.query(Roles).all()

@router.get("/users", status_code=status.HTTP_200_OK)
async def return_all_users(db: db_dependency):
    return db.query(Users).all()