"""Add Phase 3 document processing and action schema.

Revision ID: 0002_phase3_documents
Revises: 0001_phase2_auth
"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa

revision: str = '0002_phase3_documents'
down_revision: Union[str, Sequence[str], None] = '0001_phase2_auth'
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_table('documents',
		sa.Column('id', sa.Uuid(), nullable=False),
		sa.Column('user_id', sa.Uuid(), nullable=False),
		sa.Column('original_filename', sa.String(255), nullable=False),
		sa.Column('storage_key', sa.String(128), nullable=False),
		sa.Column('mime_type', sa.String(127), nullable=False),
		sa.Column('file_size', sa.Integer(), nullable=False),
		sa.Column('sha256_hash', sa.String(64), nullable=False),
		sa.Column('document_type', sa.String(32), nullable=False),
		sa.Column('detected_language', sa.String(16)),
		sa.Column('processing_status', sa.String(32), nullable=False),
		sa.Column('extraction_status', sa.String(32), nullable=False),
		sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
		sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
		sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
		sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('storage_key'))
	op.create_index('ix_documents_user_id', 'documents', ['user_id'])
	op.create_index('ix_documents_sha256_hash', 'documents', ['sha256_hash'])
	op.create_table('document_pages',
		sa.Column('id', sa.Uuid(), nullable=False), sa.Column('document_id', sa.Uuid(), nullable=False),
		sa.Column('page_number', sa.Integer(), nullable=False), sa.Column('extracted_text', sa.Text(), nullable=False),
		sa.Column('extraction_method', sa.String(32), nullable=False), sa.Column('extraction_confidence', sa.Float()),
		sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
		sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'), sa.PrimaryKeyConstraint('id'))
	op.create_index('ix_document_pages_document_id', 'document_pages', ['document_id'])
	op.create_table('document_processing_jobs',
		sa.Column('id', sa.Uuid(), nullable=False), sa.Column('document_id', sa.Uuid(), nullable=False),
		sa.Column('job_type', sa.String(32), nullable=False), sa.Column('status', sa.String(32), nullable=False),
		sa.Column('attempts', sa.Integer(), nullable=False), sa.Column('error_message', sa.Text()),
		sa.Column('started_at', sa.DateTime(timezone=True)), sa.Column('completed_at', sa.DateTime(timezone=True)),
		sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
		sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'), sa.PrimaryKeyConstraint('id'))
	op.create_index('ix_document_processing_jobs_document_id', 'document_processing_jobs', ['document_id'])
	op.create_table('analyses',
		sa.Column('id', sa.Uuid(), nullable=False), sa.Column('user_id', sa.Uuid(), nullable=False),
		sa.Column('document_id', sa.Uuid(), nullable=False), sa.Column('provider', sa.String(64), nullable=False),
		sa.Column('model_name', sa.String(128)), sa.Column('status', sa.String(32), nullable=False),
		sa.Column('summary', sa.JSON()), sa.Column('category', sa.String(64)), sa.Column('detected_language', sa.String(16)),
		sa.Column('confidence', sa.Float()), sa.Column('error_message', sa.Text()),
		sa.Column('created_at', sa.DateTime(timezone=True), nullable=False), sa.Column('completed_at', sa.DateTime(timezone=True)),
		sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'), sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'), sa.PrimaryKeyConstraint('id'))
	op.create_index('ix_analyses_user_id', 'analyses', ['user_id']); op.create_index('ix_analyses_document_id', 'analyses', ['document_id'])
	op.create_table('extracted_facts',
		sa.Column('id', sa.Uuid(), nullable=False), sa.Column('analysis_id', sa.Uuid(), nullable=False),
		sa.Column('fact_type', sa.String(64), nullable=False), sa.Column('fact_value', sa.JSON(), nullable=False),
		sa.Column('source_page', sa.Integer()), sa.Column('evidence_text', sa.Text()), sa.Column('confidence', sa.Float()),
		sa.Column('verification_status', sa.String(32), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
		sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'), sa.PrimaryKeyConstraint('id'))
	op.create_index('ix_extracted_facts_analysis_id', 'extracted_facts', ['analysis_id'])
	op.create_table('action_plans',
		sa.Column('id', sa.Uuid(), nullable=False), sa.Column('user_id', sa.Uuid(), nullable=False), sa.Column('analysis_id', sa.Uuid(), nullable=False),
		sa.Column('title', sa.String(200), nullable=False), sa.Column('description', sa.Text(), nullable=False), sa.Column('status', sa.String(32), nullable=False),
		sa.Column('created_at', sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
		sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'), sa.PrimaryKeyConstraint('id'))
	op.create_index('ix_action_plans_user_id', 'action_plans', ['user_id'])
	op.create_table('actions',
		sa.Column('id', sa.Uuid(), nullable=False), sa.Column('user_id', sa.Uuid(), nullable=False), sa.Column('analysis_id', sa.Uuid(), nullable=False),
		sa.Column('action_plan_id', sa.Uuid(), nullable=False), sa.Column('title', sa.String(200), nullable=False), sa.Column('description', sa.Text(), nullable=False),
		sa.Column('priority', sa.String(16), nullable=False), sa.Column('due_at', sa.DateTime(timezone=True)), sa.Column('status', sa.String(32), nullable=False),
		sa.Column('evidence_reference', sa.JSON()), sa.Column('confidence', sa.Float()), sa.Column('approved_at', sa.DateTime(timezone=True)),
		sa.Column('created_at', sa.DateTime(timezone=True), nullable=False), sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
		sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'), sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
		sa.ForeignKeyConstraint(['action_plan_id'], ['action_plans.id'], ondelete='CASCADE'), sa.PrimaryKeyConstraint('id'))
	op.create_index('ix_actions_user_id', 'actions', ['user_id']); op.create_index('ix_actions_action_plan_id', 'actions', ['action_plan_id'])


def downgrade() -> None:
	op.drop_index('ix_actions_action_plan_id', table_name='actions'); op.drop_index('ix_actions_user_id', table_name='actions'); op.drop_table('actions')
	op.drop_index('ix_action_plans_user_id', table_name='action_plans'); op.drop_table('action_plans')
	op.drop_index('ix_extracted_facts_analysis_id', table_name='extracted_facts'); op.drop_table('extracted_facts')
	op.drop_index('ix_analyses_document_id', table_name='analyses'); op.drop_index('ix_analyses_user_id', table_name='analyses'); op.drop_table('analyses')
	op.drop_index('ix_document_processing_jobs_document_id', table_name='document_processing_jobs'); op.drop_table('document_processing_jobs')
	op.drop_index('ix_document_pages_document_id', table_name='document_pages'); op.drop_table('document_pages')
	op.drop_index('ix_documents_sha256_hash', table_name='documents'); op.drop_index('ix_documents_user_id', table_name='documents'); op.drop_table('documents')
