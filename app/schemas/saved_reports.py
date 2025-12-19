from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict

class SavedReportBase(BaseModel):
    report_name: str
    applied_filters: Dict[str, Any]
    
class SavedReportRead(SavedReportBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


