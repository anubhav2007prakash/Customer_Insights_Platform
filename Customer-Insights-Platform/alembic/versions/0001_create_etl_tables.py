"""create etl tables

Revision ID: 0001_create_etl_tables
Revises: 
Create Date: 2026-07-03 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_create_etl_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'etl_pipelines',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('config', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'etl_jobs',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('pipeline_id', sa.UUID(as_uuid=True), nullable=True),
        sa.Column('trigger', sa.String(50), nullable=False, server_default='manual'),
        sa.Column('status', sa.String(50), nullable=False, server_default='queued'),
        sa.Column('user_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'etl_runs',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='running'),
        sa.Column('records_total', sa.Integer, nullable=True, server_default='0'),
        sa.Column('records_processed', sa.Integer, nullable=True, server_default='0'),
        sa.Column('records_failed', sa.Integer, nullable=True, server_default='0'),
    )

    op.create_table(
        'etl_transformations',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('spec', sa.JSON, nullable=False),
    )

    op.create_table(
        'etl_errors',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('run_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('record_index', sa.Integer, nullable=True),
        sa.Column('error_type', sa.String(100), nullable=False),
        sa.Column('details', sa.JSON, nullable=True),
    )

    op.create_table(
        'etl_metrics',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('run_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('metrics', sa.JSON, nullable=False),
    )

    op.create_table(
        'etl_audit_logs',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('run_id', sa.UUID(as_uuid=True), nullable=True),
        sa.Column('event', sa.String(200), nullable=False),
        sa.Column('details', sa.JSON, nullable=True),
    )


def downgrade():
    op.drop_table('etl_audit_logs')
    op.drop_table('etl_metrics')
    op.drop_table('etl_errors')
    op.drop_table('etl_transformations')
    op.drop_table('etl_runs')
    op.drop_table('etl_jobs')
    op.drop_table('etl_pipelines')
