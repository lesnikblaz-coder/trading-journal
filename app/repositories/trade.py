from app.repositories.base import BaseRepo
from app.database.models.trade import Trade


class TradeRepo(BaseRepo):
    model = Trade

    pass