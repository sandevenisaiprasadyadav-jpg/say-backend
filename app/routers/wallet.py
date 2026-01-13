from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Wallet, Transaction
from app.schemas import WalletResponse, AddMoneyRequest

router = APIRouter(prefix="/wallet", tags=["Wallet"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}", response_model=WalletResponse)
def get_wallet(user_id: int, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0.0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet


@router.post("/{user_id}/add")
def add_money(user_id: int, request: AddMoneyRequest, db: Session = Depends(get_db)):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0.0)
        db.add(wallet)

    wallet.balance += request.amount

    transaction = Transaction(
        user_id=user_id,
        amount=request.amount,
        transaction_type="CREDIT",
        description="Money added to wallet"
    )

    db.add(transaction)
    db.commit()

    return {"message": "Money added successfully", "balance": wallet.balance}
