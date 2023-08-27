from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
import models, datetime

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
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    employments = db.query(models.Employment).order_by(models.Employment.name).all()
    total_employees = db.query(models.Employees).filter(models.Employees.employment_status_id == 0).count()
    total_offboarded_employees = db.query(models.Employees).filter(models.Employees.employment_status_id == 1).count()
    todays_offboardings = db.query(models.Employees).filter(models.Employees.employment_status_id == 0).filter(models.Employees.end_date == datetime.date.today()).all()
    missed_offboardings = db.query(models.Employees).filter(models.Employees.employment_status_id == 0).filter(models.Employees.end_date < datetime.date.today()).all()
    upcoming_offboardings = db.query(models.Employees).filter(models.Employees.employment_status_id == 0).filter(models.Employees.end_date > datetime.date.today()).all()

    return templates.TemplateResponse("home.html", {"request": request, "total_employees": total_employees, "total_offboarded_employees": total_offboarded_employees, "todays_offboardings": todays_offboardings, "departments": departments, "sites": sites, "employments": employments, "missed_offboardings": missed_offboardings})