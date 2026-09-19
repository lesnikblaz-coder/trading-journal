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