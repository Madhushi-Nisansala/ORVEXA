"""Add Stage 2 extraction job lifecycle and page metadata.

Revision ID: 0006_stage2_extraction_jobs
Revises: 0005_document_extractions
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006_stage2_extraction_jobs"
down_revision: Union[str, Sequence[str], None] = "0005_document_extractions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column(
		"document_processing_jobs",
		sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
	)
	op.add_column(
		"document_processing_jobs",
		sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
	)
	op.add_column("document_processing_jobs", sa.Column("claim_token", sa.String(64), nullable=True))
	op.add_column("document_processing_jobs", sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True))
	op.add_column(
		"document_processing_jobs",
		sa.Column("processing_version", sa.String(32), nullable=False, server_default="stage2-v1"),
	)
	op.create_index(
		"ix_document_processing_jobs_claimable",
		"document_processing_jobs",
		["status", "available_at"],
	)
	op.create_index(
		"ix_document_processing_jobs_claim_token",
		"document_processing_jobs",
		["claim_token"],
		unique=True,
	)

	op.add_column(
		"document_extractions",
		sa.Column("detected_document_type", sa.String(32), nullable=True),
	)
	op.add_column(
		"document_extractions",
		sa.Column("processing_version", sa.String(32), nullable=False, server_default="stage2-v1"),
	)
	op.add_column(
		"document_extractions",
		sa.Column("language_detection_status", sa.String(32), nullable=False, server_default="not_run"),
	)

	op.add_column(
		"document_pages",
		sa.Column("extraction_status", sa.String(32), nullable=False, server_default="completed"),
	)
	op.add_column(
		"document_pages",
		sa.Column("ocr_used", sa.Boolean(), nullable=False, server_default=sa.false()),
	)
	op.add_column("document_pages", sa.Column("error_summary", sa.String(500), nullable=True))


def downgrade() -> None:
	op.drop_column("document_pages", "error_summary")
	op.drop_column("document_pages", "ocr_used")
	op.drop_column("document_pages", "extraction_status")
	op.drop_column("document_extractions", "language_detection_status")
	op.drop_column("document_extractions", "processing_version")
	op.drop_column("document_extractions", "detected_document_type")
	op.drop_index("ix_document_processing_jobs_claim_token", table_name="document_processing_jobs")
	op.drop_index("ix_document_processing_jobs_claimable", table_name="document_processing_jobs")
	op.drop_column("document_processing_jobs", "processing_version")
	op.drop_column("document_processing_jobs", "claimed_at")
	op.drop_column("document_processing_jobs", "claim_token")
	op.drop_column("document_processing_jobs", "available_at")
	op.drop_column("document_processing_jobs", "max_attempts")
