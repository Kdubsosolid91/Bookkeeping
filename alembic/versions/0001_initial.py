"""initial schema

Revision ID: 0001_initial
Revises: None
Create Date: 2026-02-27 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


account_type = sa.Enum(
    "ASSET",
    "LIABILITY",
    "EQUITY",
    "INCOME",
    "EXPENSE",
    "COGS",
    "OTHER_INCOME",
    "OTHER_EXPENSE",
    name="account_type",
    create_type=False,
)

pdf_parse_status = sa.Enum("PENDING", "PARSED", "FAILED", name="pdf_parse_status", create_type=False)

bank_txn_direction = sa.Enum("DEBIT", "CREDIT", name="bank_txn_direction", create_type=False)

bank_txn_status = sa.Enum(
    "NEW",
    "SUGGESTED",
    "MATCHED",
    "POSTED",
    "IGNORED",
    name="bank_txn_status",
    create_type=False,
)

rule_match_type = sa.Enum("CONTAINS", "STARTS_WITH", "REGEX", "EXACT", name="rule_match_type", create_type=False)

register_source = sa.Enum(
    "MANUAL",
    "BANK_FEED",
    "PAYROLL_IMPORT",
    "ADJUSTMENT",
    name="register_source",
    create_type=False,
)

match_type = sa.Enum("AUTO", "MANUAL", name="match_type", create_type=False)

reconciliation_status = sa.Enum("OPEN", "CLOSED", name="reconciliation_status", create_type=False)

audit_action = sa.Enum("CREATE", "UPDATE", "DELETE", name="audit_action", create_type=False)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    account_type.create(op.get_bind(), checkfirst=True)
    pdf_parse_status.create(op.get_bind(), checkfirst=True)
    bank_txn_direction.create(op.get_bind(), checkfirst=True)
    bank_txn_status.create(op.get_bind(), checkfirst=True)
    rule_match_type.create(op.get_bind(), checkfirst=True)
    register_source.create(op.get_bind(), checkfirst=True)
    match_type.create(op.get_bind(), checkfirst=True)
    reconciliation_status.create(op.get_bind(), checkfirst=True)
    audit_action.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "businesses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("base_currency", sa.Text(), nullable=False, server_default="USD"),
        sa.Column("close_lock_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "coa_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("type", account_type, nullable=False),
        sa.Column("code", sa.Text(), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("coa_accounts.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    op.create_table(
        "bank_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("institution", sa.Text(), nullable=True),
        sa.Column("account_last4", sa.Text(), nullable=True),
        sa.Column("opening_balance", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    op.create_table(
        "pdf_uploads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bank_accounts.id"), nullable=False),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("statement_start", sa.Date(), nullable=True),
        sa.Column("statement_end", sa.Date(), nullable=True),
        sa.Column("beginning_balance", sa.Numeric(14, 2), nullable=True),
        sa.Column("ending_balance", sa.Numeric(14, 2), nullable=True),
        sa.Column("parse_status", pdf_parse_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "bank_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bank_accounts.id"), nullable=False),
        sa.Column("pdf_upload_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pdf_uploads.id"), nullable=True),
        sa.Column("txn_date", sa.Date(), nullable=False),
        sa.Column("description_raw", sa.Text(), nullable=False),
        sa.Column("description_clean", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("direction", bank_txn_direction, nullable=False),
        sa.Column("running_balance", sa.Numeric(14, 2), nullable=True),
        sa.Column("imported_hash", sa.Text(), nullable=False),
        sa.Column("status", bank_txn_status, nullable=False),
        sa.Column("suggested_vendor", sa.Text(), nullable=True),
        sa.Column("suggested_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("coa_accounts.id"), nullable=True),
        sa.Column("suggested_confidence", sa.Numeric(3, 2), nullable=True),
        sa.Column("source_page", sa.Integer(), nullable=True),
        sa.Column("source_row", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("business_id", "bank_account_id", "imported_hash", name="uq_bank_txn_import"),
    )

    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("aliases", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("match_type", rule_match_type, nullable=False),
        sa.Column("pattern", sa.Text(), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.id"), nullable=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("coa_accounts.id"), nullable=True),
        sa.Column("class", sa.Text(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("memo_contains", sa.Text(), nullable=True),
        sa.Column("auto_suggest", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "register_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column("txn_date", sa.Date(), nullable=False),
        sa.Column("payee", sa.Text(), nullable=True),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("source", register_source, nullable=False),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bank_accounts.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "register_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "register_transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("register_transactions.id"),
            nullable=False,
        ),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("coa_accounts.id"), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("class", sa.Text(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("line_memo", sa.Text(), nullable=True),
    )

    op.create_table(
        "bank_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column(
            "bank_transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bank_transactions.id"),
            nullable=False,
        ),
        sa.Column(
            "register_transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("register_transactions.id"),
            nullable=False,
        ),
        sa.Column("match_type", match_type, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "reconciliation_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bank_accounts.id"), nullable=False),
        sa.Column("statement_start", sa.Date(), nullable=False),
        sa.Column("statement_end", sa.Date(), nullable=False),
        sa.Column("beginning_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("ending_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", reconciliation_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "reconciliation_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column(
            "reconciliation_session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reconciliation_sessions.id"),
            nullable=False,
        ),
        sa.Column(
            "register_transaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("register_transactions.id"),
            nullable=False,
        ),
        sa.Column("cleared_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("cleared_date", sa.Date(), nullable=False),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("businesses.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("entity_type", sa.Text(), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", audit_action, nullable=False),
        sa.Column("diff_json", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("reconciliation_items")
    op.drop_table("reconciliation_sessions")
    op.drop_table("bank_matches")
    op.drop_table("register_lines")
    op.drop_table("register_transactions")
    op.drop_table("rules")
    op.drop_table("vendors")
    op.drop_table("bank_transactions")
    op.drop_table("pdf_uploads")
    op.drop_table("bank_accounts")
    op.drop_table("coa_accounts")
    op.drop_table("businesses")
    op.drop_table("users")
    op.drop_table("workspaces")

    audit_action.drop(op.get_bind(), checkfirst=True)
    reconciliation_status.drop(op.get_bind(), checkfirst=True)
    match_type.drop(op.get_bind(), checkfirst=True)
    register_source.drop(op.get_bind(), checkfirst=True)
    rule_match_type.drop(op.get_bind(), checkfirst=True)
    bank_txn_status.drop(op.get_bind(), checkfirst=True)
    bank_txn_direction.drop(op.get_bind(), checkfirst=True)
    pdf_parse_status.drop(op.get_bind(), checkfirst=True)
    account_type.drop(op.get_bind(), checkfirst=True)
