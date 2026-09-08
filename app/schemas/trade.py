from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from app import enums


class TradeCreateRequest(BaseModel):
    symbol: str
    direction: enums.TradeDirection
    entry_price: Decimal = Field(gt=0)
    exit_price: Decimal | None = Field(default=None, gt=0)
    stop_loss_price: Decimal = Field(ge=0)
    quantity: int
    dollar_risk: Decimal
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
    dollar_risk: Decimal
    realized_pnl: Decimal | None
    realized_pnl_percent: Decimal | None
    result_r: Decimal | None
    notes: str
    created_at: datetime
    updated_at: datetime | None

class TradeUpdateRequest(BaseModel):
    symbol: str | None = None
    direction: enums.TradeDirection | None = None
    entry_price: Decimal | None = Field(default=None, gt=0)
    exit_price: Decimal | None = Field(default=None, gt=0)
    stop_loss_price: Decimal | None = Field(default=None, ge=0)
    quantity: int | None = None
    dollar_risk: Decimal | None = None
    opened_at: str | None = None
    closed_at: str | None = None
    status: enums.TradeStatus | None = None
    notes: str | None = None