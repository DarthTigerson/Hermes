from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from pydantic import BaseModel, Field
from models import Departments, Sites, Contracts, Employers, Employment, Country, Currency

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette import status
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix="/manage",
    tags=["manage"],
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
    departments = db.query(Departments).order_by(Departments.name).all()
    sites = db.query(Sites).order_by(Sites.name).all()
    contracts = db.query(Contracts).order_by(Contracts.name).all()
    employers = db.query(Employers).order_by(Employers.name).all()
    employment = db.query(Employment).order_by(Employment.name).all()
    country = db.query(Country).order_by(Country.name).all()
    currency = db.query(Currency).order_by(Currency.name).all()

    return templates.TemplateResponse("manage.html", {"request": request, "departments": departments, "sites": sites, "contracts": contracts, "employers": employers, "employment": employment, "countries": country, "currencies": currency})

@router.get("/add_department")
async def add_department(request: Request):
    return templates.TemplateResponse("add-department.html", {"request": request})

@router.post("/add_department", response_class=HTMLResponse)
async def create_department(request: Request, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    department_model = Departments()

    department_model.name = name
    department_model.description = description

    db.add(department_model)
    db.commit()
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_department/{department_id}")
async def edit_department(request: Request, department_id: int, db: Session = Depends(get_db)):
    department = db.query(Departments).filter(Departments.id == department_id).first()

    return templates.TemplateResponse("edit-department.html", {"request": request, "department": department})

@router.post("/edit_department/{department_id}", response_class=HTMLResponse)
async def update_department(request: Request, department_id: int, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):

    department_model = db.query(Departments).filter(Departments.id == department_id).first()

    department_model.name = name
    department_model.description = description

    db.add(department_model)
    db.commit()

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_department/{department_id}")
async def delete_department(request: Request, department_id: int, db: Session = Depends(get_db)):
    department = db.query(Departments).filter(Departments.id == department_id).first()

    if department is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    db.query(Departments).filter(Departments.id == department_id).delete()
    db.commit()

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/add_site")
async def add_site(request: Request):
    return templates.TemplateResponse("add-site.html", {"request": request})

@router.post("/add_site", response_class=HTMLResponse)
async def create_site(request: Request, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    site_model = Sites()

    site_model.name = name
    site_model.description = description

    db.add(site_model)
    db.commit()
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_site/{site_id}")
async def edit_site(request: Request, site_id: int, db: Session = Depends(get_db)):
    site = db.query(Sites).filter(Sites.id == site_id).first()

    return templates.TemplateResponse("edit-site.html", {"request": request, "site": site})

@router.post("/edit_site/{site_id}", response_class=HTMLResponse)
async def update_site(request: Request, site_id: int, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    site_model = db.query(Sites).filter(Sites.id == site_id).first()

    site_model.name = name
    site_model.description = description

    db.add(site_model)
    db.commit()

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_site/{site_id}")
async def delete_site(request: Request, site_id: int, db: Session = Depends(get_db)):
    site = db.query(Sites).filter(Sites.id == site_id).first()

    if site is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    db.query(Sites).filter(Sites.id == site_id).delete()
    db.commit()

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)