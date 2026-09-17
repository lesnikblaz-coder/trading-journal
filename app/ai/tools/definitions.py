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
    "description": "Returns performance statistics for the authenticated user's trade, selected by SYMBOL name. Example: Only AAPL trades, etc.",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Symbol name for wanted performance statistics. Minimum length = 1, maximum length = 20"
            }
        },
        "required": ["symbol"],
    }
}