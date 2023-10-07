from fastapi import APIRouter, Depends, status, HTTPException, Request, Form, Response
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from database import SessionLocal, engine
from pydantic import BaseModel, Field
from models import Preferences, Base
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from starlette import status
from starlette.responses import RedirectResponse

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
    preferences = db.query(Preferences).order_by(Preferences.id.desc()).first()

    if preferences is not None:
        if preferences.slack_webhook_channel is not None:
            url = preferences.slack_webhook_channel
            payload = {'text': message}
            response = requests.post(url, json=payload)
            return response.text
        else:
            return "No Slack Webhook URL set"
    
@router.post("/send_email/{message}/{subject}")
async def email_send_message(message: str, subject: str, db: Session = Depends(get_db)):
    preferences = db.query(Preferences).order_by(Preferences.id.desc()).first()

    if preferences is not None:
        if preferences.email_smtp_server is not None:
            msg = MIMEMultipart()
            msg['From'] = preferences.email_smtp_username
            msg['To'] = preferences.email_list
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(preferences.email_smtp_server, preferences.email_smtp_port)
            server.starttls()
            server.login(preferences.email_smtp_username, preferences.email_smtp_password)
            text = msg.as_string()
            server.sendmail(preferences.email_smtp_password, preferences.email_list, text)
            server.quit()
        else:
            return "No Email SMTP Server set"