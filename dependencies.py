from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import database

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_by_username(username: str, db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.username == username).first()

def get_current_user_id(username: str, db: Session = Depends(get_db)):
    user = get_current_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id

def require_secretary_or_treasurer(username: str, db: Session = Depends(get_db)):
    user = get_current_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role not in ["secretary", "treasurer"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return user

def validate_user_exists(username: str, db: Session = Depends(get_db)):
    user = get_current_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Session-based authentication (for cookie-based login)
def get_current_user(session: str = Cookie(None), db: Session = Depends(get_db)):
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(models.User).filter(models.User.username == session).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return user
