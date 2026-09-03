from decimal import Decimal
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import DECIMAL, String, Enum, ForeignKey, Integer, DateTime, func
from sqlalchemy import UUID as sUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import enums
from app.database import models
from app.database.base import Base



class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    trading_system_id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), ForeignKey("trading_systems.id"), nullable=False, index=True)

    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    direction: Mapped[enums.TradeDirection] = mapped_column(Enum(enums.TradeDirection), nullable=False)

    entry_price: Mapped[Decimal] = mapped_column(DECIMAL(14, 4), nullable=False)
    exit_price: Mapped[Decimal] = mapped_column(DECIMAL(14, 4), nullable=True)
    stop_loss_price: Mapped[Decimal] = mapped_column(DECIMAL(14, 4), nullable=False)

    quantity: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False)
    dollar_risk: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False)

    opened_at: Mapped[str] = mapped_column(String(30), nullable=True)
    closed_at: Mapped[str] = mapped_column(String(30), nullable=True)

    status: Mapped[enums.TradeStatus] = mapped_column(Enum(enums.TradeStatus), nullable=False, default=enums.TradeStatus.ACTIVE)

    realized_pnl: Mapped[Decimal] = mapped_column(DECIMAL(14, 4), nullable=True)
    realized_pnl_percent: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=True)

    result_r: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=True)

    notes: Mapped[str] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_onupdate=func.now(), nullable=True)

    user: Mapped["User"] = relationship(back_populates="trades")
    trading_system: Mapped["TradingSystem"] = relationship(back_populates="trades")