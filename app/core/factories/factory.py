from typing import Optional
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.factories.base_factory import AbstractTransactionFactory
from app.models.transactions import Transaction
from app.models.transaction_types import TransactionTypes
from app.models.enums import MainTransactionType, Currency, Recurrence

class DatabaseTransactionFactory(AbstractTransactionFactory):
    
    def __init__(self, session: Session):
        self._session=session
        self._type_cache = {}
    
    def create_transaction(
        self,
        main_type: MainTransactionType,
        type_name: str,
        amount: Decimal,
        description: Optional[str] = None,
        currency: Currency = Currency.RON,
        date: Optional[datetime] = None,
        recurrence: Recurrence = Recurrence.NONE
    ) -> Transaction:
        
        transaction_type = self._get_transaction_type(main_type, type_name)
        validated_amount = self._validate_amount(amount, main_type)
        transaction_date = date or datetime.now()
        is_recurring = recurrence != Recurrence.NONE
        transaction = Transaction(
            transaction_type_id=transaction_type.id,
            amount=validated_amount,
            currency=currency,
            date=transaction_date,
            is_recurring=is_recurring,
            recurrence=recurrence,
            description=description
        )
        
        self._session.add(transaction)
        
        return transaction
     
    def _get_transaction_type(
        self,
        main_type: MainTransactionType,
        type_name: str
    ) -> TransactionTypes:
        
        cache_key = (main_type, type_name)
        if cache_key in self._type_cache:
            return self._type_cache[cache_key]
        
        transaction_type = self._session.query(TransactionTypes).filter_by(
            main_type=main_type,
            name=type_name
        ).first()
        
        if not transaction_type:
            raise ValueError(
                f"Transaction type not found: {main_type.value} - {type_name}. "
            )
        
        self._type_cache[cache_key] = transaction_type
        
        return transaction_type
    
    def _validate_amount(
        self,
        amount: Decimal,
        main_type: MainTransactionType
    ) -> Decimal:
        
        if amount <=0:
            raise ValueError(f"Amount must be positive, got: {amount}")
        
        return round(amount, 2)
    
    def get_available_types(
        self, 
        main_type: Optional[MainTransactionType] = None
    ) -> list[TransactionTypes]:
        
        query = self._session.query(TransactionTypes)
        
        if main_type:
            query = query.filter_by(main_type=main_type)
        
        return query.all()
    
    def clear_cache(self):
        self._type_cache.clear()
    