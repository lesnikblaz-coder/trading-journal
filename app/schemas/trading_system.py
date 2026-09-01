from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from app import enums


class TradingSystemResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str
    asset_class: enums.AssetClass
    timeframe: enums.TradeTimeframe
    setup_requirements: str
    entry_rules: str
    stop_loss_rules: str
    take_profit_rules: str
    break_even_rules: str
    additional_rules: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

class TradingSystemRequest(BaseModel):
    name: str
    description: str
    asset_class: enums.AssetClass
    timeframe: enums.TradeTimeframe
    setup_requirements: str
    entry_rules: str
    stop_loss_rules: str
    take_profit_rules: str
    break_even_rules: str
    additional_rules: str