import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
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


class TenantRecord(Base):
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False)
    slug = Column(String(64), nullable=False, unique=True, index=True)
    plan = Column(String(32), default="enterprise", nullable=False)
    settings_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    users = relationship("UserRecord", back_populates="tenant", cascade="all, delete-orphan")
    documents = relationship("DocumentRecord", back_populates="tenant", cascade="all, delete-orphan")


class UserRecord(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), default="analyst", nullable=False)  # admin, reviewer, analyst, auditor
    totp_secret = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    tenant = relationship("TenantRecord", back_populates="users")


class ApiKeyRecord(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    key_hash = Column(String(128), nullable=False, index=True)
    prefix = Column(String(16), nullable=False)
    scopes_json = Column(Text, default="[]", nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), default="default", nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    filename = Column(String(255), nullable=False)
    mime = Column(String(64), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256 = Column(String(64), nullable=False, index=True)
    page_count = Column(Integer, default=1, nullable=False)
    doc_type = Column(String(64), default="invoice", nullable=False, index=True)
    status = Column(String(32), default="REQUIRES_HUMAN_REVIEW", nullable=False, index=True)
    vendor_name = Column(String(255), default="", nullable=False, index=True)
    invoice_number = Column(String(128), default="", nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    currency = Column(String(8), default="", nullable=False)
    storage_key = Column(String(255), nullable=True)
    result_json = Column(Text, nullable=False)
    original_result_json = Column(Text, nullable=False)
    grounding_json = Column(Text, nullable=True)
    processing_ms = Column(Integer, default=0, nullable=False)
    usage_json = Column(Text, nullable=True)

    tenant = relationship("TenantRecord", back_populates="documents")
    pages = relationship("PageImageRecord", back_populates="document", cascade="all, delete-orphan", lazy="selectin")
    edits = relationship("EditRecord", back_populates="document", cascade="all, delete-orphan", lazy="selectin")
    approvals = relationship("ApprovalRecord", back_populates="document", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("idx_doc_created", "created_at"),
        Index("idx_doc_sha256", "sha256"),
        Index("idx_doc_vendor", "vendor_name"),
        Index("idx_doc_status", "status"),
        Index("idx_doc_tenant", "tenant_id"),
        Index("idx_doc_type", "doc_type"),
    )

    def to_dict(self) -> Dict[str, Any]:
        extracted = {}
        try:
            extracted = json.loads(self.result_json)
        except Exception:
            pass

        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "filename": self.filename,
            "mime_type": self.mime,
            "file_size": self.size_bytes,
            "file_hash": self.sha256,
            "page_count": self.page_count,
            "doc_type": self.doc_type,
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
    storage_key = Column(String(255), nullable=True)
    jpeg_bytes = Column(LargeBinary, nullable=True)

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
    tenant_id = Column(String(36), default="default", nullable=False, index=True)
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


class EvalRunRecord(Base):
    __tablename__ = "eval_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    dataset_size = Column(Integer, nullable=False)
    mean_field_accuracy = Column(Float, nullable=False)
    mean_line_item_f1 = Column(Float, nullable=False)
    mean_hallucination_score = Column(Float, nullable=False)
    mean_latency_ms = Column(Float, nullable=False)
    math_pass_rate = Column(Float, nullable=False)
    model_name = Column(String(64), nullable=False)
    results_json = Column(Text, nullable=False)


class CustomSchemaRecord(Base):
    __tablename__ = "custom_schemas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    doc_type = Column(String(64), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(32), default="draft", nullable=False)  # draft, published, archived
    schema_definition = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class VendorRecord(Base):
    __tablename__ = "vendors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    canonical_name = Column(String(255), nullable=False)
    tax_id = Column(String(64), default="", nullable=False)
    aliases_json = Column(Text, default="[]", nullable=False)
    default_currency = Column(String(8), default="USD", nullable=False)
    bank_details_json = Column(Text, default="{}", nullable=False)
    risk_score = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class PurchaseOrderRecord(Base):
    __tablename__ = "purchase_orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    po_number = Column(String(128), nullable=False)
    vendor_id = Column(String(36), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True)
    order_date = Column(String(32), default="", nullable=False)
    delivery_date = Column(String(32), default="", nullable=False)
    currency = Column(String(8), default="USD", nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    line_items_json = Column(Text, default="[]", nullable=False)
    status = Column(String(32), default="open", nullable=False)  # open, partially_fulfilled, fulfilled, closed
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class WorkflowRecord(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    trigger_rules_json = Column(Text, default="{}", nullable=False)
    steps_json = Column(Text, default="[]", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class WorkflowRunRecord(Base):
    __tablename__ = "workflow_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(32), default="pending", nullable=False)  # pending, in_progress, approved, rejected
    current_step_index = Column(Integer, default=0, nullable=False)
    assigned_to = Column(String(64), nullable=True)
    history_json = Column(Text, default="[]", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class FeedbackRecord(Base):
    __tablename__ = "feedback_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field_path = Column(String(128), nullable=False)
    original_value = Column(Text, default="", nullable=False)
    corrected_value = Column(Text, default="", nullable=False)
    user_id = Column(String(64), default="reviewer", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class AuditLogRecord(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(64), nullable=False)
    details_json = Column(Text, default="{}", nullable=False)
    previous_hash = Column(String(64), default="", nullable=False)
    entry_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class WebhookRecord(Base):
    __tablename__ = "webhooks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    target_url = Column(String(512), nullable=False)
    secret = Column(String(128), nullable=False)
    events_json = Column(Text, default="[]", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class WebhookDeliveryRecord(Base):
    __tablename__ = "webhook_deliveries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    webhook_id = Column(String(36), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(64), nullable=False)
    payload_json = Column(Text, nullable=False)
    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    attempt_count = Column(Integer, default=1, nullable=False)
    delivered_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


class UsageEventRecord(Base):
    __tablename__ = "usage_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    metadata_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
