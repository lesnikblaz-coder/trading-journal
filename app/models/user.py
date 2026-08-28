from uuid import UUID, uuid4
from sqlalchemy import String, BOOLEAN, Enum
from sqlalchemy import UUID as sUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    hashed_pw: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.REGULAR)