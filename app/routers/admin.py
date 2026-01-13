from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os, hmac
from app.database import get_db
from app import models
from app.utils import create_admin_token, is_admin_token
router = APIRouter()
class AdminLoginIn(BaseModel):
    username: str
    password: str
def require_admin(Authorization: str = Header(None)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not is_admin_token(Authorization):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return True
@router.post("/login")
def admin_login(payload: AdminLoginIn):
    admin_user = os.getenv("ADMIN_USERNAME")
    admin_pass = os.getenv("ADMIN_PASSWORD")
    if not admin_user or not admin_pass:
        raise HTTPException(status_code=500, detail="Admin credentials not configured on server")
    if not (hmac.compare_digest(payload.username, admin_user) and hmac.compare_digest(payload.password, admin_pass)):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    token = create_admin_token(payload.username)
    return {"access": token, "token_type": "bearer"}
@router.get("/users")
def list_users(_admin = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    out = []
    for u in users:
        w = db.query(models.Wallet).filter(models.Wallet.user_id == u.id).first()
        out.append({
            "id": u.id,
            "phone": u.phone,
            "name": u.name,
            "balance": w.balance if w else 0,
            "created_at": u.created_at.isoformat() if u.created_at else None
        })
    return out
@router.get("/fds")
def list_fds(_admin = Depends(require_admin), db: Session = Depends(get_db)):
    fds = db.query(models.FixedDeposit).all()
    out = []
    for f in fds:
        out.append({
            "id": f.id,
            "user_id": f.user_id,
            "principal": f.principal,
            "tenure_days": f.tenure_days,
            "status": f.status,
            "start_date": f.start_date.isoformat() if f.start_date else None,
            "created_at": f.created_at.isoformat() if f.created_at else None
        })
    return out
@router.get("/transactions")
def list_transactions(_admin = Depends(require_admin), db: Session = Depends(get_db)):
    txs = db.query(models.Transaction).order_by(models.Transaction.created_at.desc()).limit(1000).all()
    out = []
    for t in txs:
        out.append({
            "id": t.id,
            "user_id": t.user_id,
            "type": t.type,
            "amount": t.amount,
            "status": t.status,
            "metadata": t.metadata,
            "created_at": t.created_at.isoformat() if t.created_at else None
        })
    return out
