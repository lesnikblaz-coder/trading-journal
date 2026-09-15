from abc import ABC, abstractmethod

class AIClient(ABC):

    @abstractmethod
    async def generate_trade_review(self):
        pass