from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(username: str, db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.username == username).first()

def require_secretary_or_treasurer(user: models.User = Depends(get_current_user)):
    if user.role not in ["secretary", "treasurer"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return user

@router.post("/expenses", response_model=schemas.ExpenseOut)
def create_expense(
    expense: schemas.ExpenseCreate,
    username: str,  # Pass username from frontend or session
    db: Session = Depends(get_db),
    user: models.User = Depends(require_secretary_or_treasurer)
):
    new_expense = models.Expense(
        date=expense.date,
        month=expense.month,
        description=expense.description,
        amount=expense.amount,
        paid_by=expense.paid_by,
        created_by=1  # or user.id if you want
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get("/expenses", response_model=list[schemas.ExpenseOut])
def list_expenses(db: Session = Depends(get_db)):
    return db.query(models.Expense).all()