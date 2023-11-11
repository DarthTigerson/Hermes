from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from routers.admin import get_current_user
from routers.logging import create_log, Log
from models import Roles, Settings
import models, datetime

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette import status
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
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
async def get_settings(request: Request, page=None, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(models.Settings).order_by(models.Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.settings == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    settings = db.query(Settings).order_by(Settings.id.desc()).first()

    if page is None:
        return RedirectResponse(url="/settings/?page=trigger_points", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("settings.html", {"request": request, "logged_in_user": user, "role_state": role_state, "settings": settings, "page": page, "settings": settings})

@router.post("/", response_class=HTMLResponse)
async def post_settings(request: Request, page: str, db: Session = Depends(get_db), trigger_onboarded_employee: bool = Form(False), trigger_updated_employee: bool = Form(False), trigger_offboarded_employee: bool = Form(False), slack_webhook: str = Form(None), email_list: str = Form(None), email_smtp_server: str = Form(None), email_smtp_port: int = Form(587), email_smtp_username: str = Form(None), email_smtp_password: str = Form(None)):
    
    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.settings == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    settings = db.query(Settings).order_by(Settings.id.desc()).first()

    if page == 'trigger_points':
        settings.email_new_employee = trigger_onboarded_employee
        settings.email_updated_employee = trigger_updated_employee
        settings.email_offboarded_employee = trigger_offboarded_employee
    elif page == 'slack_settings':
        if slack_webhook == '' or slack_webhook == 'None' or slack_webhook is None:
            settings.slack_webhook_channel = None
        else:
            settings.slack_webhook_channel = slack_webhook
    elif page == 'email_settings':
        settings.email_list = email_list
        settings.email_smtp_server = email_smtp_server
        settings.email_smtp_port = email_smtp_port
        settings.email_smtp_username = email_smtp_username
        if email_smtp_password == '' and settings is None:
            settings.email_smtp_password = None
        elif email_smtp_password != '' and settings is None:
            settings.email_smtp_password = email_smtp_password
        elif email_smtp_password == '' and settings is not None:
            settings.email_smtp_password = settings.email_smtp_password
        elif email_smtp_password != '' and settings is not None:
            settings.email_smtp_password = email_smtp_password
    settings.daily_user_reports = False
    settings.monthly_user_reports = False

    db.add(settings)
    db.commit()

    return RedirectResponse(url="/settings", status_code=status.HTTP_302_FOUND)