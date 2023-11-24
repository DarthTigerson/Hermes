from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from database import SessionLocal, engine
from models import Users, Roles, Teams, Base, Settings
from routers.messaging import slack_send_message

import base64

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

templates = Jinja2Templates(directory='templates')

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db) -> bool or Users:
    user = db.query(Users)\
        .filter(Users.username == username)\
        .first()

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(id: int, username: str, role_id: int,
                        expires_delta: Optional[timedelta] = None):

    encode = {"sub": username, "role_id": role_id, "id": id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role_id: int = payload.get("role_id")
        id: int = payload.get("id")
        if username is None or role_id is None:
            logout(request)
        return {"username": username, "role_id": role_id, "id": id}
    except JWTError:
        logout(request)

@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=300)
    token = create_access_token(user.id,
                                user.username,
                                user.role_id,
                                expires_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True

@router.get("/")
async def test(request: Request, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    users = db.query(Users).order_by(Users.username).all()
    roles = db.query(Roles).order_by(Roles.name).all()
    teams = db.query(Teams).order_by(Teams.name).all()
    nav_profile_load = db.query(Users.users_profile).filter(Users.id == logged_in_user['id']).scalar()
    
    return templates.TemplateResponse("admin.html", {"request": request, "users": users, "roles": roles, "teams": teams, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, 'nav_profile_load': nav_profile_load})

@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    role_state = {"admin": 0}
    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    return templates.TemplateResponse("login.html", {"request": request, "role_state": role_state, "settings": settings})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response, form_data=form, db=db)
        if not validate_user_cookie:
            msg = "Incorrect username or password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg, "role_state": {"admin": 0}, "settings": settings})
        return response
    except:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg, "role_state": {"admin": 0}, "settings": settings})

