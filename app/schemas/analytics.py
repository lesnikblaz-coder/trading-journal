from uuid import UUID
from pydantic import BaseModel, ConfigDict


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