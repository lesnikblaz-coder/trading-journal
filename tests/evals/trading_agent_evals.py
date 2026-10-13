EVAL_CASES = [
    {
        "question": "Am I profitable overall?",
        "expected_tool": "get_performance_summary",
        "expected_behavior": "Call performance summary",
    },
    {
        "question": "Which symbol made me the most money?",
        "expected_tool": "get_performance_by_symbol",
        "expected_behavior": "Call performance by symbol",
    },
    {
        "question": "What was my expectancy in September 2026?",
        "expected_tool": "get_performance_by_month",
        "expected_behavior": "Call monthly performance",
    },
    {
        "question": "Which of my last 10 trades had the highest dollar profit?",
        "expected_tool": "get_trade_history",
        "expected_arguments": {
                    "limit": 10
        },
        "expected_behavior": "Call trade history with limit=10",
    },
    {
        "question": "Which of my last 10 trades had the highest R-multiple?",
        "expected_tool": "get_trade_history",
        "expected_arguments": {
                    "limit": 10
        },
        "expected_behavior": "Call trade history with limit=10",
    },
    {
        "question": "Can you identify possible patterns in my recent losing trades?",
        "expected_tool": "get_trade_history",
        "expected_behavior": "Retrieve trade history and avoid unsupported conclusions",
    },
    {
        "question": "What was my most profitable time of day?",
        "expected_tool": None, # no particular tool is REQUIRED
        "expected_behavior": "Acknowledge insufficient data if the available tools don't support this",
    },
    {
        "question": "Am I guaranteed to be profitable next month?",
        "expected_tool": None, # no particular tool is REQUIRED
        "expected_behavior": "Avoid making guarantees about future results",
    },
]