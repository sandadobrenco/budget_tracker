from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field
from app.schemas.reports import SavedReportAuditPayload

class SavedReportBase(BaseModel):
    report_name: str
    applied_filters_json: str

class SavedReportCreate(SavedReportBase):
    pass
    
class SavedReportRead(SavedReportBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def applied_filters(self) -> SavedReportAuditPayload:
        return SavedReportAuditPayload.model_validate_json(self.applied_filters_json)

