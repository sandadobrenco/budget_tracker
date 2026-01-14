from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.factories.factory import DatabaseTransactionFactory
from app.models.transactions import Transaction
from app.models.transaction_types import TransactionTypes
from app.schemas.transactions import TransactionCreate, TransactionRead


class TransactionService:
    def __init__(self, session: Session | None = None) -> None:
        self._external_session = session

    def _get_session(self) -> Session:
        return self._external_session or SessionLocal()

    def add_transaction(self, data: TransactionCreate) -> TransactionRead:
        session = self._get_session()
        close = self._external_session is None

        try:
            tx_type = session.get(TransactionTypes, data.transaction_type_id)
            if tx_type is None:
                raise ValueError(f"Transaction type with the id={data.transaction_type_id} does not exist")
            
            factory = DatabaseTransactionFactory(session)
            tx = factory.create_transaction(
                main_type=tx_type.main_type,        
                type_name=tx_type.name,         
                amount=data.amount,
                description=data.description,
                currency=data.currency,
                date=data.date,
                recurrence=data.recurrence,
            )
            session.commit()
            session.refresh(tx)
            return TransactionRead.model_validate(tx)
        finally:
            if close:
                session.close()

    def list_transactions(self) -> List[TransactionRead]:
        session = self._get_session()
        close = self._external_session is None

        try:
            q = session.query(Transaction).order_by(Transaction.date.desc())
            return [TransactionRead.model_validate(t) for t in q.all()]
        finally:
            if close:
                session.close()
    
    def get_transaction(self, tx_id: int) -> Optional[TransactionRead]:
        session = self._get_session()
        close = self._external_session is None
        
        try:
            tx = session.get(Transaction, tx_id)
            if tx is None:
                return None
            return TransactionRead.model_validate(tx)
        finally:
            if close:
                session.close()
    
    def delete_transaction(self, tx_id: int) -> bool:
        session = self._get_session()
        close = self._external_session is None
        
        try:
            tx = session.get(Transaction, tx_id)
            if tx is None:
                return False
            
            session.delete(tx)
            session.commit()
            return True
        finally:
            if close:
                session.close()
    
    def update_transaction(self, tx_id: int, **updates: Any,) -> TransactionRead:
        allowed_fields = {
            "transaction_type_id",
            "amount",
            "currency",
            "date",
            "is_recurring",
            "recurrence",
            "description",
        }
        
        clean_updates: Dict[str, Any] = {
            k: v for k, v in updates.items() if k in allowed_fields and v is not None
        }
        
        if not clean_updates:
            raise ValueError("No valid fields to update")
        
        session = self._get_session()
        close = self._external_session is None
        
        try:
            tx = session.get(Transaction, tx_id)
            if tx is None:
                raise ValueError(f"Transaction with id={tx_id} does not exist")
            
            for field, value in clean_updates.items():
                setattr(tx, field, value)

            session.commit()
            session.refresh(tx)
            return TransactionRead.model_validate(tx)
        finally:
            if close:
                session.close()
