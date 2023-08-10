from database import Base
from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    password = Column(String(50))
    role_id = Column(Integer)
    active = Column(Boolean, default=True)

class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))