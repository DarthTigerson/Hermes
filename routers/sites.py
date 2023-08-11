from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Sites

router = APIRouter(
    prefix="/sites",
    tags=["sites"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class Site(BaseModel):
    id: int
    name: str
    description: str

@router.get("/", status_code=status.HTTP_200_OK)
async def return_all_sites(db: db_dependency):
    return db.query(Sites).all()

@router.get("/{site_id}", status_code=status.HTTP_200_OK)
async def return_site_by_id(site_id: int, db: db_dependency):
    site_data = db.query(Sites).filter(Sites.id == site_id).first()

    if site_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    return site_data

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_site(site: Site, db: db_dependency):
    new_site = Sites(**site.model_dump())

    new_site.id = site.id
    new_site.name = site.name
    new_site.description = site.description
    db.add(new_site)
    db.commit()

@router.put("/{site_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_site_by_id(site_id: int, site: Site, db: db_dependency):
    site_to_update = db.query(Sites).filter(Sites.id == site_id).first()

    if site_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    
    site_to_update.name = site.name
    site_to_update.description = site.description
    db.add(site_to_update)
    db.commit()

@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site_by_id(site_id: int, db: db_dependency):
    site_to_delete = db.query(Sites).filter(Sites.id == site_id).first()

    if site_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    
    db.delete(site_to_delete)
    db.commit()