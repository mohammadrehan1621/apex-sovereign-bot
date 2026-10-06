from typing import Dict, Any, Optional

class RiskEngine:
    """
    Capital Preservation and Dynamic Sizing Module.
    Calculates exact position sizing based on risk volatility and account equity.
    Enforces stop loss, dynamic take-profit, and trailing stops.
    """
    def __init__(self, config):
        self.config = config

    def calculate_order_size(self, current_capital: float, current_price: float, modifier: Optional[Dict[str, float]] = None) -> float:
        """
        Determines position size allocation while strictly adhering to max exposure limit
        and scaling down as defense layers get penetrated.
        """
        scale = modifier.get("position_size_scale", 1.0) if modifier else 1.0
        allocation_value = (current_capital * self.config.MAX_POSITION_SIZE_PCT) * scale
        raw_quantity = allocation_value / current_price
        return raw_quantity

    def check_position_exit(self, position: Dict[str, Any], current_price: float, modifier: Optional[Dict[str, float]] = None) -> Optional[str]:
        """
        Evaluates active open position against Stop Loss, Take Profit, and Trailing Stop.
        Dynamically tightens stop loss when under higher defense pressure.
        """
        entry_price = position["entry_price"]
        high_price = position.get("high_watermark", entry_price)
        
        # Determine dynamic stop loss threshold
        stop_loss_pct = modifier.get("stop_loss_tighten_pct", self.config.STOP_LOSS_PCT) if modifier else self.config.STOP_LOSS_PCT
        
        # Update high watermark
        if current_price > high_price:
            position["high_watermark"] = current_price
            high_price = current_price

        # 1. Hard Stop Loss (Dynamically escalated)
        loss_pct = (entry_price - current_price) / entry_price
        if loss_pct >= stop_loss_pct:
            return "STOP_LOSS"

        # 2. Hard Take Profit
        gain_pct = (current_price - entry_price) / entry_price
        if gain_pct >= self.config.TAKE_PROFIT_PCT:
            return "TAKE_PROFIT"

        # 3. Trailing Stop Loss
        # Triggered only when gain passed threshold, then drops by delta
        if (high_price - entry_price) / entry_price >= self.config.TRAILING_STOP_TRIGGER_PCT:
            trail_drop_pct = (high_price - current_price) / high_price
            if trail_drop_pct >= self.config.TRAILING_STOP_DELTA_PCT:
                return "TRAILING_STOP"

        return None
