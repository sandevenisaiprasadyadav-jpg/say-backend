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
from pydantic import BaseModel
from datetime import datetime


class WalletResponse(BaseModel):
    balance: float

    class Config:
        from_attributes = True


class AddMoneyRequest(BaseModel):
    amount: float


class TransactionResponse(BaseModel):
    amount: float
    transaction_type: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
class FDCreateRequest(BaseModel):
    amount: float
    interest_rate: float
    duration_days: int


class FDResponse(BaseModel):
    id: int
    amount: float
    interest_rate: float
    duration_days: int
    maturity_date: datetime
    is_closed: bool

    class Config:
        from_attributes = True
