import enum
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class AccountType(enum.Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    COGS = "COGS"
    OTHER_INCOME = "OTHER_INCOME"
    OTHER_EXPENSE = "OTHER_EXPENSE"


class PdfParseStatus(enum.Enum):
    PENDING = "PENDING"
    PARSED = "PARSED"
    FAILED = "FAILED"


class BankTxnDirection(enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class BankTxnStatus(enum.Enum):
    NEW = "NEW"
    SUGGESTED = "SUGGESTED"
    MATCHED = "MATCHED"
    POSTED = "POSTED"
    IGNORED = "IGNORED"


class RuleMatchType(enum.Enum):
    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    REGEX = "REGEX"
    EXACT = "EXACT"


class RegisterSource(enum.Enum):
    MANUAL = "MANUAL"
    BANK_FEED = "BANK_FEED"
    PAYROLL_IMPORT = "PAYROLL_IMPORT"
    ADJUSTMENT = "ADJUSTMENT"


class MatchType(enum.Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"


class ReconciliationStatus(enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class AuditAction(enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Business(Base):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(Text, nullable=False)
    base_currency = Column(Text, nullable=False, server_default="USD")
    close_lock_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CoaAccount(Base):
    __tablename__ = "coa_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    name = Column(Text, nullable=False)
    type = Column(Enum(AccountType, name="account_type"), nullable=False)
    code = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("coa_accounts.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    name = Column(Text, nullable=False)
    institution = Column(Text, nullable=True)
    account_last4 = Column(Text, nullable=True)
    opening_balance = Column(Numeric(14, 2), nullable=False, server_default="0")
    is_active = Column(Boolean, nullable=False, server_default="true")


class PdfUpload(Base):
    __tablename__ = "pdf_uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    filename = Column(Text, nullable=False)
    storage_path = Column(Text, nullable=False)
    statement_start = Column(Date, nullable=True)
    statement_end = Column(Date, nullable=True)
    beginning_balance = Column(Numeric(14, 2), nullable=True)
    ending_balance = Column(Numeric(14, 2), nullable=True)
    parse_status = Column(Enum(PdfParseStatus, name="pdf_parse_status"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class BankTransaction(Base):
    __tablename__ = "bank_transactions"
    __table_args__ = (
        UniqueConstraint("business_id", "bank_account_id", "imported_hash", name="uq_bank_txn_import"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    pdf_upload_id = Column(UUID(as_uuid=True), ForeignKey("pdf_uploads.id"), nullable=True)
    txn_date = Column(Date, nullable=False)
    description_raw = Column(Text, nullable=False)
    description_clean = Column(Text, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    direction = Column(Enum(BankTxnDirection, name="bank_txn_direction"), nullable=False)
    running_balance = Column(Numeric(14, 2), nullable=True)
    imported_hash = Column(Text, nullable=False)
    status = Column(Enum(BankTxnStatus, name="bank_txn_status"), nullable=False)
    suggested_vendor = Column(Text, nullable=True)
    suggested_account_id = Column(UUID(as_uuid=True), ForeignKey("coa_accounts.id"), nullable=True)
    suggested_confidence = Column(Numeric(3, 2), nullable=True)
    source_page = Column(Integer, nullable=True)
    source_row = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    name = Column(Text, nullable=False)
    aliases = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Rule(Base):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    priority = Column(Integer, nullable=False, server_default="100")
    match_type = Column(Enum(RuleMatchType, name="rule_match_type"), nullable=False)
    pattern = Column(Text, nullable=False)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("coa_accounts.id"), nullable=True)
    class_ = Column("class", Text, nullable=True)
    location = Column(Text, nullable=True)
    memo_contains = Column(Text, nullable=True)
    auto_suggest = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RegisterTransaction(Base):
    __tablename__ = "register_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    txn_date = Column(Date, nullable=False)
    payee = Column(Text, nullable=True)
    memo = Column(Text, nullable=True)
    source = Column(Enum(RegisterSource, name="register_source"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    lines = relationship(
        "RegisterLine",
        back_populates="transaction",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class RegisterLine(Base):
    __tablename__ = "register_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    register_transaction_id = Column(
        UUID(as_uuid=True), ForeignKey("register_transactions.id"), nullable=False
    )
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("coa_accounts.id"), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    class_ = Column("class", Text, nullable=True)
    location = Column(Text, nullable=True)
    line_memo = Column(Text, nullable=True)

    transaction = relationship("RegisterTransaction", back_populates="lines")


class BankMatch(Base):
    __tablename__ = "bank_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    bank_transaction_id = Column(UUID(as_uuid=True), ForeignKey("bank_transactions.id"), nullable=False)
    register_transaction_id = Column(
        UUID(as_uuid=True), ForeignKey("register_transactions.id"), nullable=False
    )
    match_type = Column(Enum(MatchType, name="match_type"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ReconciliationSession(Base):
    __tablename__ = "reconciliation_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    statement_start = Column(Date, nullable=False)
    statement_end = Column(Date, nullable=False)
    beginning_balance = Column(Numeric(14, 2), nullable=False)
    ending_balance = Column(Numeric(14, 2), nullable=False)
    status = Column(Enum(ReconciliationStatus, name="reconciliation_status"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)


class ReconciliationItem(Base):
    __tablename__ = "reconciliation_items"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    reconciliation_session_id = Column(
        UUID(as_uuid=True), ForeignKey("reconciliation_sessions.id"), nullable=False
    )
    register_transaction_id = Column(
        UUID(as_uuid=True), ForeignKey("register_transactions.id"), nullable=False
    )
    cleared_amount = Column(Numeric(14, 2), nullable=False)
    cleared_date = Column(Date, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    entity_type = Column(Text, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(Enum(AuditAction, name="audit_action"), nullable=False)
    diff_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
