from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi import Cookie
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from fastapi import Response
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
import models, schemas, database, expense
from expense import router as expense_router
from income import router as income_router
from income_records import router as income_records_router
from expense_records import router as expense_records_router
from dependencies import get_db, get_current_user
import os
from fastapi.responses import JSONResponse
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.include_router(expense_router)
app.include_router(income_router)
app.include_router(income_records_router)
app.include_router(expense_records_router)

# Serve static frontend
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Serve template files if exists
if os.path.isdir("template"):
    app.mount("/template", StaticFiles(directory="template", html=True), name="static")

@app.get('/')
def read_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.get("/me")
def get_me(session: models.User = Depends(get_current_user)):
    return {"name": session.name,
             "role": session.role, 
             "username":session.username, 
             "userid": session.id, 
             "flat_number": session.flat_number,
}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"id": user.id, "flat_number": user.flat_number} for user in users]

@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        print("Received user data:", user.dict())
        existing_user = db.query(models.User).filter(models.User.username == user.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        print(f"Error during registration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login(login_req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == login_req.username,
        models.User.password == login_req.password
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    #return {"message": f"Welcome {user.name} {user.role}!", "name": user.name, "Role": user.role}
    response = JSONResponse(
        content={
            "message": f"Welcome {user.name}!",
            "name": user.name,
            "role": user.role,
        }
    )
    response.set_cookie(
        key="session", 
        value=user.username, 
        httponly=True,
        max_age=1800  # 30 minutes
    )
    return response

templates = Jinja2Templates(directory="templates")

@app.get("/dashboard")
def dashboard(request: Request, session: str = Depends(get_current_user)):
    # session is verified by get_current_user
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": session}
    )

@app.get("/dashboard/expenses", response_class=HTMLResponse)
def show_expenses(request: Request, session: str = Depends(get_current_user)):
    # session is verified by get_current_user
    return templates.TemplateResponse(
        "expense.html",
        {"request": request, "user": session}
    )

@app.get("/dashboard/income", response_class=HTMLResponse)
def show_income(request: Request, session: str = Depends(get_current_user)):
    # session is verified by get_current_user
    return templates.TemplateResponse(
        "income.html",
        {"request": request, "user": session}
    )

@app.get("/dashboard/income_records", response_class=HTMLResponse)
def show_income_records(request: Request, session: str = Depends(get_current_user)):
    # session is verified by get_current_user
    return templates.TemplateResponse(
        "income_records.html",
        {"request": request, "user": session}
    )

@app.get("/dashboard/expense_records", response_class=HTMLResponse)
def show_expense_records(request: Request, session: str = Depends(get_current_user)):
    # session is verified by get_current_user
    return templates.TemplateResponse(
        "expense_records.html",
        {"request": request, "user": session}
    )

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("session")
    return {"message": "Logged out successfully"}

@app.put("/reset-password")
def reset_password(reset_req: dict, db: Session = Depends(get_db)):
    username = reset_req.get("username")
    contact_id = reset_req.get("contact_id") 
    new_password = reset_req.get("new_password")
    
    if not all([username, contact_id, new_password]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Find user by username and contact_id to verify identity
    user = db.query(models.User).filter(
        models.User.username == username,
        models.User.contact_id == contact_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found or invalid contact ID")
    
    # Update the password
    try:
        user.password = new_password
        db.commit()
        return {"message": "Password reset successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to reset password")


