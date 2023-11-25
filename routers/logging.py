import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from database import SessionLocal
from models import Logs, Roles, Settings, Users
from routers.admin import get_current_user

router = APIRouter(
    prefix="/logging",
    tags=["logging"],
)

templates = Jinja2Templates(directory='templates')

class Log(BaseModel):
    action: str = Field(...)
    user: str = Field(...)
    description: str = Field(...)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/")
async def show_logging(request: Request, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(Users.users_profile).filter(Users.id == logged_in_user['id']).scalar()

    if role_state.logs == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    logs = db.query(Logs).order_by(Logs.id.desc()).limit(400).all()

    return templates.TemplateResponse("logging.html", {"request": request, "logs": logs, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, "nav_profile_load": nav_profile_load})

@router.post("/create_log")
async def create_log(request: Request, log: Log, db: Session = Depends(get_db)):

    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.logs == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    log_model = Logs()

    log_model.action = log.action
    log_model.user = log.user
    log_model.description = log.description
    log_model.date = datetime.datetime.now()

    db.add(log_model)
    db.commit()

    return