from database import Base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey

class Logs(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50))
    user = Column(String(50))
    description = Column(String(200))
    date = Column(DateTime)

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50), unique=True, index=True)
    password = Column(String(50))
    role_id = Column(Integer, ForeignKey('roles.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    token = Column(String(250))
    active = Column(Boolean, default=True)
    users_profile = Column(String(250), default=None)
    dark_mode = Column(Integer, default=0)

class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String(200))
    onboarding = Column(Boolean, default=False)
    employee_updates = Column(Boolean, default=False)
    offboarding = Column(Boolean, default=False)
    manage_modify = Column(Boolean, default=False)
    payroll = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    logs = Column(Boolean, default=False)
    settings = Column(Boolean, default=False)
    api_report = Column(Boolean, default=False)

class Teams(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String(200))

class Employees(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    full_name = Column(String(100))
    employee_profiles = Column(String(250), default=None)
    gender = Column(Integer)
    date_of_birth = Column(String(50))
    nationality = Column(String(50))
    supplier = Column(String(50))
    entity_to_be_billed = Column(String(50))
    employer_id = Column(Integer, ForeignKey('employers.id'))
    company_email = Column(String(50))
    job_title = Column(String(50))
    direct_manager = Column(String(50))
    start_date = Column(String(50))
    end_date = Column(String(50))   
    site_id = Column(Integer, ForeignKey('sites.id'))
    country_of_origin_id = Column(Integer, ForeignKey('country.id'))
    working_country_id = Column(Integer, ForeignKey('country.id'))
    personal_email = Column(String(50))
    department_id = Column(Integer, ForeignKey('departments.id'))
    product_code = Column(String(50))
    brand_code = Column(String(50))
    business_unit = Column(String(50))
    business_verticle = Column(String(50))
    salary_currency_id = Column(Integer, ForeignKey('currency.id'))
    salary = Column(String(50))
    salary_period = Column(String(50))
    net_monthly_salary = Column(String(50))
    salary_pay_frequency_id = Column(Integer, ForeignKey('salary_pay_frequency.id'))
    change_reason = Column(String(50))
    increase_percentage = Column(String(50))
    hr_team_id = Column(Integer, ForeignKey('teams.id'))
    working_hours = Column(Integer)
    employment_contract_id = Column(Integer, ForeignKey('contracts.id'))
    employment_type_id = Column(Integer, ForeignKey('employment.id'))
    employment_status_id = Column(Integer, ForeignKey('status.id'))
    created_date = Column(DateTime)
    modified_date = Column(DateTime)

class Employers(Base):
    __tablename__ = 'employers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String(200))

class Sites(Base):
    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String(200))

class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    short_name = Column(String(5))

class Departments(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String(200))

class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    symbol = Column(String(5))

class Contracts(Base):
    __tablename__ = 'contracts'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String(200))

class Employment(Base):
    __tablename__ = 'employment'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))

class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))

class PayFrequency(Base):
    __tablename__ = 'salary_pay_frequency'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))

class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, index=True)
    email_new_employee = Column(Boolean, default=False)
    email_updated_employee = Column(Boolean, default=False)
    email_offboarded_employee = Column(Integer, default=False)
    trigger_welcome_email = Column(Boolean, default=False)
    email_list = Column(String(200), default=None)
    email_smtp_server = Column(String(200), default=None)
    email_smtp_port = Column(Integer, default=587)
    email_smtp_username = Column(String(200), default=None)
    email_smtp_password = Column(String(200), default=None)
    slack_webhook_channel = Column(String(200), default=None)
    daily_user_reports = Column(Boolean, default=False)
    monthly_user_reports = Column(Boolean, default=False)
    company_logo = Column(String(250), default=None)
    navigation_bar_color = Column(String(10), default='0e76a8')
    primary_color = Column(String(10), default='0e76a8')
    primary_color_hover = Column(String(10), default='0069d9')
    secondary_color = Column(String(10), default='6c757d')
    secondary_color_hover = Column(String(10), default='5a6268')
    info_color = Column(String(10), default='17a2b8')
    info_color_hover = Column(String(10), default='138496')
    critical_color = Column(String(10), default='dc3545')
    critical_color_hover = Column(String(10), default='bd2130')
    table_color_id = Column(Integer, default=1)

class Employee_Contracts(Base):
    __tablename__ = 'employee_contracts'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    start_date = Column(String(50))
    end_date = Column(String(50))
    contract_name = Column(String(250))
    notes = Column(String(250))
    contract_file = Column(String)

class Email_Templates(Base):
    __tablename__ = 'email_templates'
    id = Column(Integer, primary_key=True, index=True)
    onboarding_subject = Column(String(250))
    onboarding_body = Column(String)
    employee_updates_subject = Column(String(250))
    employee_updates_body = Column(String)
    offboarding_subject = Column(String(250))
    offboarding_body = Column(String)
    welcome_email_subject = Column(String(250))
    welcome_email_body = Column(String)