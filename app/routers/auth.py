from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils import create_token
router = APIRouter()
@router.post("/login")
def login(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.phone == payload.phone).first()
    if not user:
        user = models.User(phone=payload.phone, name=payload.name)
        db.add(user); db.commit(); db.refresh(user)
        wallet = models.Wallet(user_id=user.id, balance=0)
        db.add(wallet); db.commit()
    token = create_token(user.id)
    return {"access": token}
