from sqlalchemy import Column, Numeric, Integer, Boolean, DateTime, func, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.enums import Currency, Recurrence

class Transaction(Base):
    __tablename__="transaction"
    
    id = Column(Integer, primary_key=True)
    transaction_type_id = Column(Integer, ForeignKey("transaction_types.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(Enum(Currency), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    is_recurring = Column(Boolean, nullable=False, default=False, index=True)
    recurrence = Column(Enum(Recurrence), nullable=False, default=Recurrence.NONE)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    transaction_type = relationship("TransactionTypes", back_populates="transactions")

    def __repr__(self) -> str:
        return (
            f"<Transaction id={self.id} amount={self.amount} "
            f"currency={self.currency} type_id={self.transaction_type_id}>"
        )