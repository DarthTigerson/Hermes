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
from models import Settings, Email_Templates, Employees, Employers, Contracts, Employment, Sites, Teams, Departments, Base
from datetime import datetime

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
    email_templates = db.query(Email_Templates).order_by(Email_Templates.id.desc()).first()

    if settings is not None:
        if settings.email_smtp_server is not None:
            msg = MIMEMultipart()
            msg['From'] = settings.email_smtp_username
            msg['To'] = settings.email_list
            if settings.email_new_employee is not False and template == 1:
                mail_subject = email_templates.onboarding_subject
                message_body = email_templates.onboarding_body
            elif settings.email_updated_employee is not False and template == 2:
                mail_subject  = email_templates.employee_updates_subject
                message_body = email_templates.employee_updates_body
            elif settings.email_offboarded_employee is not False and template == 3:
                mail_subject  = email_templates.offboarding_subject
                message_body = email_templates.offboarding_body
            elif settings.trigger_welcome_email is not False and template == 4:
                msg['To'] = employee.personal_email
                mail_subject = email_templates.welcome_email_subject
                message_body = email_templates.welcome_email_body

            # Convert employee.start_date and employee.end_date to datetime objects
            start_date = datetime.strptime(employee.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(employee.end_date, "%Y-%m-%d")
            current_employer = db.query(Employers).filter(Employers.id == employee.employer_id).first()
            employment_contract = db.query(Contracts).filter(Contracts.id == employee.employment_contract_id).first()
            employment_type = db.query(Employment).filter(Employment.id == employee.employment_type_id).first()
            site = db.query(Sites).filter(Sites.id == employee.site_id).first()
            department = db.query(Departments).filter(Departments.id == employee.department_id).first()
            hr_teams = db.query(Teams).filter(Teams.id == employee.hr_team_id).first()

            if hr_teams is None:
                hr_teams_name = "No Team Assigned"
            else:
                hr_teams_name = hr_teams.name

            #TAG replacements
            mail_subject = mail_subject.replace("{full_name}", employee.full_name)
            message_body = message_body.replace("{full_name}", employee.full_name)
            message_body = message_body.replace("{start_date}", start_date.strftime("%d/%m/%Y"))
            message_body = message_body.replace("{end_date}", end_date.strftime("%d/%m/%Y"))
            message_body = message_body.replace("{company_email}", employee.email)
            message_body = message_body.replace("{job_title}", employee.job_title)
            message_body = message_body.replace("{current_employer}", current_employer.name)
            message_body = message_body.replace("{direct_manager}", employee.direct_manager)
            message_body = message_body.replace("{employment_contract}", employment_contract.name)
            message_body = message_body.replace("{employment_type}", employment_type.name)
            message_body = message_body.replace("{site}", site.name)
            message_body = message_body.replace("{hr_department}", hr_teams_name)
            message_body = message_body.replace("{business_unit}", employee.business_unit)
            message_body = message_body.replace("{business_verticle}", employee.business_verticle)
            message_body = message_body.replace("{brand_code}", employee.brand_code)
            message_body = message_body.replace("{product_code}", employee.product_code)
            message_body = message_body.replace("{department}", department.name)

            msg['Subject'] = mail_subject
            msg.attach(MIMEText(message_body, 'html'))
            server = smtplib.SMTP(settings.email_smtp_server, settings.email_smtp_port)
            server.starttls()
            server.login(settings.email_smtp_username, settings.email_smtp_password)
            text = msg.as_string()
            server.sendmail(settings.email_smtp_password, msg['To'], text)
            server.quit()
        else:
            return "No Email SMTP Server set"