@router.get("/add_role")
async def add_role(request: Request, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(Users.users_profile).filter(Users.id == logged_in_user['id']).scalar()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-role.html", {"request": request, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, "nav_profile_load": nav_profile_load})

@router.post("/add_role", response_class=HTMLResponse)
async def create_role(request: Request, name: str = Form(...), description: str = Form(None), onboarding: bool = Form(False), employee_updates: bool = Form(False), offboarding: bool = Form(False), manage_modify: bool = Form(False), admin: bool = Form(False), payroll: bool = Form(False), settings: bool = Form(False), api_report: bool = Form(False), db: Session = Depends(get_db)):

    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    role_model = Roles()

    role_model.name = name
    role_model.description = description
    role_model.onboarding = onboarding
    role_model.employee_updates = employee_updates
    role_model.offboarding = offboarding
    role_model.manage_modify = manage_modify
    role_model.admin = admin
    role_model.payroll = payroll
    role_model.settings = settings
    role_model.api_report = api_report

    db.add(role_model)
    db.commit()

    if payroll == True:
        await slack_send_message(f"<!channel> Role {name} has been created by {user['username']} with Payroll Access", db=db)

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/edit_role/{role_id}")
async def edit_role(request: Request, role_id: int, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(Users.users_profile).filter(Users.id == logged_in_user['id']).scalar()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    role = db.query(Roles).filter(Roles.id == role_id).first()

    return templates.TemplateResponse("edit-role.html", {"request": request, "role": role, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, "nav_profile_load": nav_profile_load})

@router.post("/edit_role/{role_id}", response_class=HTMLResponse)
async def edit_role(request: Request, role_id: int, name: str = Form(...), description: str = Form(None), onboarding: bool = Form(False), employee_updates: bool = Form(False), offboarding: bool = Form(False), manage_modify: bool = Form(False), admin: bool = Form(False), payroll: bool = Form(False), api_report: bool = Form(False), db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    role = db.query(Roles).filter(Roles.id == role_id).first()

    role.name = name
    role.description = description
    role.onboarding = onboarding
    role.employee_updates = employee_updates
    role.offboarding = offboarding
    role.manage_modify = manage_modify
    role.admin = admin
    role.payroll = payroll
    role.api_report = api_report

    db.add(role)
    db.commit()

    if payroll == True:
        await slack_send_message(f"<!channel> Role {name} has been modified by {logged_in_user['username']} to have access to Payroll Access", db=db)

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/add_team")
async def add_team(request: Request, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(Users.users_profile).filter(Users.id == logged_in_user['id']).scalar()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-team.html", {"request": request, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, "nav_profile_load": nav_profile_load})

@router.post("/add_team", response_class=HTMLResponse)
async def create_team(request: Request, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):

    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    team_model = Teams()

    team_model.name = name
    team_model.description = description

    db.add(team_model)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/edit_team/{team_id}")
async def edit_team(request: Request, team_id: int, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(Users.users_profile).filter(Users.id == logged_in_user['id']).scalar()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    team = db.query(Teams).filter(Teams.id == team_id).first()

    return templates.TemplateResponse("edit-team.html", {"request": request, "team": team, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, "nav_profile_load": nav_profile_load})

@router.post("/edit_team/{team_id}", response_class=HTMLResponse)
async def update_team(request: Request, team_id: int, name: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):

    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    team = db.query(Teams).filter(Teams.id == team_id).first()

    team.name = name
    team.description = description

    db.add(team)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/add_user")
async def add_user(request: Request, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(Users.users_profile).filter(Users.id == logged_in_user['id']).scalar()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    roles = db.query(Roles).order_by(Roles.name).all()
    teams = db.query(Teams).order_by(Teams.name).all()
    profile_load = 0

    return templates.TemplateResponse("add-user.html", {"request": request, "roles": roles, "teams": teams, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, "profile_load": profile_load, "nav_profile_load": nav_profile_load})

@router.post("/add_user", response_class=HTMLResponse)
async def create_user(request: Request, username: str = Form(...), first_name: str = Form(...), last_name: str = Form(...), role_id: int = Form(...), team_id: int = Form(None), password: str = Form(...), profile_image: str = Form(None), db: Session = Depends(get_db)):
    
    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    user_model = Users()

    user_model.username = username
    user_model.first_name = first_name
    user_model.last_name = last_name
    user_model.role_id = role_id
    user_model.team_id = team_id
    user_model.password = get_password_hash(password)
    if username != 'hermes':
        user_model.users_profile = profile_image

    db.add(user_model)
    db.commit()

    payroll_data_access = db.query(Roles).filter(Roles.id == role_id).first()

    if payroll_data_access.payroll == True:
        await slack_send_message(f"<!channel> User {username} has been created by {user['username']} with Payroll Access", db=db)

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/edit_user/{user_id}")
async def edit_user(request: Request, user_id: int, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()
    nav_profile_load = db.query(Users.users_profile).filter(Users.id == logged_in_user['id']).scalar()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    user = db.query(Users).filter(Users.id == user_id).first()
    roles = db.query(Roles).order_by(Roles.name).all()
    teams = db.query(Teams).order_by(Teams.name).all()
    profile_load = user.users_profile

    return templates.TemplateResponse("edit-user.html", {"request": request, "user": user, "roles": roles, "teams": teams, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, "profile_load": profile_load, "nav_profile_load": nav_profile_load})

@router.post("/edit_user/{user_id}", response_class=HTMLResponse)
async def update_user(request: Request, user_id: int, username: str = Form(...), first_name: str = Form(...), last_name: str = Form(...), role_id: int = Form(...), team_id: int = Form(...), profile_image: str = Form(None), db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    user = db.query(Users).filter(Users.id == user_id).first()

    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.role_id = role_id
    user.team_id = team_id
    user.users_profile = profile_image

    db.add(user)
    db.commit()

    payroll_data_access = db.query(Roles).filter(Roles.id == role_id).first()

    if payroll_data_access.payroll == True:
        await slack_send_message(f"<!channel> User {username} has been modified by {user.username} to have access to Payroll Access", db=db)

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/user_details/")
async def user_details(request: Request, db: Session = Depends(get_db)):
        
        logged_in_user = await get_current_user(request)
    
        if logged_in_user is None:
            return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
        
        settings = db.query(Settings).order_by(Settings.id.desc()).first()
        role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()
        roles = db.query(Roles).order_by(Roles.name).all()
        teams = db.query(Teams).order_by(Teams.name).all()
        user = db.query(Users).filter(Users.id == logged_in_user['id']).first()
        profile_load = user.users_profile
        nav_profile_load = db.query(Users.users_profile).filter(Users.id == logged_in_user['id']).scalar()
    
        return templates.TemplateResponse("user-details.html", {"request": request, "user": user, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, "roles": roles, "teams": teams, "profile_load": profile_load, "nav_profile_load": nav_profile_load})

@router.post("/user_details/", response_class=HTMLResponse)
async def change_picture(request: Request, profile_image: str = Form(None), db: Session = Depends(get_db)):
        logged_in_user = await get_current_user(request)
    
        if logged_in_user is None:
            return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
        
        user = db.query(Users).filter(Users.id == logged_in_user['id']).first()
        user.users_profile = profile_image

        db.add(user)
        db.commit()

        return RedirectResponse(url="/admin/user_details/", status_code=status.HTTP_302_FOUND)

@router.get("/delete_user/{user_id}")
async def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    user = db.query(Users).filter(Users.id == user_id).first()

    db.delete(user)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)

@router.get("/reset_password/{user_id}")
async def reset_password_page(request: Request, user_id: int, db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = db.query(Settings).order_by(Settings.id.desc()).first()
    role_state = db.query(Roles).filter(Roles.id == user['role_id']).first()
    nav_profile_load = db.query(Users.users_profile).filter(Users.id == logged_in_user['id']).scalar()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    user = db.query(Users).filter(Users.id == user_id).first()

    return templates.TemplateResponse("reset-password.html", {"request": request, "user": user, "logged_in_user": logged_in_user, "role_state": role_state, "settings": settings, "nav_profile_load": nav_profile_load})

@router.post("/reset_password/{user_id}", response_class=HTMLResponse)
async def reset_password(request: Request, user_id: int, password: str = Form(...), db: Session = Depends(get_db)):

    logged_in_user = await get_current_user(request)

    if logged_in_user is None:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    role_state = db.query(Roles).filter(Roles.id == logged_in_user['role_id']).first()

    if role_state.admin == False:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    user = db.query(Users).filter(Users.id == user_id).first()

    user.password = get_password_hash(password)

    db.add(user)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)