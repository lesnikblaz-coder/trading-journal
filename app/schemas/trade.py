from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from app import enums


class TradeCreateRequest(BaseModel):
    symbol: str
    direction: enums.TradeDirection
    entry_price: Decimal
    exit_price: Decimal | None = None
    stop_loss_price: Decimal
    quantity: int
    opened_at: str | None = None
    closed_at: str | None = None
    status: enums.TradeStatus
    notes: str | None = None

class TradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    trading_system_id: UUID
    symbol: str
    direction: enums.TradeDirection
    entry_price: Decimal
    exit_price: Decimal
    stop_loss_price: Decimal
    quantity: int
    opened_at: str
    closed_at: str
    status: enums.TradeStatus
    realized_pnl: Decimal | None
    realized_pnl_percent: Decimal | None
    result_r: Decimal | None
    notes: str
    created_at: datetime
    updated_at: datetime | None

class TradeUpdateRequest(BaseModel):
    symbol: str | None = None
    direction: enums.TradeDirection | None = None
    entry_price: Decimal | None = None
    exit_price: Decimal | None = None
    stop_loss_price: Decimal | None = None
    quantity: int | None = None
    opened_at: str | None = None
    closed_at: str | None = None
    status: enums.TradeStatus | None = None
    notes: str | None = None