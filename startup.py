from database import SessionLocal, engine
import models
from routers import admin

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
        user = models.Users(first_name="Hermes", last_name="Admin", username="hermes", password=admin.get_password_hash('hermes'), role_id=role.id, team_id=0, active=True)
        db.add(user)
        db.commit()

        print("Default user and role created successfully.")
    except Exception as e:
        print(f"Error creating default user and role: {e}")
    finally:
        db.close()

def create_all_countries():
    db = SessionLocal()
    try:
        # Delete all existing countries
        db.query(models.Country).delete()

        # Add all countries in the world
        with open('static/data/countries.txt', 'r') as f:
            for line in f:
                name, short_name = line.strip().split(',')
                country = models.Country(name=name, short_name=short_name)
                db.add(country)
        db.commit()

        print("All countries added successfully.")
    except Exception as e:
        print(f"Error adding countries: {e}")
    finally:
        db.close()
    
def create_all_currencies():
    db = SessionLocal()
    try:
        # Delete all existing currencies
        db.query(models.Currency).delete()

        # Add all currencies in the world
        with open('static/data/currencies.txt', 'r') as f:
            for line in f:
                name, symbol = line.strip().split(',')
                currencies = models.Currency(name=name, symbol=symbol)
                db.add(currencies)
        db.commit()

        print("All currencies added successfully.")
    except Exception as e:
        print(f"Error adding currencies: {e}")
    finally:
        db.close()

#create_default_user()
#create_all_countries()
create_all_currencies()