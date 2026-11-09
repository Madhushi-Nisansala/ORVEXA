from __future__ import annotations

from pathlib import Path
from uuid import UUID


class StorageError(RuntimeError):
	pass


class LocalStorageProvider:
	"""Private development storage; physical paths never leave this boundary."""

	def __init__(self, root: str | Path) -> None:
		self.root = Path(root).resolve()
		self.root.mkdir(parents=True, exist_ok=True)

	def _safe_path(self, storage_key: str) -> Path:
		if not storage_key or Path(storage_key).is_absolute():
			raise StorageError("Invalid storage key")
		candidate = (self.root / storage_key).resolve()
		if candidate == self.root or self.root not in candidate.parents:
			raise StorageError("Invalid storage key")
		return candidate

	async def save(self, storage_key: str, content: bytes) -> None:
		path = self._safe_path(storage_key)
		path.parent.mkdir(parents=True, exist_ok=True)
		temporary_path = path.with_name(f".{path.name}.tmp")
		try:
			temporary_path.write_bytes(content)
			temporary_path.replace(path)
		except OSError as exc:
			temporary_path.unlink(missing_ok=True)
			raise StorageError("Unable to store document") from exc

	async def read(self, storage_key: str) -> bytes:
		path = self._safe_path(storage_key)
		try:
			return path.read_bytes()
		except FileNotFoundError as exc:
			raise StorageError("Stored document is unavailable") from exc

	async def delete(self, storage_key: str) -> None:
		path = self._safe_path(storage_key)
		path.unlink(missing_ok=True)

	@staticmethod
	def key_for(document_id: UUID, extension: str) -> str:
		return f"{document_id.hex[:2]}/{document_id.hex}/{document_id.hex}{extension}"
