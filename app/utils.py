from jose import jwt
import os
SECRET = os.getenv("JWT_SECRET", "changeme")
def create_token(user_id: str):
    return jwt.encode({"sub": user_id}, SECRET, algorithm="HS256")
def get_user_id_from_token(token: str):
    token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
    data = jwt.decode(token, SECRET, algorithms=["HS256"])
    return data.get("sub")
def create_admin_token(admin_username: str):
    payload = {"sub": admin_username, "is_admin": True}
    return jwt.encode(payload, SECRET, algorithm="HS256")
def is_admin_token(token: str) -> bool:
    token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        return bool(data.get("is_admin"))
    except Exception:
        return False
from datetime import datetime
from app.database import SessionLocal
from app.models import FixedDeposit, Wallet, Transaction

def close_matured_fds():
    db = SessionLocal()
    now = datetime.utcnow()

    fds = db.query(FixedDeposit).filter(
        FixedDeposit.is_closed == False,
        FixedDeposit.maturity_date <= now
    ).all()

    for fd in fds:
        interest = fd.amount * (fd.interest_rate / 100)
        total_amount = fd.amount + interest

        wallet = db.query(Wallet).filter(Wallet.user_id == fd.user_id).first()
        if wallet:
            wallet.balance += total_amount

            txn = Transaction(
                user_id=fd.user_id,
                amount=total_amount,
                transaction_type="CREDIT",
                description="FD matured and credited"
            )
            db.add(txn)

        fd.is_closed = True

    db.commit()
    db.close()
