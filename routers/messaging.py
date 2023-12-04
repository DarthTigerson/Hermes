import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated

import requests
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Settings, Email_Templates, Employees, Base

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/messaging",
    tags=["messaging"],
)

templates = Jinja2Templates(directory='templates')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/slack_send_message/{message}")
async def slack_send_message(message: str, db: Session = Depends(get_db)):
    settings = db.query(Settings).order_by(Settings.id.desc()).first()

    if settings is not None:
        if settings.slack_webhook_channel is not None:
            url = settings.slack_webhook_channel
            payload = {'text': message}
            response = requests.post(url, json=payload)
            return response.text
        else:
            return "No Slack Webhook URL set"

        
@router.post("/send_email_template/{template}/{employee_id}")
async def email_send_template(template: int, employee_id: int, db: Session = Depends(get_db)):
    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    employee = db.query(Employees).filter(Employees.id == employee_id).first()
    email_templates = db.query(Email_Templates).filter(Email_Templates.id == template).first()

    if settings is not None:
        if settings.email_smtp_server is not None:
            msg = MIMEMultipart()
            msg['From'] = settings.email_smtp_username
            msg['To'] = employee.email
            if settings.email_new_employee is not False and template == 1:
                msg['Subject'] = email_templates.onboarding_subject
                message_body = email_templates.onboarding_message
            elif settings.email_updated_employee is not False and template == 2:
                msg['Subject'] = email_templates.updated_subject
                message_body = email_templates.updated_message
            elif settings.email_offboarded_employee is not False and template == 3:
                msg['Subject'] = email_templates.offboarded_subject
                message_body = email_templates.offboarded_message
            elif settings.trigger_welcome_email is not False and template == 4:
                msg['Subject'] = email_templates.welcome_subject
                message_body = email_templates.welcome_message

            #TAG replacements
            message_body = message_body.replace("{first_name}", employee.first_name)
            message_body = message_body.replace("{start_date}", employee.start_date.strftime("%d/%m/%Y"))
            message_body = message_body.replace("{end_date}", employee.end_date.strftime("%d/%m/%Y"))
            message_body = message_body.replace("{company_email}", employee.email)
            message_body = message_body.replace("{job_title}", employee.job_title)
            message_body = message_body.replace("{current_employer}", employee.current_employer)
            message_body = message_body.replace("{direct_manager}", employee.direct_manager)
            message_body = message_body.replace("{employment_contract}", employee.employment_contract)
            message_body = message_body.replace("{employment_type}", employee.employment_type)
            message_body = message_body.replace("{site}", employee.site)
            message_body = message_body.replace("{hr_department}", employee.hr_department)
            message_body = message_body.replace("{business_unit}", employee.business_unit)
            message_body = message_body.replace("{business_verticle}", employee.business_verticle)
            message_body = message_body.replace("{brand_code}", employee.brand_code)
            message_body = message_body.replace("{product_code}", employee.product_code)
            message_body = message_body.replace("{department}", employee.department)
            
            msg.attach(MIMEText(message_body, 'html'))
            server = smtplib.SMTP(settings.email_smtp_server, settings.email_smtp_port)
            server.starttls()
            server.login(settings.email_smtp_username, settings.email_smtp_password)
            text = msg.as_string()
            server.sendmail(settings.email_smtp_password, employee.email, text)
            server.quit()
        else:
            return "No Email SMTP Server set"

    
    
@router.post("/send_email/{message}/{subject}")
async def email_send_message(message: str, subject: str, db: Session = Depends(get_db)):
    settings = db.query(Settings).order_by(Settings.id.desc()).first()

    if settings is not None:
        if settings.email_smtp_server is not None:
            msg = MIMEMultipart()
            msg['From'] = settings.email_smtp_username
            msg['To'] = settings.email_list
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(settings.email_smtp_server, settings.email_smtp_port)
            server.starttls()
            server.login(settings.email_smtp_username, settings.email_smtp_password)
            text = msg.as_string()
            server.sendmail(settings.email_smtp_password, settings.email_list, text)
            server.quit()
        else:
            return "No Email SMTP Server set"