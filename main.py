from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from fastapi import Response
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request
import models, schemas, database, expense
#from expense import get_current_user, require_secretary_or_treasurer
from expense import router as expense_router
import os
from fastapi import Cookie
from fastapi.responses import JSONResponse
models.Base.metadata.create_all(bind=database.engine)

# DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()
app.include_router(expense_router)

from fastapi import Cookie

def get_current_user(session: str = Cookie(None), db: Session = Depends(get_db)):
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(models.User).filter(models.User.username == session).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return user

# Serve static frontend
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Serve templates
if os.path.isdir("template"):
    app.mount("/template", StaticFiles(directory="template", html=True), name="static")

@app.get('/')
def read_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.get('/me')
def get_me(session: models.User = Depends(get_current_user)):
    return {"name": session.name, "role": session.role, "username": session.username, "userId": session.id}

@app.get('/users')
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"flat_number":user.flat_number} for user in users]

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

#class LoginRequest(BaseModel):
#    username: str
#    password: str

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

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, session: str = Depends(get_current_user)):
    # session is verified by get_current_user
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": session}
    )
    #with open("templates/dashboard.html", "r", encoding="utf-8") as f:
     #   html_content = f.read()
    #return HTMLResponse(content=html_content)

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("session")
    return {"message": "Logged out successfully"}

#@app.post("/expenses", response_model=schemas.ExpenseOut)
# def create_expense(
#     expense: schemas.ExpenseCreate,
#     username: str,  # Pass username from frontend or session
#     db: Session = Depends(get_db),
#     user: models.User = Depends(require_secretary_or_treasurer)
# ):
#     new_expense = models.Expense(
#         **expense.dict(),
#         created_by=user.id
#     )
#     db.add(new_expense)
#     db.commit()
#     db.refresh(new_expense)
#     return new_expense

# @app.get("/expenses", response_model=list[schemas.ExpenseOut])
# def list_expenses(db: Session = Depends(get_db)):
#     return db.query(models.Expense).all()