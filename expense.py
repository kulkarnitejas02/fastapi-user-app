from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database
from datetime import datetime

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(username: str, db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.username == username).first()

def get_current_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id

def require_secretary_or_treasurer(user: models.User = Depends(get_current_user)):
    if user.role not in ["secretary", "treasurer"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return user

@router.post("/expenses", response_model=schemas.ExpenseOut)
def create_expense(
    expense: schemas.ExpenseCreate,
    #username: str,  # Pass username from frontend or session
    db: Session = Depends(get_db),
    user: models.User = Depends(require_secretary_or_treasurer)
):
    print("Incomming expense data:", expense)
    from datetime import datetime
        # Convert string date to Python date object if needed
    if isinstance(expense.date, str):
        expense_date = datetime.strptime(expense.date, "%Y-%m-%d").date()
    else:
        expense_date = expense.date
    new_expense = models.Expense(
        date=expense_date,
        month=expense.month,
        expense_name=expense.expense_name,
        description=expense.description,
        amount=expense.amount,
        paid_by=expense.paid_by,
        #created_by=user.id  # or user.id if you want
    )
    print("Creating expense:", new_expense)
    try:
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)
        return new_expense
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create expense: {str(e)}")

@router.get("/expenses", response_model=list[schemas.ExpenseOut])
def list_expenses(db: Session = Depends(get_db)):
    return db.query(models.Expense).all()