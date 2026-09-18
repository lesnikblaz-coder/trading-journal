from pydantic import BaseModel, ConfigDict, Field, field_validator
from decimal import Decimal
from uuid import UUID
from datetime import datetime, date

from app import enums


class TradeCreateRequest(BaseModel):
    symbol: str
    direction: enums.TradeDirection
    entry_price: Decimal = Field(gt=0)
    exit_price: Decimal | None = Field(default=None, gt=0)
    stop_loss_price: Decimal = Field(ge=0)
    quantity: int = Field(gt=0)
    dollar_risk: Decimal = Field(gt=0)
    percent_risk: Decimal = Field(gt=0, le=100)
    opened_at: date | None = None
    closed_at: date | None = None
    status: enums.TradeStatus
    notes: str | None = None

    @field_validator("symbol")
    @classmethod
    def uppercase_symbol_name(cls, s: str) -> str:
        return s.upper().strip()

class TradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    trading_system_id: UUID
    symbol: str
    direction: enums.TradeDirection
    entry_price: Decimal
    exit_price: Decimal | None
    stop_loss_price: Decimal
    quantity: int | None = Field(default=None, gt=0)
    dollar_risk: Decimal = Field(gt=0)
    percent_risk: Decimal = Field(gt=0, le=100)
    opened_at: date | None
    closed_at: date | None
    status: enums.TradeStatus
    realized_pnl: Decimal | None
    realized_pnl_percent: Decimal | None
    result_r: Decimal | None
    notes: str | None
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
    percent_risk: Decimal | None = None
    opened_at: date | None = None
    closed_at: date | None = None
    status: enums.TradeStatus | None = None
    notes: str | None = None

    @field_validator("symbol")
    @classmethod
    def uppercase_symbol_name(cls, s: str | None) -> str | None:
        if s is None:
            return None
        return s.upper().strip()