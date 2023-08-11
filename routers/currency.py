from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Currency

router = APIRouter(
    prefix="/currency",
    tags=["currency"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class Currency_Class(BaseModel):
    id: int
    name: str
    symbol: str

@router.get("/", status_code=status.HTTP_200_OK)
async def return_all_currency(db: db_dependency):
    return db.query(Currency).all()

@router.get("/{currency_id}", status_code=status.HTTP_200_OK)
async def return_currency_by_id(currency_id: int, db: db_dependency):
    currency_data = db.query(Currency).filter(Currency.id == currency_id).first()

    if currency_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found")
    return currency_data

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_currency(currency: Currency_Class, db: db_dependency):
    new_currency = Currency(**currency.model_dump())

    new_currency.name = currency.name
    new_currency.symbol = currency.symbol
    db.add(new_currency)
    db.commit()

@router.put("/{currency_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_currency_by_id(currency_id: int, currency: Currency_Class, db: db_dependency):
    currency_to_update = db.query(Currency).filter(Currency.id == currency_id).first()

    if currency_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found")
    
    currency_to_update.name = currency.name
    currency_to_update.symbol = currency.symbol
    db.add(currency_to_update)
    db.commit()

@router.delete("/{currency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_currency_by_id(currency_id: int, db: db_dependency):
    currency_to_delete = db.query(Currency).filter(Currency.id == currency_id).first()

    if currency_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found")
    
    db.delete(currency_to_delete)
    db.commit()