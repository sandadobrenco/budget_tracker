from collections import defaultdict
from collections.abc import Iterable
from decimal import Decimal
from typing import Dict, List

from app.core.strategies.base_strategy import AbstractReportStrategy
from app.models.enums import MainTransactionType
from app.models.transactions import Transaction
from app.schemas.reports import (
    ReportFilters,
    DetailedReport,
    CategoryBreakdownItem,
)

class DetailedReportStrategy(AbstractReportStrategy):
    def generate(
        self,
        transactions: Iterable[Transaction],
        filters: ReportFilters,
    ) -> DetailedReport:
        total_income = Decimal("0")
        total_expense = Decimal("0")

        breakdown_map: Dict[int, Dict] = defaultdict(
            lambda: {
                "category_name": "",
                "main_type": None,
                "total_amount": Decimal("0"),
                "count": 0,
            }
        )

        for tx in transactions:
            tx_type = tx.transaction_type
            main_type = tx_type.main_type

            if main_type == MainTransactionType.INCOME:
                total_income += tx.amount
            elif main_type == MainTransactionType.EXPENSE:
                total_expense += tx.amount

            entry = breakdown_map[tx_type.id]
            entry["category_name"] = tx_type.name
            entry["main_type"] = main_type
            entry["total_amount"] += tx.amount
            entry["count"] += 1

        balance = total_income - total_expense

        breakdown_items: List[CategoryBreakdownItem] = [
            CategoryBreakdownItem(
                category_id=cat_id,
                category_name=data["category_name"],
                main_type=data["main_type"],
                total_amount=data["total_amount"],
                transaction_count=data["count"],
            )
            for cat_id, data in breakdown_map.items()
        ]

        breakdown_items.sort(key=lambda item: item.total_amount, reverse=True)

        return DetailedReport(
            start_date=filters.start_date,
            end_date=filters.end_date,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            breakdown=breakdown_items,
        )