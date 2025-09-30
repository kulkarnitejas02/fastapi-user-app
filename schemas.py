from pydantic import BaseModel
#from sqlalchemy import Column, Integer, String, Float, ForeignKey
from datetime import date

class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    flat_number: str
    contact_id: str
    role: str = "member"  # New field for role

class UserOut(BaseModel):
    id: int
    username: str
    name: str
    flat_number: str
    contact_id: str
    role: str  # New field for role

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    date: str
    month: str
    expense_name: str
    description: str
    amount: float
    paid_by: int | None = None
    created_by: int  

class ExpenseOut(ExpenseCreate):
    id: int
    date: date
    month: str
    created_by: int

    class Config:
        from_attributes = True

class MaintenanceCreate(BaseModel):
    owner_name: str
    date: str
    month: str
    year: int
    amount: float
    paid_by: int | None = None

class MaintenanceOut(MaintenanceCreate):
    id: int
    date: date
    month: str
    year: int
    amount: float
    paid_by: int | None = None
    owner_name: str
    created_by: int
    updated_by: int | None = None

    class Config:
        from_attributes = True