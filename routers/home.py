from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from sqlalchemy import func
import models, datetime
from routers.admin import get_current_user
from starlette.responses import RedirectResponse

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

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    departments = db.query(models.Departments).order_by(models.Departments.name).all()
    sites = db.query(models.Sites).order_by(models.Sites.name).all()
    employments = db.query(models.Employment).order_by(models.Employment.name).all()
    total_employees = db.query(models.Employees).filter(models.Employees.employment_status_id == 0).count()
    total_offboarded_employees = db.query(models.Employees).filter(models.Employees.employment_status_id == 1).count()
    total_users = db.query(models.Users).count()
    todays_offboardings = db.query(models.Employees).filter(models.Employees.employment_status_id == 0).filter(models.Employees.end_date == datetime.date.today()).all()
    missed_offboardings = db.query(models.Employees).filter(models.Employees.employment_status_id == 0).filter(models.Employees.end_date < datetime.date.today()).all()
    todays_birthdays = db.query(models.Employees).filter(models.Employees.employment_status_id == 0).filter(func.extract('month', models.Employees.date_of_birth) == datetime.date.today().month).filter(func.extract('day', models.Employees.date_of_birth) == datetime.date.today().day).all()

    end_date = datetime.date.today() + datetime.timedelta(days=8)
    upcoming_offboardings = db.query(models.Employees).filter(models.Employees.employment_status_id == 0).filter(models.Employees.end_date > datetime.date.today()).filter(models.Employees.end_date <= end_date).all()

    role_state = db.query(models.Roles).filter(models.Roles.id == user['role_id']).first()

    return templates.TemplateResponse("home.html", {"request": request, "total_employees": total_employees, "total_offboarded_employees": total_offboarded_employees, "total_users": total_users, "todays_offboardings": todays_offboardings, "departments": departments, "sites": sites, "employments": employments, "missed_offboardings": missed_offboardings, "upcoming_offboardings": upcoming_offboardings, "todays_birthdays": todays_birthdays, "logged_in_user": user, "role_state": role_state})