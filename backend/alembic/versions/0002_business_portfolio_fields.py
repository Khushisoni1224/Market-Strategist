"""business portfolio fields

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-24

- business_profiles.business_type is RENAMED to industry (existing data is kept).
- Adds description, business_model, website_url, location.
- description and business_model are nullable so existing rows migrate safely;
  those users simply show onboarding_completed = false until they fill them in.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('business_profiles', schema=None) as batch_op:
        batch_op.alter_column(
            'business_type',
            new_column_name='industry',
            existing_type=sa.String(length=100),
            existing_nullable=False,
        )
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('business_model', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('website_url', sa.String(length=2048), nullable=True))
        batch_op.add_column(sa.Column('location', sa.String(length=200), nullable=True))
        batch_op.create_check_constraint(
            op.f('ck_business_profiles_business_model_valid'),
            "business_model IS NULL OR business_model IN ('product', 'service', 'both')",
        )


def downgrade() -> None:
    with op.batch_alter_table('business_profiles', schema=None) as batch_op:
        batch_op.drop_constraint(op.f('ck_business_profiles_business_model_valid'), type_='check')
        batch_op.drop_column('location')
        batch_op.drop_column('website_url')
        batch_op.drop_column('business_model')
        batch_op.drop_column('description')
        batch_op.alter_column(
            'industry',
            new_column_name='business_type',
            existing_type=sa.String(length=100),
            existing_nullable=False,
        )
