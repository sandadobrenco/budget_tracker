from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from app.models.enums import Currency, Recurrence

class TransactionBase(BaseModel):
    transaction_type_id: int
    amount: Decimal
    currency: Currency = Currency.RON
    date: datetime
    is_recurring: bool = False
    recurrence: Recurrence = Recurrence.NONE
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)