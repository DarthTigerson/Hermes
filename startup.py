from database import SessionLocal, engine
import models, os
from routers import admin

def create_default_user():
    db = SessionLocal()
    try:
        # Wipe the database
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)

        # Create a default role
        role = models.Roles(name="Admin", description="Administrator", onboarding=True, employee_updates=True, offboarding=True, manage_modify=True, payroll=False, admin=True, preferences=True, logs=True, api_report=True)
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

def create_all_contracts():
    db = SessionLocal()
    try:
        # Delete all existing contracts
        db.query(models.Contracts).delete()

        # Add all contracts in the world
        with open('static/data/contracts.txt', 'r') as f:
            for line in f:
                name, description = line.strip().split(',')
                contract = models.Contracts(name=name, description=description)
                db.add(contract)
        db.commit()

        print("All contracts added successfully.")
    except Exception as e:
        print(f"Error adding contracts: {e}")
    finally:
        db.close()

def create_all_employment_types():
    db = SessionLocal()
    try:
        # Delete all existing employment types
        db.query(models.Employment).delete()

        # Add all employment types in the world
        with open('static/data/employment_types.txt', 'r') as f:
            for line in f:
                employment_type = models.Employment(name=line)
                db.add(employment_type)
        db.commit()

        print("All employment types added successfully.")
    except Exception as e:
        print(f"Error adding employment types: {e}")
    finally:
        db.close()

def create_all_departments():
    db = SessionLocal()
    try:
        # Delete all existing departments
        db.query(models.Departments).delete()

        # Add all departments in the world
        with open('static/data/departments.txt', 'r') as f:
            for line in f:
                name, description = line.strip().split(',')
                department = models.Departments(name=name, description=description)
                db.add(department)
        db.commit()

        print("All departments added successfully.")
    except Exception as e:
        print(f"Error adding departments: {e}")
    finally:
        db.close()

def create_all_employers():
    db = SessionLocal()
    try:
        # Delete all existing employers
        db.query(models.Employers).delete()

        # Add all employers in the world
        with open('static/data/employers.txt', 'r') as f:
            for line in f:
                name, description = line.strip().split(',')
                employer = models.Employers(name=name, description=description)
                db.add(employer)
        db.commit()

        print("All employers added successfully.")
    except Exception as e:
        print(f"Error adding employers: {e}")
    finally:
        db.close()

def create_all_pay_frequencies():
    db = SessionLocal()
    try:
        # Delete all existing pay frequencies
        db.query(models.PayFrequency).delete()

        # Add all pay frequencies in the world
        with open('static/data/pay_frequencies.txt', 'r') as f:
            for line in f:
                pay_frequency = models.PayFrequency(name=line)
                db.add(pay_frequency)
        db.commit()

        print("All pay frequencies added successfully.")
    except Exception as e:
        print(f"Error adding pay frequencies: {e}")
    finally:
        db.close()

def create_preferences_table():
    db = SessionLocal()
    try:
        # Delete all existing preferences
        db.query(models.Preferences).delete()

        # Setup Preferences table
        preferences = models.Preferences(id=1, email_new_employee=False, email_updated_employee=False, email_offboarded_employee=False, email_list=None, email_smtp_server=None, email_smtp_port=587, email_smtp_username=None, email_smtp_password=None, slack_webhook_channel=None, daily_user_reports=False, monthly_user_reports=False)
        db.add(preferences)
        db.commit()

        print("Preferences table created successfully.")
    except Exception as e:
        print(f"Error creating preferences table: {e}")
    finally:
        db.close()

def full_run():
    os.system('cls' if os.name == 'nt' else 'clear')

    db_path = "hermes.db"
    if os.path.exists(db_path):
        db_run_status = input("You are about to overwrite Hermes database!\nThis will delete all records and accounts currently present.\n\nAre you sure you want to proceed? (y/n): ")
    else:
        print("Setting up database for the first time.")
        db_run_status = "y"


    if db_run_status.lower() == 'y':
        create_default_user()
        create_all_countries()
        create_all_currencies()
        create_all_contracts()
        create_all_employment_types()
        create_all_departments()
        create_all_employers()
        create_all_pay_frequencies()
        create_preferences_table()
        #openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 730

        print("\nSetup complete.\nYou can launch Hermes with the following command: `uvicorn main:app --reload`")
    else:
        print("Setup cancelled.")

if __name__ == "__main__":
    full_run()