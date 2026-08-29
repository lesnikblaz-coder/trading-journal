from enum import StrEnum


class UserRole(StrEnum):
    REGULAR = "REGULAR"
    ADMIN = "ADMIN"
    STAFF = "STAFF"

class AssetClass(StrEnum):
    ALL = "ALL"
    STOCKS = "STOCKS"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"
    ETFS = "ETFS"
    COMMODITIES = "COMMODITIES"

class TradeTimeframe(StrEnum):
    ONE_MINUTE = "1m"
    FIVE_MINUTE = "5m"
    FIFTEEN_MINUTE = "15m"
    THIRTY_MINUTE = "30m"
    ONE_HOUR = "1h"
    FOUR_HOUR = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1month"
    SIX_MONTH = "6month"

class TradeDirection(StrEnum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"

class TradeStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"