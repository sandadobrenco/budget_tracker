from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.transaction_types import TransactionTypes
from app.models.enums import MainTransactionType


class TransactionTypeService:
    def __init__(self, session: Session | None = None) -> None:
        self._external_session = session

    def _get_session(self) -> Session:
        return self._external_session or SessionLocal()

    def list_types(
        self,
        main_type: Optional[MainTransactionType] = None,
    ) -> List[TransactionTypes]:
        session = self._get_session()
        close = self._external_session is None

        try:
            q = session.query(TransactionTypes)
            if main_type:
                q = q.filter_by(main_type=main_type)
            return q.order_by(TransactionTypes.main_type, TransactionTypes.name).all()
        finally:
            if close:
                session.close()
