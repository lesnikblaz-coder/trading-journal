from pydantic import BaseModel, ConfigDict, Field


class AnalyticsOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_trades: int
    winning_trades: int
    losing_trades: int
    breakevens: int
    win_rate: float
    avg_winner: float
    avg_loser: float
    profit_factor: float| None
    expectancy: float

class PerformanceRequest(BaseModel):
    year: int = Field(default=2026, ge=1800)
    month: int = Field(ge=1, le=12)