"""Add strategy runs, recommendations, and outcomes.

Revision ID: 0004
Revises: 0003
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "strategy_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("llm_provider", sa.String(length=50), nullable=False),
        sa.Column("used_fallback", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("data_warnings", sa.JSON(), nullable=False),
        sa.Column("weights_used", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )



    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("strategy_run_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("target_product_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("score_interpretation", sa.String(length=30), nullable=False),
        sa.Column("reasoning_summary", sa.Text(), nullable=False),
        sa.Column("supporting_evidence", sa.JSON(), nullable=False),
        sa.Column("suggested_content", sa.Text(), nullable=True),
        sa.Column("data_gaps", sa.JSON(), nullable=False),
        sa.Column("caveats", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["strategy_run_id"], ["strategy_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_product_id"], ["products.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_recommendations_strategy_run_id", "recommendations", ["strategy_run_id"])
    op.create_index("ix_recommendations_owner_id", "recommendations", ["owner_id"])
    op.create_index("ix_recommendations_target_product_id", "recommendations", ["target_product_id"])

    op.create_table(
        "recommendation_outcomes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recommendation_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("reach", sa.Integer(), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=True),
        sa.Column("orders", sa.Integer(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["recommendation_id"], ["recommendations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_recommendation_outcomes_recommendation_id", "recommendation_outcomes", ["recommendation_id"])
    op.create_index("ix_recommendation_outcomes_owner_id", "recommendation_outcomes", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_recommendation_outcomes_owner_id", table_name="recommendation_outcomes")
    op.drop_index("ix_recommendation_outcomes_recommendation_id", table_name="recommendation_outcomes")
    op.drop_table("recommendation_outcomes")
    op.drop_index("ix_recommendations_target_product_id", table_name="recommendations")
    op.drop_index("ix_recommendations_owner_id", table_name="recommendations")
    op.drop_index("ix_recommendations_strategy_run_id", table_name="recommendations")
    op.drop_table("recommendations")
    op.drop_index("ix_strategy_runs_owner_id", table_name="strategy_runs")
    op.drop_table("strategy_runs")
