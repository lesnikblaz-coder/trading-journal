from app.schemas.ai import AITradeReviewInput

def build_trade_review_prompt(data: AITradeReviewInput) -> str:
    return f"""
TRADING SYSTEM

Name: {data.trading_system.name}
Description: {data.trading_system.description}
Asset class: {data.trading_system.asset_class}
Timeframe: {data.trading_system.timeframe}

Setup requirements:
{data.trading_system.setup_requirements}

Entry rules:
{data.trading_system.entry_rules}

Stop-loss rules:
{data.trading_system.stop_loss_rules}

Take-profit rules:
{data.trading_system.take_profit_rules}

Break-even rules:
{data.trading_system.break_even_rules}

Additional rules:
{data.trading_system.additional_rules}


TRADE

Symbol: {data.trade.symbol}
Direction: {data.trade.direction}

Entry price: {data.trade.entry_price}
Exit price: {data.trade.exit_price}
Stop-loss price: {data.trade.stop_loss_price}

Quantity: {data.trade.quantity}
Dollar risk: {data.trade.dollar_risk}

Opened at: {data.trade.opened_at}
Closed at: {data.trade.closed_at}

Realized P&L: {data.trade.realized_pnl}
Realized P&L %: {data.trade.realized_pnl_percent}
Result R: {data.trade.result_r}

Trader notes:
{data.trade.notes}
"""