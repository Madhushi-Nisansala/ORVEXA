from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Table, Column, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

user_roles = Table(
	"user_roles",
	Base.metadata,
	Column("user_id", Uuid, ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True),
	Column("role_id", Uuid, ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True),
)


class User(Base):
	__tablename__ = "users"
	__table_args__ = (Index("ix_users_email", "email", unique=True),)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	email: Mapped[str] = mapped_column(String(320), nullable=False)
	password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
	full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
	preferred_language: Mapped[str] = mapped_column(String(2), nullable=False, default="en")
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
	is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

	roles: Mapped[list[Role]] = relationship(secondary=user_roles, back_populates="users")
	refresh_tokens: Mapped[list[RefreshToken]] = relationship(
		back_populates="user", cascade="all, delete-orphan"
	)


class Role(Base):
	__tablename__ = "roles"
	__table_args__ = (Index("ix_roles_name", "name", unique=True),)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	name: Mapped[str] = mapped_column(String(50), nullable=False)

	users: Mapped[list[User]] = relationship(secondary=user_roles, back_populates="roles")


class RefreshToken(Base):
	__tablename__ = "refresh_tokens"
	__table_args__ = (
		Index("ix_refresh_tokens_token_hash", "token_hash", unique=True),
		Index("ix_refresh_tokens_user_id", "user_id"),
		Index("ix_refresh_tokens_expires_at", "expires_at"),
	)

	id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(
		Uuid, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
	)
	token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
	expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
	revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	replaced_by_token_id: Mapped[uuid.UUID | None] = mapped_column(
		Uuid, ForeignKey("refresh_tokens.id", ondelete="SET NULL"), nullable=True
	)
	device_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
	last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

	user: Mapped[User] = relationship(back_populates="refresh_tokens")
	replaced_by: Mapped[RefreshToken | None] = relationship(remote_side=[id])
