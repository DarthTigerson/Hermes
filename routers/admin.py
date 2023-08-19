from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Users, Roles, Teams

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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