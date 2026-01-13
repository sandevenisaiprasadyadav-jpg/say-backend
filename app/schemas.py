from pydantic import BaseModel
from typing import Optional
class UserCreate(BaseModel):
    phone: str
    name: Optional[str] = None
class TokenOut(BaseModel):
    access: str
class WalletAdd(BaseModel):
    amount: int
class FDCreate(BaseModel):
    amount: int
    tenure_days: int
class CreateOrderIn(BaseModel):
    amount: int
    currency: str = "INR"
