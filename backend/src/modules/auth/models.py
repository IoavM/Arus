import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy.orm import relationship
from src.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    tax_id = Column(String(50), nullable=False, unique=True, index=True)
    status = Column(String(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="tenant", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="tenant", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="tenant", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="tenant", cascade="all, delete-orphan")
