from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, DECIMAL, BOOLEAN, Integer, Enum, ForeignKey, func, DateTime
from sqlalchemy import UUID as sUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app import enums


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    hashed_pw: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    role: Mapped[enums.UserRole] = mapped_column(Enum(enums.UserRole), nullable=False, default=enums.UserRole.REGULAR)

    trading_systems: Mapped[list["TradingSystem"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    trades: Mapped[list["Trade"]] = relationship(back_populates="user", cascade="all, delete-orphan")


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

    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, defualt=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_onupdate=func.now(), nullable=True)

    user: Mapped["User"] = relationship(back_populates="trading_systems")
    trades: Mapped[list["Trade"]] = relationship(back_populates="trading_system")


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    trading_system_id: Mapped[UUID] = mapped_column(sUUID(as_uuid=True), ForeignKey("trading_systems.id"), nullable=False, index=True)

    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    direction: Mapped[enums.TradeDirection] = mapped_column(Enum(enums.TradeDirection), nullable=False)

    entry_price: Mapped[Decimal] = mapped_column(DECIMAL(14, 4), nullable=False)
    exit_price: Mapped[Decimal] = mapped_column(DECIMAL(14, 4), nullable=False)
    stop_loss_price: Mapped[Decimal] = mapped_column(DECIMAL(14, 4), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    opened_at: Mapped[str] = mapped_column(String(30), nullable=True)
    closed_at: Mapped[str] = mapped_column(String(30), nullable=True)

    status: Mapped[enums.TradeStatus] = mapped_column(Enum(enums.TradeStatus), nullable=False, default=enums.TradeStatus.ACTIVE)

    realized_pnl: Mapped[Decimal] = mapped_column(DECIMAL(14, 4), nullable=True)
    realized_pnl_percent: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=True)

    result_r: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=True)

    notes: Mapped[str] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_onupdate=func.now(), nullable=True)