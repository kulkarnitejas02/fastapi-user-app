from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from fastapi.logger import logger
from fastapi import Query
from schemas import ExpenseOut
from dependencies import get_current_user, get_db, get_current_user_by_username, get_current_user_id, require_secretary_or_treasurer, validate_user_exists

router = APIRouter(prefix="/expense_records", tags=["expense_records"])

@router.get("/", response_model=dict)  # Fixed: summery -> summary
def get_expense_summary(
    username: str =Query(...),
    year: int = Query(..., description="Year for summary (e.g., 2025)"),  # Made required
    month: str = Query(None, description="Optional: specific month for details"),   
    db: Session = Depends(get_db)
):
    user = get_current_user(username,db)

    # Only secretary/treasurer can access summary
    if user.role not in ["secretary", "treasurer"]:
        raise HTTPException(status_code=403, detail="Not authorized to view expense summary")
    
    #get all expense records for the year
    year_query = db.query(models.Expense).filter(models.Expense.year == year)
    yearly_records = year_query.all()

    #calculate yearly total
    yearly_total = sum(record.amount for record in yearly_records)

    #month-wise breakdown for the year
    monthly_summary = {}
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"] 
    for month_name in months:
        month_records = [r for r in yearly_records if r.month == month_name]
        monthly_summary[month_name] = {
            "count": len(month_records),
            "total": sum(r.amount for r in month_records)
        }

    #if specific month requested, get detailed records
    detailed_records = []
    month_total = 0
    if month:
        month_records = db.query(models.Expense).filter(
            models.Expense.year == year,
            models.Expense.month == month
        ).all()
        detailed_records = [ExpenseOut.model_validate(r).model_dump() for r in month_records]
        month_total = sum(record.amount for record in month_records)
    else:
        detailed_records = []   

    return {
        "year": year,   
        "yearly_total": yearly_total,
        "yearly_count": len(yearly_records),
        "monthly_summary": monthly_summary,
        "selected_month": month,
        "month_total": month_total,
        "month_records": detailed_records
    }