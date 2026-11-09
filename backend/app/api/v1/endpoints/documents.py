from uuid import UUID
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.config import get_settings
from app.database.models import User
from app.database.session import get_db
from app.modules.documents.document_models import Document, DocumentPage
from app.modules.documents.document_schemas import DocumentListResponse, DocumentResponse, DocumentSearchResponse, ProcessingJobResponse
from app.modules.documents.document_service import DocumentNotFoundError, DocumentService, DuplicateDocumentError
from app.modules.documents.storage import StorageError
from app.modules.extraction.schemas import ExtractedPageResponse, ExtractionResponse
from app.modules.extraction.extractors import available_ocr_languages
from app.modules.extraction.models import DocumentExtraction

router = APIRouter(prefix="/documents", tags=["documents"])


def service(db: AsyncSession) -> DocumentService:
	return DocumentService(db, get_settings())


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
	file: UploadFile = File(...),
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
	settings = get_settings()
	if file.content_type is None:
		raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Document type is required")
	content = await file.read(settings.document_max_file_size_bytes + 1)
	if len(content) > settings.document_max_file_size_bytes:
		raise HTTPException(
			status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
			detail="Document exceeds the maximum allowed size",
		)
	try:
		return await service(db).create_upload(user.id, file.filename, file.content_type, content)
	except DuplicateDocumentError as exc:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"message": "Document already exists", "document_id": str(exc.document.id)}) from exc
	except ValueError as exc:
		raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("", response_model=DocumentListResponse)
async def list_documents(
	limit: int = 50,
	offset: int = 0,
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
	if limit < 1 or limit > 100 or offset < 0:
		raise HTTPException(status_code=422, detail="Invalid pagination")
	items, total = await service(db).repository.list_owned(user.id, limit, offset)
	return DocumentListResponse(items=items, limit=limit, offset=offset, total=total)


@router.get("/search", response_model=DocumentSearchResponse)
async def search_documents(
	q: str = Query(min_length=1, max_length=200),
	user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> DocumentSearchResponse:
	result = await db.execute(
		select(Document)
		.join(DocumentPage, DocumentPage.document_id == Document.id)
		.where(
			Document.user_id == user.id,
			Document.deleted_at.is_(None),
			DocumentPage.extracted_text.ilike(f"%{q}%"),
		)
		.distinct()
		.order_by(Document.created_at.desc())
	)
	return DocumentSearchResponse(items=list(result.scalars().unique()))


@router.get("/capabilities")
async def extraction_capabilities() -> dict[str, object]:
	return {
		"pdf": True,
		"docx": True,
		"txt": True,
		"csv": True,
		**available_ocr_languages(),
	}


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> DocumentResponse:
	try:
		return await service(db).get_owned(document_id, user.id)
	except DocumentNotFoundError as exc:
		raise HTTPException(status_code=404, detail="Document not found") from exc


@router.post("/{document_id}/extract", response_model=ProcessingJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def extract_document(document_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> ProcessingJobResponse:
	document_service = service(db)
	try:
		return await document_service.enqueue_extraction(document_id, user.id)
	except DocumentNotFoundError as exc:
		raise HTTPException(status_code=404, detail="Document not found") from exc


@router.get("/{document_id}/extraction", response_model=ExtractionResponse)
async def extraction_status(document_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> ExtractionResponse:
	try:
		document = await service(db).get_owned(document_id, user.id)
	except DocumentNotFoundError as exc:
		raise HTTPException(status_code=404, detail="Document not found") from exc
	extraction = await db.scalar(
		select(DocumentExtraction)
		.where(DocumentExtraction.document_id == document.id)
		.order_by(DocumentExtraction.created_at.desc())
	)
	if extraction is None:
		raise HTTPException(status_code=404, detail="Extraction not found")
	return extraction


@router.get("/{document_id}/pages", response_model=list[ExtractedPageResponse])
async def extracted_pages(document_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[ExtractedPageResponse]:
	try:
		await service(db).get_owned(document_id, user.id)
	except DocumentNotFoundError as exc:
		raise HTTPException(status_code=404, detail="Document not found") from exc
	rows = await db.scalars(select(DocumentPage).where(DocumentPage.document_id == document_id).order_by(DocumentPage.page_number))
	return [ExtractedPageResponse(
		page_number=row.page_number, text=row.extracted_text, extraction_method=row.extraction_method,
		extraction_status=row.extraction_status, ocr_used=row.ocr_used,
		error_summary=row.error_summary, extraction_confidence=row.extraction_confidence,
	) for row in rows]


@router.get("/{document_id}/content")
async def download_document(document_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Response:
	document_service = service(db)
	try:
		document = await document_service.get_owned(document_id, user.id)
		content = await document_service.storage.read(document.storage_key)
	except DocumentNotFoundError as exc:
		raise HTTPException(status_code=404, detail="Document not found") from exc
	except StorageError as exc:
		raise HTTPException(status_code=404, detail="Stored document is unavailable") from exc
	filename = document.original_filename.replace('"', "'")
	return Response(
		content=content,
		media_type=document.mime_type,
		headers={
			"Content-Disposition": f"attachment; filename=\"{filename}\"; filename*=UTF-8''{quote(filename)}",
			"X-Content-Type-Options": "nosniff",
		},
	)


@router.post("/{document_id}/archive", response_model=DocumentResponse)
async def archive_document(document_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> DocumentResponse:
	try:
		return await service(db).archive(document_id, user.id)
	except DocumentNotFoundError as exc:
		raise HTTPException(status_code=404, detail="Document not found") from exc


@router.post("/{document_id}/retry", response_model=ProcessingJobResponse)
async def retry_document(document_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> ProcessingJobResponse:
	try:
		return await service(db).retry(document_id, user.id)
	except DocumentNotFoundError as exc:
		raise HTTPException(status_code=404, detail="Document not found") from exc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> None:
	try:
		await service(db).delete(document_id, user.id)
	except DocumentNotFoundError as exc:
		raise HTTPException(status_code=404, detail="Document not found") from exc
