from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from datetime import datetime

from app.models.enums import MainTransactionType, Currency, Recurrence
from app.models.transactions import Transaction

class AbstractTransactionFactory(ABC):
    @abstractmethod
    def create_transaction(
        self,
        main_type: MainTransactionType,
        type_name: str,
        amount: Decimal,
        description: Optional[str] = None,
        currency: Currency = Currency.RON,
        date: Optional[datetime] = None,
        recurrence: Recurrence = Recurrence.NONE,
    ) -> Transaction:
        
        raise NotImplementedError
    
    def create_income(
        self, 
        type_name: str, 
        amount: Decimal, 
        description: Optional[str] = None,
        **kwargs
    ) -> Transaction:
        return self.create_transaction(
            main_type=MainTransactionType.INCOME,
            type_name=type_name,
            amount=amount,
            description=description,
            **kwargs
        )
    
    def create_expense(
        self,
        type_name: str,
        amount: Decimal,
        description: Optional[str] = None,
        **kwargs
    ) -> Transaction:
        return self.create_transaction(
            main_type=MainTransactionType.EXPENSE,
            type_name=type_name,
            amount=amount,
            description=description,
            **kwargs
        )
    
    def create_transfer(
        self,
        amount: Decimal,
        description: Optional[str] = None,
        **kwargs
    ) -> Transaction:
        return self.create_transaction(
            main_type=MainTransactionType.TRANSFER,
            type_name="Internal transfer",
            amount=amount,
            description=description,
            **kwargs
        )
    
    def create_recurring_transaction(
        self,
        main_type: MainTransactionType,
        type_name: str,
        amount: Decimal,
        recurrence: Recurrence,
        description: Optional[str] = None,
        **kwargs
    ) -> Transaction:
    
        if recurrence == Recurrence.NONE:
            raise ValueError('Recurrence must be specified for recurring transactions')
        
        return self.create_transaction(
            main_type=main_type,
            type_name=type_name,
            amount=amount,
            description=description,
            recurrence=recurrence,
            **kwargs
        )