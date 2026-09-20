"""create data quality tables

Revision ID: 0002_create_data_quality_tables
Revises: 0001_create_etl_tables
Create Date: 2026-07-05 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0002_create_data_quality_tables'
down_revision = '0001_create_etl_tables'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'data_profiles',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.Uuid(as_uuid=True), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('total_rows', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_columns', sa.Integer, nullable=False, server_default='0'),
        sa.Column('profile_metrics', sa.JSON, nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'data_quality_scores',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('overall_score', sa.Float, nullable=False),
        sa.Column('category_scores', sa.JSON, nullable=False),
        sa.Column('grade', sa.String(2), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'schema_definitions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('version_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('schema_spec', sa.JSON, nullable=False),
        sa.Column('manual_overrides', sa.JSON, nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'schema_versions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('schema_definition_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.Integer, nullable=False),
        sa.Column('change_summary', sa.Text, nullable=True),
        sa.Column('schema_spec', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'validation_rules',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('rule_name', sa.String(200), nullable=False),
        sa.Column('rule_type', sa.String(100), nullable=False),
        sa.Column('parameters', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'validation_results',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('rule_name', sa.String(200), nullable=False),
        sa.Column('passed', sa.Boolean, nullable=False),
        sa.Column('details', sa.JSON, nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'duplicate_reports',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('report', sa.JSON, nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'outlier_reports',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('report', sa.JSON, nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'drift_reports',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('baseline_version', sa.Integer, nullable=False),
        sa.Column('target_version', sa.Integer, nullable=False),
        sa.Column('drift_metrics', sa.JSON, nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'lineage_records',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('lineage', sa.JSON, nullable=False),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'governance_policies',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('policy_name', sa.String(200), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('policy_type', sa.String(100), nullable=False),
        sa.Column('policy_definition', sa.JSON, nullable=False),
        sa.Column('enabled', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'data_versions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_name', sa.String(200), nullable=False),
        sa.Column('import_version', sa.Integer, nullable=False),
        sa.Column('schema_version', sa.Integer, nullable=False),
        sa.Column('transformation_version', sa.Integer, nullable=False),
        sa.Column('validation_version', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'quality_audit_logs',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('event', sa.String(200), nullable=False),
        sa.Column('details', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table('quality_audit_logs')
    op.drop_table('data_versions')
    op.drop_table('governance_policies')
    op.drop_table('lineage_records')
    op.drop_table('drift_reports')
    op.drop_table('outlier_reports')
    op.drop_table('duplicate_reports')
    op.drop_table('validation_results')
    op.drop_table('validation_rules')
    op.drop_table('schema_versions')
    op.drop_table('schema_definitions')
    op.drop_table('data_quality_scores')
    op.drop_table('data_profiles')
