"""Platform Phase 3 schema

Revision ID: 0002_platform
Revises: 0001_baseline
Create Date: 2026-11-03 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_platform"
down_revision: Union[str, None] = "0001_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tenants table
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("plan", sa.String(length=32), nullable=False, server_default="enterprise"),
        sa.Column("settings_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # 2. Users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="analyst"),
        sa.Column("totp_secret", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "email"),
    )

    # 3. API Keys table
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("key_hash", sa.String(length=128), nullable=False),
        sa.Column("prefix", sa.String(length=16), nullable=False),
        sa.Column("scopes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_api_key_hash", "api_keys", ["key_hash"])

    # 4. Custom Schemas table
    op.create_table(
        "custom_schemas",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("doc_type", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("schema_definition", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 5. Vendors table
    op.create_table(
        "vendors",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("canonical_name", sa.String(length=255), nullable=False),
        sa.Column("tax_id", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("aliases_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("default_currency", sa.String(length=8), nullable=False, server_default="USD"),
        sa.Column("bank_details_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_vendor_name_tax", "vendors", ["tenant_id", "canonical_name", "tax_id"])

    # 6. Purchase Orders table
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("po_number", sa.String(length=128), nullable=False),
        sa.Column("vendor_id", sa.String(length=36), nullable=True),
        sa.Column("order_date", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("delivery_date", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="USD"),
        sa.Column("total_amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("line_items_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "po_number"),
    )

    # 7. Workflows table
    op.create_table(
        "workflows",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("trigger_rules_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("steps_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 8. Workflow Runs table
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("workflow_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("current_step_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assigned_to", sa.String(length=64), nullable=True),
        sa.Column("history_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflows.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 9. Feedback Records table
    op.create_table(
        "feedback_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("field_path", sa.String(length=128), nullable=False),
        sa.Column("original_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("corrected_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("user_id", sa.String(length=64), nullable=False, server_default="reviewer"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 10. Audit Logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=64), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("previous_hash", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("entry_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_tenant_time", "audit_logs", ["tenant_id", "created_at"])

    # 11. Webhooks table
    op.create_table(
        "webhooks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("target_url", sa.String(length=512), nullable=False),
        sa.Column("secret", sa.String(length=128), nullable=False),
        sa.Column("events_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 12. Webhook Deliveries table
    op.create_table(
        "webhook_deliveries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("webhook_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["webhook_id"], ["webhooks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 13. Usage Events table
    op.create_table(
        "usage_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_usage_tenant_time", "usage_events", ["tenant_id", "created_at"])

    # 14. Add tenant_id, doc_type, storage_key to documents table
    with op.batch_alter_table("documents") as batch_op:
        batch_op.add_column(sa.Column("tenant_id", sa.String(length=36), nullable=False, server_default="default"))
        batch_op.add_column(sa.Column("doc_type", sa.String(length=64), nullable=False, server_default="invoice"))
        batch_op.add_column(sa.Column("storage_key", sa.String(length=255), nullable=True))
        batch_op.create_index("idx_doc_tenant", ["tenant_id"])
        batch_op.create_index("idx_doc_type", ["doc_type"])

    # 15. Add storage_key to page_images table
    with op.batch_alter_table("page_images") as batch_op:
        batch_op.add_column(sa.Column("storage_key", sa.String(length=255), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("page_images") as batch_op:
        batch_op.drop_column("storage_key")

    with op.batch_alter_table("documents") as batch_op:
        batch_op.drop_index("idx_doc_type")
        batch_op.drop_index("idx_doc_tenant")
        batch_op.drop_column("storage_key")
        batch_op.drop_column("doc_type")
        batch_op.drop_column("tenant_id")

    op.drop_table("usage_events")
    op.drop_table("webhook_deliveries")
    op.drop_table("webhooks")
    op.drop_table("audit_logs")
    op.drop_table("feedback_records")
    op.drop_table("workflow_runs")
    op.drop_table("workflows")
    op.drop_table("purchase_orders")
    op.drop_table("vendors")
    op.drop_table("custom_schemas")
    op.drop_table("api_keys")
    op.drop_table("users")
    op.drop_table("tenants")
