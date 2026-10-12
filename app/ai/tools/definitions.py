GET_PERFORMANCE_SUMMARY = {
    "type": "function",
    "name": "get_performance_summary",
    "description": "Returns performance statistics for the authenticated user's trading system.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    }
}

###

GET_PERFORMANCE_BY_MONTH = {
    "type": "function",
    "name": "get_performance_by_month",
    "description": "Returns performance statistics for authenticated user's trades for a given month.",
    "parameters": {
        "type": "object",
        "properties": {
            "year": {
                "type": "integer",
                "description": "The year to retrieve performance statistics for."
            },
            "month": {
                "type": "integer",
                "description": "The month to retrieve performance statistics for, from 1 to 12."
            }
        },
        "required": ["year", "month"],
    }
}

###

GET_PERFORMANCE_BY_SYMBOL = {
    "type": "function",
    "name": "get_performance_by_symbol",
    "description": "Returns performance statistics for the authenticated user's trading system, combined performance by symbol name. For example, all AAPL trades combined, etc. "
                   "Returns symbol name, total profit, total risk-reward result, average entry price and net quantity of shares.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    }
}

###

GET_TRADE_HISTORY = {
    "type": "function",
    "name": "get_trade_history",
    "description": "Returns the authenticated user's most recent trades for the trading system. Optionally filters trades by symbol. Defaults to the 20 most recent trades if no limit is specified.",
    "parameters": {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "The maximum number of trades to return. Defaults to 20 if not specified.",
                "minimum": 1,
                "default": 20,
                "maximum": 50
            },
            "symbol": {
                "type": ["string", "null"],
                "description": "The symbol to filter trades by, such as AAPL or TSLA. If not specified or null, trades for all symbols are returned.",
                "default": None
            }
        },
        "required": [],
    }
}