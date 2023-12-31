from fastapi import FastAPI
from routers import employee, home, manage, admin, logging, messaging, reporting, settings
from database import engine
import models
from starlette.staticfiles import StaticFiles


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(employee.router)
app.include_router(reporting.router)
app.include_router(manage.router)
app.include_router(settings.router)
app.include_router(admin.router)
app.include_router(logging.router)
app.include_router(messaging.router)