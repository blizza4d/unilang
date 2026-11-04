"""Baseline Phase 2 schema

Revision ID: 0001_baseline
Revises: 
Create Date: 2026-11-03 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("mime", sa.String(length=64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="REQUIRES_HUMAN_REVIEW"),
        sa.Column("vendor_name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("invoice_number", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("total_amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default=""),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column("original_result_json", sa.Text(), nullable=False),
        sa.Column("grounding_json", sa.Text(), nullable=True),
        sa.Column("processing_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("usage_json", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_doc_created", "documents", ["created_at"])
    op.create_index("idx_doc_sha256", "documents", ["sha256"])
    op.create_index("idx_doc_vendor", "documents", ["vendor_name"])
    op.create_index("idx_doc_status", "documents", ["status"])

    op.create_table(
        "page_images",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.Column("width_px", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column("height_px", sa.Integer(), nullable=False, server_default="1414"),
        sa.Column("jpeg_bytes", sa.LargeBinary(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_page_doc", "page_images", ["document_id", "page"])

    op.create_table(
        "edit_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("field_path", sa.String(length=128), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("new_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("editor", sa.String(length=64), nullable=False, server_default="reviewer"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_edit_doc", "edit_records", ["document_id", "created_at"])

    op.create_table(
        "approval_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_by", sa.String(length=64), nullable=False, server_default="reviewer"),
        sa.Column("note", sa.String(length=255), nullable=False, server_default=""),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "batches",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_files", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="processing"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "batch_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("batch_id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "eval_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dataset_size", sa.Integer(), nullable=False),
        sa.Column("mean_field_accuracy", sa.Float(), nullable=False),
        sa.Column("mean_line_item_f1", sa.Float(), nullable=False),
        sa.Column("mean_hallucination_score", sa.Float(), nullable=False),
        sa.Column("mean_latency_ms", sa.Float(), nullable=False),
        sa.Column("math_pass_rate", sa.Float(), nullable=False),
        sa.Column("model_name", sa.String(length=64), nullable=False),
        sa.Column("results_json", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("eval_runs")
    op.drop_table("batch_items")
    op.drop_table("batches")
    op.drop_table("approval_records")
    op.drop_table("edit_records")
    op.drop_table("page_images")
    op.drop_table("documents")
