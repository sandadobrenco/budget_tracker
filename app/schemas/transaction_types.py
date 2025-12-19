from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import MainTransactionType

class TransactionTypeBase(BaseModel):
    main_type: MainTransactionType
    name: str
    description: Optional[str] = None

class TransactionTypeRead(TransactionTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)