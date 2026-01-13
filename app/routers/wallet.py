from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils import get_user_id_from_token
router = APIRouter()
def get_user(db: Session, Authorization: str):
    if not Authorization:
        raise HTTPException(401, "Missing Authorization")
    try:
        user_id = get_user_id_from_token(Authorization)
    except Exception:
        raise HTTPException(401, "Invalid token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user
@router.get("/")
def get_wallet(Authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_user(db, Authorization)
    w = db.query(models.Wallet).filter(models.Wallet.user_id == user.id).first()
    return {"balance": w.balance}
