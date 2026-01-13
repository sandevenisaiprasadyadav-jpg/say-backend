from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Wallet, Transaction
from app.schemas import AddMoneyRequest

router = APIRouter(prefix="/payments", tags=["Payments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{user_id}/pay")
def make_payment(user_id: int, request: AddMoneyRequest, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet or wallet.balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    wallet.balance -= request.amount

    transaction = Transaction(
        user_id=user_id,
        amount=request.amount,
        transaction_type="DEBIT",
        description="Payment transaction"
    )

    db.add(transaction)
    db.commit()

    return {"message": "Payment successful", "remaining_balance": wallet.balance}
