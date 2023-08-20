from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Users, Roles, Teams

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette import status
from starlette.responses import RedirectResponse
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
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
    users = db.query(Users).order_by(Users.username).all()
    roles = db.query(Roles).order_by(Roles.name).all()
    teams = db.query(Teams).order_by(Teams.name).all()

    return templates.TemplateResponse("admin.html", {"request": request, "users": users, "roles": roles, "teams": teams})

@router.get("/add_role")
async def add_role(request: Request):
    return templates.TemplateResponse("add-role.html", {"request": request})

@router.post("/add_role", response_class=HTMLResponse)
async def create_role(request: Request, name: str = Form(...), description: str = Form(None), onboarding: bool = Form(False), offboarding: bool = Form(False), manage_modify: bool = Form(False), admin: bool = Form(False), db: Session = Depends(get_db)):
    role_model = Roles()

    role_model.name = name
    role_model.description = description
    role_model.onboarding = onboarding
    role_model.offboarding = offboarding
    role_model.manage_modify = manage_modify
    role_model.admin = admin

    db.add(role_model)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/add_user")
async def add_user(request: Request, db: Session = Depends(get_db)):
    roles = db.query(Roles).order_by(Roles.name).all()
    teams = db.query(Teams).order_by(Teams.name).all()

    return templates.TemplateResponse("add-user.html", {"request": request, "roles": roles, "teams": teams})

@router.post("/add_user", response_class=HTMLResponse)
async def create_user(request: Request, username: str = Form(...), first_name: str = Form(...), last_name: str = Form(...), role_id: int = Form(...), team_id: int = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user_model = Users()

    user_model.username = username
    user_model.first_name = first_name
    user_model.last_name = last_name
    user_model.role_id = role_id
    user_model.team_id = team_id
    user_model.password = password

    db.add(user_model)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)