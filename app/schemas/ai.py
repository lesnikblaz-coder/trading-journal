from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from decimal import Decimal

from app import enums as e


class AITradeReviewResponse(BaseModel):
    setup_quality: int
    followed_rules: bool
    violations: list[str]
    summary: str

class TradeInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Trade
    symbol: str
    direction: e.TradeDirection
    entry_price: Decimal
    exit_price: Decimal | None
    stop_loss_price: Decimal
    quantity: Decimal
    dollar_risk: Decimal
    opened_at: date | None
    closed_at: date | None
    realized_pnl: Decimal | None
    realized_pnl_percent: Decimal | None
    result_r: Decimal | None
    notes: str | None

class TradingSystemInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Trading system
    name: str
    description: str | None
    asset_class: e.AssetClass
    timeframe: e.TradeTimeframe
    setup_requirements: str
    entry_rules: str
    stop_loss_rules: str | None
    take_profit_rules: str | None
    break_even_rules: str | None
    additional_rules: str | None

class AITradeReviewInput(BaseModel):
    trade: TradeInput
    trading_system: TradingSystemInput

class AIAnalysisRequest(BaseModel):
    question: str

class AIAnalysisResponse(BaseModel):
    answer: str


###
class AIArgumentValidations(BaseModel):
    """
    Base class to validate AI's requested arguments for function calling.
    """
    model_config = ConfigDict(extra="forbid")

class MonthSummaryArg(AIArgumentValidations):
    year: int
    month: int = Field(ge=1, le=12)

class SymbolSummaryArg(AIArgumentValidations):
    symbol: str = Field(min_length= 1, max_length=20)