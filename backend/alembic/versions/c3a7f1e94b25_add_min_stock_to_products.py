"""add_min_stock_to_products

Revision ID: c3a7f1e94b25
Revises: 21b58fdf539e
Create Date: 2026-08-22 09:15:00.000000

HU-011: umbral configurable de stock mínimo por producto. Cambio puramente
aditivo (NOT NULL con DEFAULT 0), seguro sobre datos existentes sin backfill.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3a7f1e94b25'
down_revision: Union[str, Sequence[str], None] = '21b58fdf539e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'products',
        sa.Column('min_stock', sa.Integer(), nullable=False, server_default='0')
    )
    op.create_check_constraint(
        'ck_products_min_stock_non_negative',
        'products',
        'min_stock >= 0'
    )


def downgrade() -> None:
    op.drop_constraint('ck_products_min_stock_non_negative', 'products', type_='check')
    op.drop_column('products', 'min_stock')
