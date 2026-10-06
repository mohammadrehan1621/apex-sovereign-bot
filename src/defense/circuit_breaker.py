from typing import Dict, Any
from datetime import datetime
from src.sovereign_defense.matrix_99 import Apex99LayerDefenseMatrix

class DefenseProtocol:
    """
    Absolute Protocol and Defense Layer.
    Monitors capital solvency, maximum daily drawdown, and the 99-Layer Citadel Matrix.
    Escalates difficulty and counter-measures whenever deeper tiers are tested.
    """
    def __init__(self, config, alerts):
        self.config = config
        self.alerts = alerts
        self.start_capital = config.INITIAL_CAPITAL_USDT
        self.current_capital = config.INITIAL_CAPITAL_USDT
        self.peak_capital = config.INITIAL_CAPITAL_USDT
        self.daily_start_capital = config.INITIAL_CAPITAL_USDT
        self.consecutive_losses = 0
        self.is_terminated = False
        self.cooldown_active = False
        
        # Initialize the 99-Layer Defense Matrix
        self.matrix = Apex99LayerDefenseMatrix(
            initial_capital=config.INITIAL_CAPITAL_USDT,
            hard_floor=config.INSOLVENCY_FLOOR_USDT,
            alerts=alerts
        )

    def update_balance(self, new_balance: float):
        self.current_capital = new_balance
        if new_balance > self.peak_capital:
            self.peak_capital = new_balance

    async def evaluate_safety(self, total_equity: float = None) -> bool:
        """
        Runs comprehensive security and risk checks before any order execution.
        Uses Total Portfolio Equity (Cash + Market Positions) to determine health.
        """
        import sys
        if self.is_terminated:
            return False

        eval_capital = total_equity if total_equity is not None else self.current_capital
        self.current_capital = eval_capital
        if eval_capital > self.peak_capital:
            self.peak_capital = eval_capital

        # Evaluate the 99 Citadel Layers
        daily_loss_pct = (self.daily_start_capital - self.current_capital) / self.daily_start_capital
        layer_breached, layer_alert = self.matrix.assess_security_envelope(self.current_capital, daily_loss_pct)
        if layer_breached:
            await self.alerts.emit_alert("99-LAYER REINFORCEMENT ENGAGED", layer_alert, level="CRITICAL")

        # 0. Check active cooldown timer expiration
        if self.cooldown_active:
            if hasattr(self, "cooldown_until") and datetime.utcnow() >= self.cooldown_until:
                self.cooldown_active = False
                self.consecutive_losses = 0
                await self.alerts.emit_alert("COOLDOWN COMPLETED", "Tactical cooldown period ended. Normal trading resumed.", level="INFO")
            else:
                return False

        # 1. Check Absolute Insolvency Floor ("Die if it does not earn / bleeds out")
        if self.config.KILL_ON_INSOLVENCY and self.current_capital <= self.config.INSOLVENCY_FLOOR_USDT:
            self.is_terminated = True
            msg = (
                f"ALL 99 DEFENSE LAYERS EXHAUSTED.\n"
                f"Capital dropped to ${self.current_capital:.2f}, breaching hard floor "
                f"${self.config.INSOLVENCY_FLOOR_USDT:.2f}.\n"
                f"Peak Capital: ${self.peak_capital:.2f}\n"
                f"Action: Initiating omega emergency shutdown and killing process."
            )
            await self.alerts.emit_alert("ABSOLUTE DEFENSE LAYER BREACH", msg, level="TERMINATION")
            sys.exit(101)  # Terminate process permanently

        # 2. Check Daily Drawdown Circuit Breaker
        if daily_loss_pct >= self.config.MAX_DAILY_DRAWDOWN_PCT:
            self.cooldown_active = True
            from datetime import timedelta
            self.cooldown_until = datetime.utcnow() + timedelta(minutes=10)
            msg = (
                f"Daily Drawdown reached {daily_loss_pct * 100:.2f}% "
                f"(Limit: {self.config.MAX_DAILY_DRAWDOWN_PCT * 100:.2f}%).\n"
                f"Trading paused for 10 minutes to protect capital."
            )
            await self.alerts.emit_alert("CIRCUIT BREAKER TRIGGERED", msg, level="CRITICAL")
            return False

        # 3. Check Consecutive Loss Streak (60-second tactical cooldown)
        if self.consecutive_losses >= self.config.MAX_CONSECUTIVE_LOSSES:
            self.cooldown_active = True
            from datetime import timedelta
            self.cooldown_until = datetime.utcnow() + timedelta(seconds=60)
            msg = (
                f"Bot incurred {self.consecutive_losses} consecutive loss trades.\n"
                f"Market conditions unfavorable. Triggering tactical 60-second cooldown."
            )
            await self.alerts.emit_alert("STREAK DEFENSE ACTIVATED", msg, level="WARNING")
            return False

        return True

    def reset_cooldown(self):
        """Immediately clears cooldown and resets loss streak."""
        self.cooldown_active = False
        self.consecutive_losses = 0
        if hasattr(self, "cooldown_until"):
            delattr(self, "cooldown_until")

    def record_trade_result(self, pnl: float):
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
