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

@router.get("/add_contract")
async def add_contract(request: Request):
    return templates.TemplateResponse("add-contract.html", {"request": request})

@router.post("/add_contract", response_class=HTMLResponse)
async def create_contract(request: Request, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    contract_model = Contracts()

    contract_model.name = name
    contract_model.description = description

    db.add(contract_model)
    db.commit()
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_contract/{contract_id}")
async def edit_contract(request: Request, contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contracts).filter(Contracts.id == contract_id).first()

    return templates.TemplateResponse("edit-contract.html", {"request": request, "contract": contract})

@router.post("/edit_contract/{contract_id}", response_class=HTMLResponse)
async def update_contract(request: Request, contract_id: int, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    contract_model = db.query(Contracts).filter(Contracts.id == contract_id).first()

    contract_model.name = name
    contract_model.description = description

    db.add(contract_model)
    db.commit()

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_contract/{contract_id}")
async def delete_contract(request: Request, contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contracts).filter(Contracts.id == contract_id).first()

    if contract is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    db.query(Contracts).filter(Contracts.id == contract_id).delete()
    db.commit()

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/add_employer")
async def add_employer(request: Request):
    return templates.TemplateResponse("add-employer.html", {"request": request})

@router.post("/add_employer", response_class=HTMLResponse)
async def create_employer(request: Request, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    employer_model = Employers()

    employer_model.name = name
    employer_model.description = description

    db.add(employer_model)
    db.commit()
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_employer/{employer_id}")
async def edit_employer(request: Request, employer_id: int, db: Session = Depends(get_db)):
    employer = db.query(Employers).filter(Employers.id == employer_id).first()

    return templates.TemplateResponse("edit-employer.html", {"request": request, "employer": employer})

@router.post("/edit_employer/{employer_id}", response_class=HTMLResponse)
async def update_employer(request: Request, employer_id: int, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    employer_model = db.query(Employers).filter(Employers.id == employer_id).first()

    employer_model.name = name
    employer_model.description = description

    db.add(employer_model)
    db.commit()

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_employer/{employer_id}")
async def delete_employer(request: Request, employer_id: int, db: Session = Depends(get_db)):
    employer = db.query(Employers).filter(Employers.id == employer_id).first()

    if employer is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    db.query(Employers).filter(Employers.id == employer_id).delete()
    db.commit()

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
