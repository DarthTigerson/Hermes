from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
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

class Role(BaseModel):
    role_name: str
    role_description: str

@router.get("/roles", status_code=status.HTTP_200_OK)
async def return_all_roles(db: db_dependency):
    return db.query(Roles).all()

@router.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_role(role: Role, db: db_dependency):
    role_data = Roles(**role.model_dump())

    db.add(role_data)
    db.commit()

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_by_id(role_id: int, db: db_dependency):
    role_to_delete = db.query(Roles).filter(Roles.id == role_id).first()

    if role_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    db.delete(role_to_delete)
    db.commit()

@router.get("/users", status_code=status.HTTP_200_OK)
async def return_all_users(db: db_dependency):
    return db.query(Users).all()

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: User, db: db_dependency):
    new_user = Users(**user.model_dump())

    db.add(new_user)
    db.commit()

@router.put("/users/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_user_by_id(user_id: int, user: User, db: db_dependency):
    user_to_update = db.query(Users).filter(Users.id == user_id).first()

    if user_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_to_update = Users(**user.model_dump())
    db.add(user_to_update)
    db.commit()

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(user_id: int, db: db_dependency):
    user_to_delete = db.query(Users).filter(Users.id == user_id).first()

    if user_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user_to_delete)
    db.commit()