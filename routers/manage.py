from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from database import SessionLocal
from models import Departments, Sites, Contracts, Employers, Employment, Country, Currency, PayFrequency, Roles, \
    Settings
from routers.admin import get_current_user
from routers.logging import create_log, Log

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

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    departments = db.query(Departments).order_by(Departments.name).all()
    sites = db.query(Sites).order_by(Sites.name).all()
    contracts = db.query(Contracts).order_by(Contracts.name).all()
    employers = db.query(Employers).order_by(Employers.name).all()
    employment = db.query(Employment).order_by(Employment.name).all()
    country = db.query(Country).order_by(Country.name).all()
    currency = db.query(Currency).order_by(Currency.name).all()
    salary_pay_frequency = db.query(PayFrequency).order_by(PayFrequency.name).all()

    log = Log(action="Info",user=user['username'],description=f"Viewed the manage page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("manage.html", {"request": request, "departments": departments, "sites": sites, "contracts": contracts, "employers": employers, "employment": employment, "countries": country, "currencies": currency, "salary_pay_frequencies": salary_pay_frequency, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.get("/add_department")
async def add_department(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    log = Log(action="Info",user=user['username'],description=f"Viewed the add department page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("add-department.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/add_department", response_class=HTMLResponse)
async def create_department(request: Request, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    department_model = Departments()

    department_model.name = name
    department_model.description = description

    db.add(department_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Created a new department: {name}.")
    await create_log(request=request, log=log, db=db)
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_department/{department_id}")
async def edit_department(request: Request, department_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    department = db.query(Departments).filter(Departments.id == department_id).first()

    log = Log(action="Info",user=user['username'],description=f"Viewed the edit department page for {department.name}.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("edit-department.html", {"request": request, "department": department, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/edit_department/{department_id}", response_class=HTMLResponse)
async def update_department(request: Request, department_id: int, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    department_model = db.query(Departments).filter(Departments.id == department_id).first()

    department_model.name = name
    department_model.description = description

    db.add(department_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Updated the department: {name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_department/{department_id}")
async def delete_department(request: Request, department_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    department = db.query(Departments).filter(Departments.id == department_id).first()

    if department is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    db.query(Departments).filter(Departments.id == department_id).delete()
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Deleted the department: {department.name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/add_site")
async def add_site(request: Request, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    log = Log(action="Info",user=user['username'],description=f"Viewed the add site page.")
    await create_log(request=request, log=log, db=db)
    
    return templates.TemplateResponse("add-site.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/add_site", response_class=HTMLResponse)
async def create_site(request: Request, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    site_model = Sites()

    site_model.name = name
    site_model.description = description

    db.add(site_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Created a new site: {name}.")
    await create_log(request=request, log=log, db=db)
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_site/{site_id}")
async def edit_site(request: Request, site_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    site = db.query(Sites).filter(Sites.id == site_id).first()

    log = Log(action="Info",user=user['username'],description=f"Viewed the edit site page for {site.name}.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("edit-site.html", {"request": request, "site": site, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/edit_site/{site_id}", response_class=HTMLResponse)
async def update_site(request: Request, site_id: int, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    site_model = db.query(Sites).filter(Sites.id == site_id).first()

    site_model.name = name
    site_model.description = description

    db.add(site_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Updated the site: {name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_site/{site_id}")
async def delete_site(request: Request, site_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    site = db.query(Sites).filter(Sites.id == site_id).first()

    if site is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    db.query(Sites).filter(Sites.id == site_id).delete()
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Deleted the site: {site.name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/add_contract")
async def add_contract(request: Request, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    log = Log(action="Info",user=user['username'],description=f"Viewed the add contract page.")
    await create_log(request=request, log=log, db=db)
    
    return templates.TemplateResponse("add-contract.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/add_contract", response_class=HTMLResponse)
async def create_contract(request: Request, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    contract_model = Contracts()

    contract_model.name = name
    contract_model.description = description

    db.add(contract_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Created a new contract: {name}.")
    await create_log(request=request, log=log, db=db)
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_contract/{contract_id}")
async def edit_contract(request: Request, contract_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    contract = db.query(Contracts).filter(Contracts.id == contract_id).first()

    log = Log(action="Info",user=user['username'],description=f"Viewed the edit contract page for {contract.name}.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("edit-contract.html", {"request": request, "contract": contract, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/edit_contract/{contract_id}", response_class=HTMLResponse)
async def update_contract(request: Request, contract_id: int, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    contract_model = db.query(Contracts).filter(Contracts.id == contract_id).first()

    contract_model.name = name
    contract_model.description = description

    db.add(contract_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Updated the contract: {name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_contract/{contract_id}")
async def delete_contract(request: Request, contract_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    contract = db.query(Contracts).filter(Contracts.id == contract_id).first()

    if contract is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    db.query(Contracts).filter(Contracts.id == contract_id).delete()
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Deleted the contract: {contract.name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/add_employer")
async def add_employer(request: Request, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    log = Log(action="Info",user=user['username'],description=f"Viewed the add employer page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("add-employer.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/add_employer", response_class=HTMLResponse)
async def create_employer(request: Request, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    employer_model = Employers()

    employer_model.name = name
    employer_model.description = description

    db.add(employer_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Created a new employer: {name}.")
    await create_log(request=request, log=log, db=db)
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_employer/{employer_id}")
async def edit_employer(request: Request, employer_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    employer = db.query(Employers).filter(Employers.id == employer_id).first()

    log = Log(action="Info",user=user['username'],description=f"Viewed the edit employer page for {employer.name}.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("edit-employer.html", {"request": request, "employer": employer, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/edit_employer/{employer_id}", response_class=HTMLResponse)
async def update_employer(request: Request, employer_id: int, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    employer_model = db.query(Employers).filter(Employers.id == employer_id).first()

    employer_model.name = name
    employer_model.description = description

    db.add(employer_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Updated the employer: {name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_employer/{employer_id}")
async def delete_employer(request: Request, employer_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    employer = db.query(Employers).filter(Employers.id == employer_id).first()

    if employer is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    db.query(Employers).filter(Employers.id == employer_id).delete()
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Deleted the employer: {employer.name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/add_employment")
async def add_employment(request: Request, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    log = Log(action="Info",user=user['username'],description=f"Viewed the add employment page.")
    await create_log(request=request, log=log, db=db)
    
    return templates.TemplateResponse("add-employment.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/add_employment", response_class=HTMLResponse)
async def create_employment(request: Request, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    employment_model = Employment()

    employment_model.name = name
    employment_model.description = description

    db.add(employment_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Created a new employment: {name}.")
    await create_log(request=request, log=log, db=db)
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_employment/{employment_id}")
async def edit_employment(request: Request, employment_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    employment = db.query(Employment).filter(Employment.id == employment_id).first()

    log = Log(action="Info",user=user['username'],description=f"Viewed the edit employment page for {employment.name}.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("edit-employment.html", {"request": request, "employment": employment, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/edit_employment/{employment_id}", response_class=HTMLResponse)
async def update_employment(request: Request, employment_id: int, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    employment_model = db.query(Employment).filter(Employment.id == employment_id).first()

    employment_model.name = name
    employment_model.description = description

    db.add(employment_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Updated the employment: {name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_employment/{employment_id}")
async def delete_employment(request: Request, employment_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    employment = db.query(Employment).filter(Employment.id == employment_id).first()

    if employment is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    db.query(Employment).filter(Employment.id == employment_id).delete()
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Deleted the employment: {employment.name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/add_country")
async def add_country(request: Request, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    log = Log(action="Info",user=user['username'],description=f"Viewed the add country page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("add-country.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/add_country", response_class=HTMLResponse)
async def create_country(request: Request, name: str = Form(...), short_name: str = Form(...), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    country_model = Country()

    country_model.name = name
    country_model.short_name = short_name

    db.add(country_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Created a new country: {name}.")
    await create_log(request=request, log=log, db=db)
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_country/{country_id}")
async def edit_country(request: Request, country_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    country = db.query(Country).filter(Country.id == country_id).first()

    log = Log(action="Info",user=user['username'],description=f"Viewed the edit country page for {country.name}.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("edit-country.html", {"request": request, "country": country, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/edit_country/{country_id}", response_class=HTMLResponse)
async def update_country(request: Request, country_id: int, name: str = Form(...), short_name: str = Form(...), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    country_model = db.query(Country).filter(Country.id == country_id).first()

    country_model.name = name
    country_model.short_name = short_name

    db.add(country_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Updated the country: {name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_country/{country_id}")
async def delete_country(request: Request, country_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    counrty = db.query(Country).filter(Country.id == country_id).first()

    if counrty is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    db.query(Country).filter(Country.id == country_id).delete()
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Deleted the country: {counrty.name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/add_currency")
async def add_currency(request: Request, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    log = Log(action="Info",user=user['username'],description=f"Viewed the add currency page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("add-currency.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/add_currency", response_class=HTMLResponse)
async def create_currency(request: Request, name: str = Form(...), symbol: str = Form(...), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    currency_model = Currency()

    currency_model.name = name
    currency_model.symbol = symbol

    db.add(currency_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Created a new currency: {name}.")
    await create_log(request=request, log=log, db=db)
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_currency/{currency_id}")
async def edit_currency(request: Request, currency_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    currency = db.query(Currency).filter(Currency.id == currency_id).first()

    log = Log(action="Info",user=user['username'],description=f"Viewed the edit currency page for {currency.name}.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("edit-currency.html", {"request": request, "currency": currency, "logged_in_user": user, "role_state": role_state, "nav":"manage", "settings": settings})

@router.post("/edit_currency/{currency_id}", response_class=HTMLResponse)
async def update_currency(request: Request, currency_id: int, name: str = Form(...), symbol: str = Form(...), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    currency_model = db.query(Currency).filter(Currency.id == currency_id).first()

    currency_model.name = name
    currency_model.symbol = symbol

    db.add(currency_model)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Updated the currency: {name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_currency/{currency_id}")
async def delete_currency(request: Request, currency_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    currency = db.query(Currency).filter(Currency.id == currency_id).first()

    if currency is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    db.query(Currency).filter(Currency.id == currency_id).delete()
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Deleted the currency: {currency.name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/add_salary_pay_frequency")
async def add_salary_pay_frequency(request: Request, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    log = Log(action="Info",user=user['username'],description=f"Viewed the add salary pay frequency page.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("add-salary-frequency.html", {"request": request, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/add_salary_pay_frequency", response_class=HTMLResponse)
async def create_salary_pay_frequency(request: Request, name: str = Form(...), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    salary_pay_frequency = PayFrequency()

    salary_pay_frequency.name = name

    db.add(salary_pay_frequency)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Created a new salary pay frequency: {name}.")
    await create_log(request=request, log=log, db=db)
    
    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/edit_salary_pay_frequency/{spf_id}")
async def edit_salary_pay_frequency(request: Request, spf_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    payFrequency = db.query(PayFrequency).filter(PayFrequency.id == spf_id).first()

    log = Log(action="Info",user=user['username'],description=f"Viewed the edit salary pay frequency page for {payFrequency.name}.")
    await create_log(request=request, log=log, db=db)

    return templates.TemplateResponse("edit-salary-frequency.html", {"request": request, "salary_pay_frequency": payFrequency, "logged_in_user": user, "role_state": role_state, "nav": 'manage', "settings": settings})

@router.post("/edit_salary_pay_frequency/{spf_id}", response_class=HTMLResponse)
async def update_salary_pay_frequency(request: Request, spf_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    payFrequency = db.query(PayFrequency).filter(PayFrequency.id == spf_id).first()

    payFrequency.name = name

    db.add(payFrequency)
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Updated the salary pay frequency: {name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

@router.get("/delete_salary_pay_frequency/{spf_id}")
async def delete_salary_pay_frequency(request: Request, spf_id: int, db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.manage_modify == False:
        return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)

    payFrequency = db.query(PayFrequency).filter(PayFrequency.id == spf_id).first()

    if payFrequency is None:
        raise RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)
    
    db.query(PayFrequency).filter(PayFrequency.id == spf_id).delete()
    db.commit()

    log = Log(action="Info",user=user['username'],description=f"Deleted the salary pay frequency: {payFrequency.name}.")
    await create_log(request=request, log=log, db=db)

    return RedirectResponse(url="/manage", status_code=status.HTTP_302_FOUND)