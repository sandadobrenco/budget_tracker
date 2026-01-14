from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session
from app.core.strategies.base_strategy import AbstractReportStrategy
from app.db.session import SessionLocal
from app.models.transactions import Transaction   
from app.models.transaction_types import TransactionTypes
from app.models.saved_reports import SavedReports   

from app.schemas.reports import (
    ReportFilters,
    SavedReportAuditPayload,
)
from app.schemas.saved_reports import SavedReportRead 

class ReportService:
    def __init__(self, session: Optional[Session] = None) -> None:
        self._external_session = session
    
    def _get_session(self) -> Session:
        return self._external_session or SessionLocal()
    
    def _build_query(self, session: Session, filters: ReportFilters):
        q = session.query(Transaction).join(Transaction.transaction_type)
        
        if filters.start_date:
            q = q.filter(Transaction.date >= filters.start_date)
        if filters.end_date:
            q = q.filter(Transaction.date <= filters.end_date)
        
        if filters.main_type is not None:
            q = q.filter(TransactionTypes.main_type == filters.main_type)
        
        if filters.category_ids:
            q = q.filter(Transaction.transaction_type_id.in_(filters.category_ids))
            
        if filters.min_amount is not None:
            q = q.filter(Transaction.amount >= filters.min_amount)
        if filters.max_amount is not None:
            q = q.filter(Transaction.amount <= filters.max_amount)
        
        if filters.recurring:
            q = q.filter(Transaction.is_recurring.is_(True))
            
        if filters.currency is not None:
            q = q.filter(Transaction.currency == filters.currency)
            
        q = q.order_by(Transaction.date.asc())
        
        return q
    
    def _load_transactions(
        self,
        session: Session,
        filters: ReportFilters,
    ) -> List[Transaction]:
        q = self._build_query(session, filters)
        return q.all()

    def generate_report(
        self,
        strategy: AbstractReportStrategy,
        filters: ReportFilters,
        report_name: str = "Budget report",
        output_format: str = "cli",
        save_audit: bool = True,
    ):
        session = self._get_session()
        close = self._external_session is None
        
        try:
            transactions = self._load_transactions(session, filters)
            
            report = strategy.generate(transactions, filters)
            
            if save_audit:
                output_path = getattr(report, "file_path", None)
                 
                audit_payload = SavedReportAuditPayload(
                    strategy_name=type(strategy).__name__,
                    filters=filters,
                    generated_at = datetime.now(timezone.utc),
                    output_format=output_format,
                    output_path=output_path,
                )
                
                saved = SavedReports(
                    report_name=report_name,
                    applied_filters_json=audit_payload.model_dump_json(),
                )
                
                session.add(saved)
                session.commit()
                
            return report
        
        finally:
            if close:
                session.close()
        
    def list_saved_reports(self) -> List[SavedReportRead]:
        session = self._get_session()
        close = self._external_session is None
        
        try:
            q = session.query(SavedReports).order_by(SavedReports.created_at.desc())
            results = q.all()
            return [SavedReportRead.model_validate(sr) for sr in results]
        finally:
            if close:
                session.close()
                 
                 