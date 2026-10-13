"""create opspulse schema

Revision ID: 0001_create_opspulse
Revises: 
Create Date: 2026-10-13

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_opspulse"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "environments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "deployments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_name", sa.String(length=200), nullable=False),
        sa.Column("version", sa.String(length=100), nullable=False),
        sa.Column(
            "environment_id",
            sa.Integer(),
            sa.ForeignKey("environments.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("deployed_by", sa.String(length=120), nullable=False, server_default="system"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_deployments_status", "deployments", ["status"])
    op.create_index("ix_deployments_id", "deployments", ["id"])

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("affected_service", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("owner", sa.String(length=120), nullable=False, server_default="Unassigned"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_incidents_status", "incidents", ["status"])
    op.create_index("ix_incidents_id", "incidents", ["id"])


def downgrade():
    op.drop_table("incidents")
    op.drop_table("deployments")
    op.drop_table("environments")
