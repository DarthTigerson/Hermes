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

    return templates.TemplateResponse("preferences.html", {"request": request, "logged_in_user": user, "role_state": role_state})