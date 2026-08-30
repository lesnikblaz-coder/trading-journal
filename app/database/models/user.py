from uuid import UUID, uuid4
from sqlalchemy import String, BOOLEAN, Enum
from sqlalchemy import UUID as sUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import enums
from app.database import models
from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    hashed_pw: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    role: Mapped[enums.UserRole] = mapped_column(Enum(enums.UserRole), nullable=False, default=enums.UserRole.REGULAR)

    trading_systems: Mapped[list["TradingSystem"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    trades: Mapped[list["Trade"]] = relationship(back_populates="user", cascade="all, delete-orphan")