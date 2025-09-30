from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    flat_number = Column(String, nullable=False)
    contact_id = Column(String, nullable=False)
    role = Column(String, nullable=False) 

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    month = Column(String, nullable=False)
    expense_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    paid_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.name"), nullable=False)

class Maintenance(Base):
    __tablename__ = "maintenance"
    id = Column(Integer, primary_key=True, index=True)
    owner_name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    month = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    paid_by = Column(Integer, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)