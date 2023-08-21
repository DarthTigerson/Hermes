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
async def create_role(request: Request, name: str = Form(...), description: str = Form(None), onboarding: bool = Form(False), employee_updates: bool = Form(False), offboarding: bool = Form(False), manage_modify: bool = Form(False), admin: bool = Form(False), payroll: bool = Form(False), api_report: bool = Form(False), db: Session = Depends(get_db)):
    role_model = Roles()

    role_model.name = name
    role_model.description = description
    role_model.onboarding = onboarding
    role_model.employee_updates = employee_updates
    role_model.offboarding = offboarding
    role_model.manage_modify = manage_modify
    role_model.admin = admin
    role_model.payroll = payroll
    role_model.api_report = api_report

    db.add(role_model)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/edit_role/{role_id}")
async def edit_role(request: Request, role_id: int, db: Session = Depends(get_db)):
    role = db.query(Roles).filter(Roles.id == role_id).first()
    
    return templates.TemplateResponse("edit-role.html", {"request": request, "role": role})

@router.post("/edit_role/{role_id}", response_class=HTMLResponse)
async def edit_role(request: Request, role_id: int, name: str = Form(...), description: str = Form(None), onboarding: bool = Form(False), employee_updates: bool = Form(False), offboarding: bool = Form(False), manage_modify: bool = Form(False), admin: bool = Form(False), payroll: bool = Form(False), api_report: bool = Form(False), db: Session = Depends(get_db)):
    role = db.query(Roles).filter(Roles.id == role_id).first()

    role.name = name
    role.description = description
    role.onboarding = onboarding
    role.employee_updates = employee_updates
    role.offboarding = offboarding
    role.manage_modify = manage_modify
    role.admin = admin
    role.payroll = payroll
    role.api_report = api_report

    db.add(role)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/add_team")
async def add_team(request: Request):
    return templates.TemplateResponse("add-team.html", {"request": request})

@router.post("/add_team", response_class=HTMLResponse)
async def create_team(request: Request, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    team_model = Teams()

    team_model.name = name
    team_model.description = description

    db.add(team_model)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/edit_team/{team_id}")
async def edit_team(request: Request, team_id: int, db: Session = Depends(get_db)):
    team = db.query(Teams).filter(Teams.id == team_id).first()
    
    return templates.TemplateResponse("edit-team.html", {"request": request, "team": team})

@router.post("/edit_team/{team_id}", response_class=HTMLResponse)
async def update_team(request: Request, team_id: int, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    team = db.query(Teams).filter(Teams.id == team_id).first()

    team.name = name
    team.description = description

    db.add(team)
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

@router.get("/edit_user/{user_id}")
async def edit_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    roles = db.query(Roles).order_by(Roles.name).all()
    teams = db.query(Teams).order_by(Teams.name).all()
    
    return templates.TemplateResponse("edit-user.html", {"request": request, "user": user, "roles": roles, "teams": teams})

@router.post("/edit_user/{user_id}", response_class=HTMLResponse)
async def update_user(request: Request, user_id: int, username: str = Form(...), first_name: str = Form(...), last_name: str = Form(...), role_id: int = Form(...), team_id: int = Form(...), db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()

    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.role_id = role_id
    user.team_id = team_id

    db.add(user)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)