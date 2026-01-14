from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Union

from pydantic import BaseModel

from app.models.enums import MainTransactionType, Currency

class ReportFilters(BaseModel):
    start_date: datetime
    end_date: datetime
    main_type: Optional[MainTransactionType] = None
    category_ids: Optional[List[int]] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    recurring: bool = False
    currency: Optional[Currency] = None
    
class BaseReport(BaseModel):
    start_date: datetime
    end_date: datetime
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    
class SimpleReport(BaseReport):
    transaction_count: int

class CategoryBreakdownItem(BaseModel):
    category_id: int
    category_name: str
    main_type: MainTransactionType
    total_amount: Decimal
    transaction_count: int

class DetailedReport(BaseReport):
    breakdown: List[CategoryBreakdownItem]

class PDFReport(BaseModel):
    file_path: str
    base_report: Union[SimpleReport, DetailedReport]
    generated_at: datetime

class SavedReportAuditPayload(BaseModel):
    strategy_name: str
    filters: ReportFilters
    generated_at: datetime
    output_format: str = "cli"
    output_path: Optional[str] = None