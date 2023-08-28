from fastapi import FastAPI
from routers import employee, home, manage, admin, logging, about
from database import SessionLocal, engine
import models
from starlette.staticfiles import StaticFiles

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(employee.router)
app.include_router(manage.router)
app.include_router(admin.router)
app.include_router(logging.router)
app.include_router(about.router)

def create_default_user():
    db = SessionLocal()
    try:
        # Wipe the database
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)

        # Create a default role
        role = models.Roles(name="admin", description="Administrator", onboarding=True, employee_updates=True, offboarding=True, manage_modify=True, payroll=True, admin=True, logs=True, api_report=True)
        db.add(role)
        db.commit()

        # Create a default user
        user = models.Users(first_name="Hermes", last_name="Admin", username="hermes", password="nimda", role_id=role.id)
        db.add(user)
        db.commit()

        print("Default user and role created successfully.")
    except Exception as e:
        print(f"Error creating default user and role: {e}")
    finally:
        db.close()