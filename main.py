from fastapi import FastAPI
from routers import employee, home, manage, admin, logging, about
from database import engine
import models
from starlette.staticfiles import StaticFiles
from starlette import status
from starlette.responses import RedirectResponse

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)

app.include_router(home.router)
app.include_router(employee.router)
app.include_router(manage.router)
app.include_router(admin.router)
app.include_router(logging.router)
app.include_router(about.router)