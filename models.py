from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    password = Column(String(50))
    role_id = Column(Integer, ForeignKey('roles.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    active = Column(Boolean, default=True)

class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))

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
    gender = Column(String(10))
    date_of_birth = Column(DateTime)
    nationality = Column(String(50))
    supplier = Column(String(50))
    entity_to_be_billed = Column(String(50))
    employer_id = Column(Integer, ForeignKey('employers.id'))
    company_email = Column(String(50))
    job_title = Column(String(50))
    direct_manager_id = Column(Integer, ForeignKey('employees.id'))
    second_level_manager_id = Column(Integer, ForeignKey('employees.id'))
    third_level_manager_id = Column(Integer, ForeignKey('employees.id'))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    site_id = Column(Integer, ForeignKey('site.id'))
    country_of_origin_id = Column(Integer, ForeignKey('country.id'))
    working_country_id = Column(Integer, ForeignKey('country.id'))
    department_id = Column(Integer, ForeignKey('department.id'))
    product_code = Column(String(50))
    brand_code = Column(String(50))
    business_unit = Column(String(50))
    business_vertical = Column(String(50))
    salary_currency_id = Column(Integer, ForeignKey('currency.id'))
    salary = Column(Integer)
    salary_period = Column(String(50))
    hr_team_id = Column(Integer, ForeignKey('teams.id'))
    working_hours = Column(Integer)
    employment_contract_id = Column(Integer, ForeignKey('contract.id'))
    employment_type_id = Column(Integer, ForeignKey('employment.id'))
    employment_status_id = Column(Integer, ForeignKey('status.id'))

class Employers(Base):
    __tablename__ = 'employers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String(200))

class Site(Base):
    __tablename__ = 'site'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String(200))

class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    short_name = Column(String(2))

class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String(200))

class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    symbol = Column(String(1))

class Contract(Base):
    __tablename__ = 'contract'
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