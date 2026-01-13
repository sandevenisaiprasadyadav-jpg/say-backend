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
@router.post("/")
def create_fd(payload: schemas.FDCreate, Authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_user(db, Authorization)
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == user.id).first()
    if not wallet or wallet.balance < payload.amount:
        raise HTTPException(400, "Insufficient balance")
    wallet.balance -= payload.amount
    fd = models.FixedDeposit(user_id=user.id, principal=payload.amount, tenure_days=payload.tenure_days)
    db.add(fd)
    tx = models.Transaction(user_id=user.id, type="fd_create", amount=payload.amount, status="completed")
    db.add(tx)
    db.commit()
    db.refresh(fd)
    return {"fd_id": fd.id, "principal": fd.principal, "status": fd.status}
@router.get("/")
def list_fds(Authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_user(db, Authorization)
    fds = db.query(models.FixedDeposit).filter(models.FixedDeposit.user_id == user.id).all()
    out = []
    for f in fds:
        out.append({"id": f.id, "principal": f.principal, "tenure_days": f.tenure_days, "status": f.status})
    return out
