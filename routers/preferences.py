from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from routers.admin import get_current_user
from routers.logging import create_log, Log
from models import Roles, Preferences
import models, datetime

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette import status
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix="/preferences",
    tags=["preferences"],
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
async def get_preferences(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.preferences == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    preferences = db.query(Preferences).order_by(Preferences.id.desc()).first()

    return templates.TemplateResponse("preferences.html", {"request": request, "logged_in_user": user, "role_state": role_state, "preferences": preferences, "nav": 'settings'})

@router.post("/", response_class=HTMLResponse)
async def post_preferences(request: Request, db: Session = Depends(get_db), trigger_onboarded_employee: bool = Form(False), trigger_updated_employee: bool = Form(False), trigger_offboarded_employee: bool = Form(False), slack_webhook: str = Form(None), email_list: str = Form(None), email_smtp_server: str = Form(None), email_smtp_port: int = Form(587), email_smtp_username: str = Form(None), email_smtp_password: str = Form(None)):
    
    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.preferences == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    preferences = db.query(Preferences).order_by(Preferences.id.desc()).first()

    preferences_model = Preferences()

    preferences_model.email_new_employee = trigger_onboarded_employee
    preferences_model.email_updated_employee = trigger_updated_employee
    preferences_model.email_offboarded_employee = trigger_offboarded_employee
    preferences_model.email_list = email_list
    preferences_model.email_smtp_server = email_smtp_server
    preferences_model.email_smtp_port = email_smtp_port
    preferences_model.email_smtp_username = email_smtp_username
    if email_smtp_password == '' and preferences is None:
        preferences_model.email_smtp_password = None
    elif email_smtp_password != '' and preferences is None:
        preferences_model.email_smtp_password = email_smtp_password
    elif email_smtp_password == '' and preferences is not None:
        preferences_model.email_smtp_password = preferences.email_smtp_password
    elif email_smtp_password != '' and preferences is not None:
        preferences_model.email_smtp_password = email_smtp_password
    if slack_webhook == '' or slack_webhook == 'None' or slack_webhook is None:
        preferences_model.slack_webhook_channel = None
    else:
        preferences_model.slack_webhook_channel = slack_webhook
    preferences_model.daily_user_reports = False
    preferences_model.monthly_user_reports = False

    db.add(preferences_model)
    db.commit()

    return RedirectResponse(url="/preferences", status_code=status.HTTP_302_FOUND)