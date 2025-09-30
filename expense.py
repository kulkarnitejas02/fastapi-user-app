from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from fastapi.logger import logger
from fastapi import Query
from dependencies import get_db, get_current_user_by_username, get_current_user_id, require_secretary_or_treasurer, validate_user_exists

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("/", response_model=schemas.ExpenseOut)
def create_expense(
    expense: schemas.ExpenseCreate,
    username: str = Query(...),  # Require username as query param
    db: Session = Depends(get_db)
):
    user = validate_user_exists(username, db)
    # Allow only secretary, treasurer, and member roles to create expenses
    if user.role not in ["secretary", "treasurer", "member"]:
        raise HTTPException(status_code=403, detail="Not authorized - invalid role")
    print("Received expense data from frontend:", expense.dict())
    new_expense = models.Expense(
        date=expense.date,
        month=expense.month,
        expense_name=expense.expense_name,
        description=expense.description,
        amount=expense.amount,
        paid_by=expense.paid_by,
        created_by=expense.created_by  # Set created_by to current user's ID
    )
    print("Incoming expense data:", new_expense)
    try:
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)
        return new_expense
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding expense to DB: {e}")
        raise HTTPException(status_code=500, detail="Failed to add expense to database")

@router.get("/", response_model=list[schemas.ExpenseOut])
def list_expenses(username: str = Query(...), db: Session = Depends(get_db)):
    user = validate_user_exists(username, db)
    # Allow only secretary, treasurer, and member roles to view expenses
    if user.role not in ["secretary", "treasurer", "member"]:
        raise HTTPException(status_code=403, detail="Not authorized - invalid role")
    return db.query(models.Expense).all()
