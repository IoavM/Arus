import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey, UUID, UniqueConstraint
from sqlalchemy.orm import relationship
from src.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True)
    sku = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    sale_price = Column(Numeric(12, 2), nullable=False)
    current_stock = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="ACTIVE")  # 'ACTIVE', 'INACTIVE'
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uq_product_tenant_sku"),
    )

    tenant = relationship("Tenant", back_populates="products")
