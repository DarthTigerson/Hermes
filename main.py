from fastapi import FastAPI
from routers import admin, contracts, country, currency, departments, employers, employment, sites, status
from database import engine
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(admin.router)
app.include_router(contracts.router)
app.include_router(country.router)
app.include_router(currency.router)
app.include_router(departments.router)
app.include_router(employers.router)
app.include_router(employment.router)
app.include_router(sites.router)
app.include_router(status.router)