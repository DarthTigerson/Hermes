from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

import base64
import models
from database import SessionLocal
from models import Roles, Settings
from routers.admin import get_current_user

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

    logged_in_user = await get_current_user(request)
    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(models.Users.users_profile).filter(models.Users.id == logged_in_user['id']).scalar()
    email_templates = db.query(models.Email_Templates).order_by(models.Email_Templates.id.desc()).first()

    if role_state.settings == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    settings = db.query(Settings).order_by(Settings.id.desc()).first()

    if page is None:
        return RedirectResponse(url="/settings/?page=trigger_points", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("settings.html", {"request": request, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, "page": page, "settings": settings, "nav_profile_load": nav_profile_load, "email_templates": email_templates})

@router.post("/", response_class=HTMLResponse)
async def post_settings(request: Request, page: str, db: Session = Depends(get_db), trigger_onboarded_employee: bool = Form(False), trigger_updated_employee: bool = Form(False), trigger_offboarded_employee: bool = Form(False), slack_webhook: str = Form(None), email_list: str = Form(None), email_smtp_server: str = Form(None), email_smtp_port: int = Form(587), email_smtp_username: str = Form(None), email_smtp_password: str = Form(None), navigation_bar_color: str = Form(None), primary_button_color: str = Form(None), primary_button_hover_color: str = Form(None), secondary_button_color: str = Form(None), secondary_button_hover_color: str = Form(None), info_button_color: str = Form(None), info_button_hover_color: str = Form(None), critical_button_color: str = Form(None), critical_button_hover_color: str = Form(None),  email_template_subject: str = Form(None), emailContent: str = Form(None)):
    
    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.settings == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    if page == 'trigger_points' or page == 'slack_settings' or page == 'email_settings' or page == 'color_palettes':
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
        elif page == 'color_palettes':
            settings.navigation_bar_color = navigation_bar_color
            settings.primary_color = primary_button_color
            settings.primary_color_hover = primary_button_hover_color
            settings.secondary_color = secondary_button_color
            settings.secondary_color_hover = secondary_button_hover_color
            settings.info_color = info_button_color
            settings.info_color_hover = info_button_hover_color
            settings.critical_color = critical_button_color
            settings.critical_color_hover = critical_button_hover_color
        settings.daily_user_reports = False
        settings.monthly_user_reports = False

        db.add(settings)
        db.commit()
    else:
        email_templates = db.query(models.Email_Templates).order_by(models.Email_Templates.id.desc()).first()

        if page == 'email_templates1':
            email_templates.onboarding_subject = email_template_subject
            email_templates.onboarding_body = emailContent
        elif page == 'email_templates2':
            email_templates.employee_updates_subject = email_template_subject
            email_templates.employee_updates_body = emailContent
        elif page == 'email_templates3':
            email_templates.offboarding_subject = email_template_subject
            email_templates.offboarding_body = emailContent
        elif page == 'email_templates4':
            email_templates.welcome_email_subject = email_template_subject
            email_templates.welcome_email_body = emailContent

        db.add(email_templates)
        db.commit()

    return RedirectResponse(url="/settings", status_code=status.HTTP_302_FOUND)

@router.post("/change_company_logo", response_class=HTMLResponse)
async def change_company_logo(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    logo = data.get('logo')

    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.settings == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    settings = db.query(Settings).order_by(Settings.id.desc()).first()

    settings.company_logo = logo

    db.add(settings)
    db.commit()

    return RedirectResponse(url="/settings/?page=color_palettes", status_code=status.HTTP_302_FOUND)

@router.get("/reset_company_logo", response_class=HTMLResponse)
async def reset_company_logo(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.settings == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    settings = db.query(Settings).order_by(Settings.id.desc()).first()

    # Open the image file in binary mode
    with open('static/img/logo.png', 'rb') as f:
        # Read the contents
        image_data = f.read()

    # Encode the image data into a base64 string
    hermes_logo = base64.b64encode(image_data).decode('utf-8')

    settings.company_logo = hermes_logo

    db.add(settings)
    db.commit()

    return RedirectResponse(url="/settings/?page=color_palettes", status_code=status.HTTP_302_FOUND)