from pydantic import BaseModel


class AITradeReviewResponse(BaseModel):
    setup_quality: int
    followed_rules: bool
    violations: list[str]
    summary: str