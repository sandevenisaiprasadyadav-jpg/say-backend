from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Wallet, FixedDeposit, Transaction
from app.schemas import FDCreateRequest, FDResponse

router = APIRouter(prefix="/fds", tags=["Fixed Deposits"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{user_id}", response_model=FDResponse)
def create_fd(user_id: int, request: FDCreateRequest, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet or wallet.balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    wallet.balance -= request.amount

    maturity = datetime.utcnow() + timedelta(days=request.duration_days)

    fd = FixedDeposit(
        user_id=user_id,
        amount=request.amount,
        interest_rate=request.interest_rate,
        duration_days=request.duration_days,
        maturity_date=maturity
    )

    txn = Transaction(
        user_id=user_id,
        amount=request.amount,
        transaction_type="DEBIT",
        description="Fixed Deposit created"
    )

    db.add_all([fd, txn])
    db.commit()
    db.refresh(fd)

    return fd


@router.get("/{user_id}", response_model=list[FDResponse])
def list_fds(user_id: int, db: Session = Depends(get_db)):
    return db.query(FixedDeposit).filter(FixedDeposit.user_id == user_id).all()
