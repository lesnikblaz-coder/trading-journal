from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, BOOLEAN, Enum, ForeignKey, func, DateTime
from sqlalchemy import UUID as sUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import enums
from app.database import models
from app.database.base import Base


class TradingSystem(Base):
    __tablename__ = "trading_systems"

    id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)

    asset_class: Mapped[enums.AssetClass] = mapped_column(Enum(enums.AssetClass), nullable=False, default=enums.AssetClass.ALL)
    timeframe: Mapped[enums.TradeTimeframe] = mapped_column(Enum(enums.TradeTimeframe), nullable=False)

    setup_requirements: Mapped[str] = mapped_column(String(300), nullable=False)
    entry_rules: Mapped[str] = mapped_column(String(100), nullable=False)
    stop_loss_rules: Mapped[str] = mapped_column(String(100), nullable=True)
    take_profit_rules: Mapped[str] = mapped_column(String(100), nullable=True)
    break_even_rules: Mapped[str] = mapped_column(String(100), nullable=True)
    additional_rules: Mapped[str] = mapped_column(String(200), nullable=True)

    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_onupdate=func.now(), nullable=True)

    user: Mapped["User"] = relationship(back_populates="trading_systems")
    trades: Mapped[list["Trade"]] = relationship(back_populates="trading_system")