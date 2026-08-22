"""add_categories

Revision ID: a3f7c21d9e04
Revises: 21b58fdf539e
Create Date: 2026-08-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f7c21d9e04'
down_revision: Union[str, Sequence[str], None] = '21b58fdf539e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # HU-013: Categories table (tenant-scoped, unique name per tenant)
    op.create_table(
        'categories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'name', name='uq_category_tenant_name')
    )
    op.create_index('ix_categories_tenant_id', 'categories', ['tenant_id'], unique=False)

    # HU-013: Optional category reference on products (additive, nullable)
    op.add_column('products', sa.Column('category_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_products_category_id', 'products', 'categories', ['category_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_products_category_id', 'products', type_='foreignkey')
    op.drop_column('products', 'category_id')
    op.drop_index('ix_categories_tenant_id', table_name='categories')
    op.drop_table('categories')
