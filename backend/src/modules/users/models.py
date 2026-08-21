import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, UniqueConstraint
from sqlalchemy.orm import relationship
from src.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(50), primary_key=True)  # 'ADMIN', 'SELLER'
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role_id = Column(String(50), ForeignKey("roles.id"), nullable=False, default="SELLER")
    status = Column(String(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),
    )

    tenant = relationship("Tenant", back_populates="users")
    role = relationship("Role")
