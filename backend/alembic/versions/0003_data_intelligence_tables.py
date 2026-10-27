"""Create Member 3 feedback and marketing tables.

Revision ID: 0003
Revises: 0002
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the feedback and marketing tables."""

    # 1. Feedback import history
    op.create_table(
        "feedback_imports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("saved_rows", sa.Integer(), nullable=False),
        sa.Column("failed_rows", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "status IN ('processing', 'completed', 'failed')",
            name=op.f("ck_feedback_imports_status_valid"),
        ),
        sa.CheckConstraint(
            "total_rows >= 0",
            name=op.f("ck_feedback_imports_total_rows_non_negative"),
        ),
        sa.CheckConstraint(
            "saved_rows >= 0",
            name=op.f("ck_feedback_imports_saved_rows_non_negative"),
        ),
        sa.CheckConstraint(
            "failed_rows >= 0",
            name=op.f("ck_feedback_imports_failed_rows_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_feedback_imports_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_feedback_imports"),
        ),
    )

    op.create_index(
        op.f("ix_feedback_imports_user_id"),
        "feedback_imports",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_feedback_imports_user_created",
        "feedback_imports",
        ["user_id", "created_at"],
        unique=False,
    )

    # 2. Customer feedback and precomputed sentiment
    op.create_table(
        "customer_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("feedback_import_id", sa.Integer(), nullable=False),
        sa.Column("review_text", sa.Text(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("sentiment", sa.Text(), nullable=False),
        sa.Column("sentiment_score", sa.Float(), nullable=False),
        sa.Column("themes", sa.JSON(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "rating IS NULL OR rating BETWEEN 1 AND 5",
            name=op.f("ck_customer_feedback_rating_valid"),
        ),
        sa.CheckConstraint(
            "sentiment IN ('Positive', 'Neutral', 'Negative')",
            name=op.f("ck_customer_feedback_sentiment_valid"),
        ),
        sa.CheckConstraint(
            "sentiment_score BETWEEN -1 AND 1",
            name=op.f("ck_customer_feedback_sentiment_score_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_customer_feedback_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["feedback_import_id"],
            ["feedback_imports.id"],
            name=op.f(
                "fk_customer_feedback_feedback_import_id_feedback_imports"
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_customer_feedback_product_id_products"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_customer_feedback"),
        ),
    )

    op.create_index(
        op.f("ix_customer_feedback_user_id"),
        "customer_feedback",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_customer_feedback_feedback_import_id"),
        "customer_feedback",
        ["feedback_import_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_customer_feedback_product_id"),
        "customer_feedback",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        "ix_customer_feedback_user_sentiment",
        "customer_feedback",
        ["user_id", "sentiment"],
        unique=False,
    )
    op.create_index(
        "ix_customer_feedback_user_created",
        "customer_feedback",
        ["user_id", "created_at"],
        unique=False,
    )

    # 3. Marketing import history
    op.create_table(
        "marketing_imports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("saved_rows", sa.Integer(), nullable=False),
        sa.Column("updated_rows", sa.Integer(), nullable=False),
        sa.Column("invalid_rows", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "status IN ('processing', 'completed', 'failed')",
            name=op.f("ck_marketing_imports_status_valid"),
        ),
        sa.CheckConstraint(
            "total_rows >= 0",
            name=op.f("ck_marketing_imports_total_rows_non_negative"),
        ),
        sa.CheckConstraint(
            "saved_rows >= 0",
            name=op.f("ck_marketing_imports_saved_rows_non_negative"),
        ),
        sa.CheckConstraint(
            "updated_rows >= 0",
            name=op.f("ck_marketing_imports_updated_rows_non_negative"),
        ),
        sa.CheckConstraint(
            "invalid_rows >= 0",
            name=op.f("ck_marketing_imports_invalid_rows_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_marketing_imports_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_marketing_imports"),
        ),
    )

    op.create_index(
        op.f("ix_marketing_imports_user_id"),
        "marketing_imports",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_marketing_imports_user_created",
        "marketing_imports",
        ["user_id", "created_at"],
        unique=False,
    )

    # 4. Marketing performance records
    op.create_table(
        "marketing_performance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("marketing_import_id", sa.Integer(), nullable=False),
        sa.Column("content_date", sa.Date(), nullable=False),
        sa.Column("content_id", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=100), nullable=True),
        sa.Column("content_type", sa.String(length=100), nullable=True),
        sa.Column("reach", sa.Integer(), nullable=True),
        sa.Column("impressions", sa.Integer(), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=True),
        sa.Column("likes", sa.Integer(), nullable=True),
        sa.Column("comments", sa.Integer(), nullable=True),
        sa.Column("shares", sa.Integer(), nullable=True),
        sa.Column("conversions", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "reach IS NULL OR reach >= 0",
            name=op.f("ck_marketing_performance_reach_non_negative"),
        ),
        sa.CheckConstraint(
            "impressions IS NULL OR impressions >= 0",
            name=op.f(
                "ck_marketing_performance_impressions_non_negative"
            ),
        ),
        sa.CheckConstraint(
            "clicks IS NULL OR clicks >= 0",
            name=op.f("ck_marketing_performance_clicks_non_negative"),
        ),
        sa.CheckConstraint(
            "likes IS NULL OR likes >= 0",
            name=op.f("ck_marketing_performance_likes_non_negative"),
        ),
        sa.CheckConstraint(
            "comments IS NULL OR comments >= 0",
            name=op.f("ck_marketing_performance_comments_non_negative"),
        ),
        sa.CheckConstraint(
            "shares IS NULL OR shares >= 0",
            name=op.f("ck_marketing_performance_shares_non_negative"),
        ),
        sa.CheckConstraint(
            "conversions IS NULL OR conversions >= 0",
            name=op.f(
                "ck_marketing_performance_conversions_non_negative"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_marketing_performance_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["marketing_import_id"],
            ["marketing_imports.id"],
            name=op.f(
                "fk_marketing_performance_marketing_import_id_marketing_imports"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_marketing_performance"),
        ),
        sa.UniqueConstraint(
            "user_id",
            "content_date",
            "content_id",
            name="user_date_content_unique",
        ),
    )

    op.create_index(
        op.f("ix_marketing_performance_user_id"),
        "marketing_performance",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_marketing_performance_marketing_import_id"),
        "marketing_performance",
        ["marketing_import_id"],
        unique=False,
    )
    op.create_index(
        "ix_marketing_performance_user_date",
        "marketing_performance",
        ["user_id", "content_date"],
        unique=False,
    )


def downgrade() -> None:
    """Remove Member 3 tables in dependency-safe order."""

    # Remove marketing records before their import history.
    op.drop_index(
        "ix_marketing_performance_user_date",
        table_name="marketing_performance",
    )
    op.drop_index(
        op.f("ix_marketing_performance_marketing_import_id"),
        table_name="marketing_performance",
    )
    op.drop_index(
        op.f("ix_marketing_performance_user_id"),
        table_name="marketing_performance",
    )
    op.drop_table("marketing_performance")

    op.drop_index(
        "ix_marketing_imports_user_created",
        table_name="marketing_imports",
    )
    op.drop_index(
        op.f("ix_marketing_imports_user_id"),
        table_name="marketing_imports",
    )
    op.drop_table("marketing_imports")

    # Remove reviews before their feedback import history.
    op.drop_index(
        "ix_customer_feedback_user_created",
        table_name="customer_feedback",
    )
    op.drop_index(
        "ix_customer_feedback_user_sentiment",
        table_name="customer_feedback",
    )
    op.drop_index(
        op.f("ix_customer_feedback_product_id"),
        table_name="customer_feedback",
    )
    op.drop_index(
        op.f("ix_customer_feedback_feedback_import_id"),
        table_name="customer_feedback",
    )
    op.drop_index(
        op.f("ix_customer_feedback_user_id"),
        table_name="customer_feedback",
    )
    op.drop_table("customer_feedback")

    op.drop_index(
        "ix_feedback_imports_user_created",
        table_name="feedback_imports",
    )
    op.drop_index(
        op.f("ix_feedback_imports_user_id"),
        table_name="feedback_imports",
    )
    op.drop_table("feedback_imports")