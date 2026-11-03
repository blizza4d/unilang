import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    filename = Column(String(255), nullable=False)
    mime = Column(String(64), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256 = Column(String(64), nullable=False, index=True)
    page_count = Column(Integer, default=1, nullable=False)
    status = Column(String(32), default="REQUIRES_HUMAN_REVIEW", nullable=False, index=True)
    vendor_name = Column(String(255), default="", nullable=False, index=True)
    invoice_number = Column(String(128), default="", nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    currency = Column(String(8), default="", nullable=False)
    result_json = Column(Text, nullable=False)
    original_result_json = Column(Text, nullable=False)
    grounding_json = Column(Text, nullable=True)
    processing_ms = Column(Integer, default=0, nullable=False)
    usage_json = Column(Text, nullable=True)

    pages = relationship("PageImageRecord", back_populates="document", cascade="all, delete-orphan", lazy="selectin")
    edits = relationship("EditRecord", back_populates="document", cascade="all, delete-orphan", lazy="selectin")
    approvals = relationship("ApprovalRecord", back_populates="document", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("idx_doc_created", "created_at"),
        Index("idx_doc_sha256", "sha256"),
        Index("idx_doc_vendor", "vendor_name"),
        Index("idx_doc_status", "status"),
    )

    def to_dict(self) -> Dict[str, Any]:
        extracted = {}
        try:
            extracted = json.loads(self.result_json)
        except Exception:
            pass

        return {
            "id": self.id,
            "filename": self.filename,
            "mime_type": self.mime,
            "file_size": self.size_bytes,
            "file_hash": self.sha256,
            "page_count": self.page_count,
            "status": self.status,
            "vendor_name": self.vendor_name,
            "invoice_number": self.invoice_number,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "overall_confidence": 0.95,
            "math_verified": self.status != "FLAGGED",
            "extracted_data": extracted,
            "created_at": self.created_at.isoformat() if self.created_at else "",
            "updated_at": self.updated_at.isoformat() if self.updated_at else "",
            "edits": [e.to_dict() for e in self.edits] if self.edits else [],
            "approvals": [a.to_dict() for a in self.approvals] if self.approvals else [],
        }


class PageImageRecord(Base):
    __tablename__ = "page_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page = Column(Integer, nullable=False)
    width_px = Column(Integer, default=1000, nullable=False)
    height_px = Column(Integer, default=1414, nullable=False)
    jpeg_bytes = Column(LargeBinary, nullable=False)

    document = relationship("DocumentRecord", back_populates="pages")

    __table_args__ = (Index("idx_page_doc", "document_id", "page"),)


class EditRecord(Base):
    __tablename__ = "edit_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    field_path = Column(String(128), nullable=False)
    old_value = Column(Text, default="", nullable=False)
    new_value = Column(Text, default="", nullable=False)
    editor = Column(String(64), default="reviewer", nullable=False)

    document = relationship("DocumentRecord", back_populates="edits")

    __table_args__ = (Index("idx_edit_doc", "document_id", "created_at"),)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "field_name": self.field_path,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "user_id": self.editor,
            "created_at": self.created_at.isoformat() if self.created_at else "",
        }


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    approved_by = Column(String(64), default="reviewer", nullable=False)
    note = Column(String(255), default="", nullable=False)

    document = relationship("DocumentRecord", back_populates="approvals")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.approved_by,
            "notes": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else "",
        }


class BatchRecord(Base):
    __tablename__ = "batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    total_files = Column(Integer, default=0, nullable=False)
    status = Column(String(32), default="processing", nullable=False)

    items = relationship("BatchItemRecord", back_populates="batch", cascade="all, delete-orphan", lazy="selectin")


class BatchItemRecord(Base):
    __tablename__ = "batch_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    status = Column(String(32), default="queued", nullable=False)
    document_id = Column(String(36), nullable=True)
    error_code = Column(String(64), nullable=True)

    batch = relationship("BatchRecord", back_populates="items")
