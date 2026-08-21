import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey, UUID
from sqlalchemy.orm import relationship
from src.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), nullable=False, default="CONFIRMED")  # Inmutable en v1
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="sales")
    customer = relationship("Customer")
    user = relationship("User")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.id", ondelete="RESTRICT"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    movement_type = Column(String(20), nullable=False)  # 'SALE', 'PURCHASE'
    quantity = Column(Integer, nullable=False)  # - for sale, + for purchase
    stock_before = Column(Integer, nullable=False)
    stock_after = Column(Integer, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reference_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    product = relationship("Product")
    user = relationship("User")
