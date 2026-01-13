import os, requests, json, hmac, hashlib
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.utils import get_user_id_from_token
router = APIRouter()
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_API = "https://api.razorpay.com/v1/orders"
WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "demo_webhook_secret")
class CreateOrderIn(BaseModel):
    amount: int
    currency: str = "INR"
@router.post("/create-order")
def create_order(payload: CreateOrderIn, Authorization: str = Header(None), db: Session = Depends(get_db)):
    if not Authorization:
        raise HTTPException(401, "Missing Authorization")
    try:
        user_id = get_user_id_from_token(Authorization)
    except Exception:
        raise HTTPException(401, "Invalid token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    tx = models.Transaction(user_id=user.id, type="topup", amount=payload.amount, status="pending", metadata={})
    db.add(tx); db.commit(); db.refresh(tx)
    order_payload = {"amount": payload.amount * 100, "currency": payload.currency, "receipt": f"topup_{tx.id}", "payment_capture": 1}
    r = requests.post(RAZORPAY_API, auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET), json=order_payload, timeout=15)
    if r.status_code >= 300:
        raise HTTPException(502, "Razorpay order creation failed")
    resp = r.json()
    tx.metadata = {"razorpay_order_id": resp["id"]}
    db.commit()
    return {"order_id": resp["id"], "key_id": RAZORPAY_KEY_ID, "amount": resp["amount"], "currency": resp["currency"]}
@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    expected = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return {"status":"ignored", "reason":"invalid signature"}
    payload = json.loads(body)
    event = payload.get("event")
    if event != "payment.captured":
        return {"status":"ignored", "reason":"not a payment.captured event"}
    payment_entity = payload["payload"]["payment"]["entity"]
    razorpay_order_id = payment_entity["order_id"]
    payment_id = payment_entity["id"]
    amount = int(payment_entity["amount"])
    tx = db.query(models.Transaction).filter(models.Transaction.metadata["razorpay_order_id"].astext == razorpay_order_id).first()
    if not tx:
        return {"status":"ignored", "reason":"tx not found"}
    if tx.status == "completed":
        return {"status":"ok", "msg":"already processed"}
    tx.status = "completed"
    md = tx.metadata or {}
    md["razorpay_payment_id"] = payment_id
    tx.metadata = md
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == tx.user_id).first()
    if not wallet:
        wallet = models.Wallet(user_id=tx.user_id, balance=0)
        db.add(wallet)
    wallet.balance += amount // 100
    db.commit()
    return {"status":"ok", "credited": amount // 100}
