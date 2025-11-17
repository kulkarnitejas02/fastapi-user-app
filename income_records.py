from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from fastapi.logger import logger
from fastapi import Query
from schemas import MaintenanceOut
from dependencies import get_current_user, get_db, get_current_user_by_username, get_current_user_id, require_secretary_or_treasurer, validate_user_exists

router = APIRouter(prefix="/income_records", tags=["income_records"])

@router.get("/", response_model=dict)  # Fixed: summery -> summary
def get_income_summary(  # Fixed: summery -> summary
    username: str = Query(...),
    year: int = Query(..., description="Year for summary (e.g., 2025)"),  # Made required
    month: str = Query(None, description="Optional: specific month for details"),
    db: Session = Depends(get_db)
):
    user = get_current_user(username, db)

    # Only secretary/treasurer can access summary
    if user.role not in ["secretary", "treasurer"]:
        raise HTTPException(status_code=403, detail="Not authorized to view income summary")

    # Get all maintenance records for the year
    year_query = db.query(models.Maintenance).filter(models.Maintenance.year == year)
    yearly_records = year_query.all()
    
    # Calculate yearly total
    yearly_total = sum(record.amount for record in yearly_records)

    # Month-wise breakdown for the year
    monthly_summary = {}
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    for month_name in months:
        month_records = [r for r in yearly_records if r.month == month_name]
        monthly_summary[month_name] = {
            "count": len(month_records),
            "total": sum(r.amount for r in month_records)
        }
    
    # If specific month requested, get detailed records
    detailed_records = []
    month_total = 0
    if month:
        month_records = db.query(models.Maintenance).filter(
            models.Maintenance.year == year,
            models.Maintenance.month == month
        ).all()
        #detailed_records = month_records
        #month_total = sum(record.amount for record in month_records)
        detailed_records = [MaintenanceOut.model_validate(r).model_dump() for r in month_records]
        month_total = sum(record.amount for record in month_records)
    else:
        detailed_records = []
        
    # Fixed: Return statement moved outside the if block
    return {
        "year": year,
        "yearly_total": yearly_total,
        "yearly_count": len(yearly_records),
        "monthly_summary": monthly_summary,
        "selected_month": month,
        "month_total": month_total,
        "month_records": detailed_records
    }
