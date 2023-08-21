from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
import models

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="",
    tags=["home"],
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
    total_employees = db.query(models.Employees).filter(models.Employees.employment_status_id == 0).count()
    return templates.TemplateResponse("home.html", {"request": request, "total_employees": total_employees})