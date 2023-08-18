from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Departments, Sites, Contracts, Employers, Employment, Country, Currency

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/manage",
    tags=["manage"],
)

templates = Jinja2Templates(directory='templates')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/")
async def test(request: Request, db: Session = Depends(get_db)):
    departments = db.query(Departments).all()
    sites = db.query(Sites).all()
    contracts = db.query(Contracts).all()
    employers = db.query(Employers).all()
    employment = db.query(Employment).all()
    country = db.query(Country).all()
    currency = db.query(Currency).all()

    return templates.TemplateResponse("manage.html", {"request": request, "departments": departments, "sites": sites, "contracts": contracts, "employers": employers, "employment": employment, "countries": country, "currencies": currency})