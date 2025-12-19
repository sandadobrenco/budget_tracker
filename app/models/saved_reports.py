from sqlalchemy import Column, String, Integer, DateTime, func, Index, Text
from app.db.session import Base

class SavedReports(Base):
    __tablename__ = "saved_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(255), nullable=False, index=True)
    applied_filters_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<SavedReport id={self.id} name={self.report_name!r}>"
    
    __table_args__ = (
        Index('ix_saved_reports_created_at', 'created_at'),
    )