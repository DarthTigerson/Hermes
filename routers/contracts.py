from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Contracts

router = APIRouter(
    prefix="/contracts",
    tags=["contracts"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class Contract(BaseModel):
    id: int
    name: str
    description: str

@router.get("/", status_code=status.HTTP_200_OK)
async def return_all_contracts(db: db_dependency):
    return db.query(Contracts).all()

@router.get("/{contract_id}", status_code=status.HTTP_200_OK)
async def return_contract_by_id(contract_id: int, db: db_dependency):
    contract_data = db.query(Contracts).filter(Contracts.id == contract_id).first()

    if contract_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract_data

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_contract(contract: Contract, db: db_dependency):
    new_contract = Contracts(**contract.model_dump())

    new_contract.name = contract.name
    new_contract.description = contract.description
    db.add(new_contract)
    db.commit()

@router.put("/{contract_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_contract_by_id(contract_id: int, contract: Contract, db: db_dependency):
    contract_to_update = db.query(Contracts).filter(Contracts.id == contract_id).first()

    if contract_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    
    contract_to_update.name = contract.name
    contract_to_update.description = contract.description
    db.add(contract_to_update)
    db.commit()

@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract_by_id(contract_id: int, db: db_dependency):
    contract_to_delete = db.query(Contracts).filter(Contracts.id == contract_id).first()

    if contract_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    
    db.delete(contract_to_delete)
    db.commit()