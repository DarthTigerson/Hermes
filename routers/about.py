from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette import status
from starlette.responses import RedirectResponse
router = APIRouter(
    prefix="/about",
    tags=["about"],
)

templates = Jinja2Templates(directory='templates')

@router.get("/")
async def test(request: Request):

    return templates.TemplateResponse("about.html", {"request": request})