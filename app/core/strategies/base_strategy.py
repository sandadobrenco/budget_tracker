from abc import ABC, abstractmethod
from collections.abc import Iterable

from pydantic import BaseModel

from app.models.transactions import Transaction
from app.schemas.reports import ReportFilters

class AbstractReportStrategy(ABC):
    
    @abstractmethod
    def generate(
        self,
        transactions: Iterable[Transaction],
        filters: ReportFilters,
    ) -> BaseModel:
        raise NotImplementedError
