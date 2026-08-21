import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, DateTime
from sqlalchemy.orm import declared_attr
from src.database import Base

class TenantMixin:
    """Mixin for models requiring mandatory multi-tenant scope isolation."""
    @declared_attr
    def tenant_id(cls):
        return Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True)

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
