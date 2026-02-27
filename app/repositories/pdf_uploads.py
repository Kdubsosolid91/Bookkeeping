from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.core import PdfUpload


class PdfUploadRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, upload_id: UUID) -> Optional[PdfUpload]:
        return self.db.get(PdfUpload, upload_id)

    def create(self, upload: PdfUpload) -> PdfUpload:
        self.db.add(upload)
        self.db.commit()
        self.db.refresh(upload)
        return upload

    def update(self, upload: PdfUpload) -> PdfUpload:
        self.db.add(upload)
        self.db.commit()
        self.db.refresh(upload)
        return upload
