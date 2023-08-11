from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Country

router = APIRouter(
    prefix="/country",
    tags=["country"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class Country_Class(BaseModel):
    id: int
    name: str
    short_name: str

@router.get("/", status_code=status.HTTP_200_OK)
async def return_all_country(db: db_dependency):
    return db.query(Country).all()

@router.get("/{country_id}", status_code=status.HTTP_200_OK)
async def return_country_by_id(country_id: int, db: db_dependency):
    country_data = db.query(Country).filter(Country.id == country_id).first()

    if country_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    return country_data

@router.get("/{country_name}", status_code=status.HTTP_200_OK)
async def return_country_by_name(country_name: str, db: db_dependency):
    country_data = db.query(Country).filter(Country.name == country_name).first()

    if country_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    return country_data

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_country(country: Country_Class, db: db_dependency):
    new_country = Country(**country.model_dump())

    new_country.name = country.name
    new_country.short_name = country.short_name
    db.add(new_country)
    db.commit()

@router.put("/{country_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_country_by_id(country_id: int, country: Country_Class, db: db_dependency):
    country_to_update = db.query(Country).filter(Country.id == country_id).first()

    if country_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    
    country_to_update.name = country.name
    country_to_update.short_name = country.short_name
    db.add(country_to_update)
    db.commit()

@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country_by_id(country_id: int, db: db_dependency):
    country_to_delete = db.query(Country).filter(Country.id == country_id).first()

    if country_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    
    db.delete(country_to_delete)
    db.commit()