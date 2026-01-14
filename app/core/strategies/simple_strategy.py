from collections.abc import Iterable
from decimal import Decimal

from app.core.strategies.base_strategy import AbstractReportStrategy
from app.models.enums import MainTransactionType
from app.models.transactions import Transaction
from app.schemas.reports import ReportFilters, SimpleReport

class SimpleReportStrategy(AbstractReportStrategy):
    
    def generate(
        self,
        transactions: Iterable[Transaction],
        filters: ReportFilters,
    ) -> SimpleReport:
        total_income = Decimal("0")
        total_expense = Decimal("0")
        transaction_count = 0

        for tx in transactions:
            transaction_count += 1

            main_type = tx.transaction_type.main_type

            if main_type == MainTransactionType.INCOME:
                total_income += tx.amount
            elif main_type == MainTransactionType.EXPENSE:
                total_expense += tx.amount
                
        balance = total_income - total_expense
        
        return SimpleReport(
            start_date=filters.start_date,
            end_date=filters.end_date,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            transaction_count=transaction_count,
        )