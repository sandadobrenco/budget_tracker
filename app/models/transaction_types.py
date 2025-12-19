from sqlalchemy import Column, String, Text, Enum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

from app.db.session import Base
from app.models.enums import MainTransactionType

class TransactionTypes(Base):
    __tablename__ = "transaction_types"

    id = Column(Integer, primary_key=True)
    main_type = Column(Enum(MainTransactionType), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    transactions = relationship("Transaction", back_populates="transaction_type", cascade="all, delete-orphan", passive_deletes=True)
    def __repr__(self) -> str:
        return f"<TransactionTypes(id={self.id}, main_type={self.main_type}, name={self.name!r})>"
    
    __table_args__ = (
        UniqueConstraint('main_type', 'name', name='uix_main_type_name'),   
    )