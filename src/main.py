import asyncio
import sys
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

from src.config import BotConfig
from src.telemetry.alerts import TelemetryAlerts
from src.defense.circuit_breaker import DefenseProtocol
from src.risk.risk_engine import RiskEngine
from src.strategies.supreme_ultra_strategy import SupremeUltraWinStrategy
from src.strategies.whale_flow import WhaleMomentumTracker
from src.strategies.multi_asset_hft import MultiAssetMacroHFTMatrix
from src.execution.router import ExecutionRouter

console = Console(force_terminal=True, legacy_windows=False)

class SovereignTerminalEngine:
    def __init__(self, config: BotConfig):
        self.config = config
        self.alerts = TelemetryAlerts(
            telegram_token=config.TELEGRAM_BOT_TOKEN,
            chat_id=config.TELEGRAM_CHAT_ID,
            discord_url=config.DISCORD_WEBHOOK_URL
        )
        self.defense = DefenseProtocol(config, self.alerts)
        self.risk = RiskEngine(config)
        self.strategy = SupremeUltraWinStrategy()
        self.whale_tracker = WhaleMomentumTracker()
        self.router = ExecutionRouter(config, self.alerts)
        self.hft = MultiAssetMacroHFTMatrix(self.router, self.risk, self.defense, self.alerts)
        self.iteration = 0
        self.latest_hft_feed: Dict[str, Any] = {}
        self.latest_whale_feed: Dict[str, Any] = {}
        self.latest_confluence_scores: Dict[str, Any] = {}

    def generate_dashboard(self) -> Table:
        table = Table(title="[bold yellow]>>> APEX SOVEREIGN 99-LAYER CITADEL TERMINAL v2.0.0 <<<[/bold yellow]", border_style="cyan")
        table.add_column("Metric / Fortress Status", style="bold white")
        table.add_column("Absolute Value / Reinforcement", style="bold green")

        # Portfolio metrics
        cash = self.router.paper_balance
        unrealized = 0.0
        for sym, pos in self.router.positions.items():
            unrealized += pos["quantity"] * pos["entry_price"]
        total_equity = cash + unrealized

        mod = self.defense.matrix.get_offensive_risk_modifier()
        active_layer = mod["current_tier"]
        tier_title = mod["tier_name"]

        table.add_row("Execution Engine Mode", f"[bold magenta]{self.config.MODE}[/bold magenta]")
        table.add_row("Total Portfolio Equity", f"[bold cyan]${total_equity:,.2f} USDT[/bold cyan]")
        table.add_row("Active Defense Tier", f"[bold red]{tier_title} (Layer {active_layer}/99)[/bold red]")
        table.add_row("Kinetic Defense Hardening", f"[bold yellow]{self.defense.matrix.kinetic_tightening_factor:.3f}x Difficulty Escalation[/bold yellow]")
        table.add_row("Offensive Position Sizing Scale", f"{mod['position_size_scale'] * 100:.1f}% Allocation Capacity")
        table.add_row("Dynamic Stop Loss Clamp", f"{mod['stop_loss_tighten_pct'] * 100:.2f}% (Auto-Tightened)")
        table.add_row("Active Positions Count", str(len(self.router.positions)))
        table.add_row("Hard Floor Kill-Switch Limit", f"[bold red]${self.config.INSOLVENCY_FLOOR_USDT:,.2f} USDT[/bold red]")
        table.add_row("Circuit Breaker Status", "[bold green]OPERATIONAL & SECURE[/bold green]" if not self.defense.cooldown_active else "[bold red]COOLDOWN HALTED[/bold red]")
        table.add_row("Monitored Market Pairs", ", ".join(self.config.PAIRS))
        table.add_row("Engine Cycles Completed", str(self.iteration))
        
        return table

    async def run_cycle(self):
        self.iteration += 1

        # Calculate live total portfolio equity (cash + unrealized position values)
        cash = self.router.paper_balance
        unrealized = 0.0
        for sym, pos in self.router.positions.items():
            unrealized += pos["quantity"] * pos["entry_price"]
        total_equity = cash + unrealized
        self.defense.update_balance(total_equity)

        # 1. Evaluate Defense Layer before touching anything with total equity
        is_safe = await self.defense.evaluate_safety(total_equity=total_equity)
        if not is_safe:
            return

        modifier = self.defense.matrix.get_offensive_risk_modifier()

        # Sub-second Multi-Asset Execution Sweep (Indices, Commodities, Forex)
        for idx_sym in list(self.hft.INDICES_CATALOG.keys()):
            try:
                cat = "INDICES" if "^" in idx_sym else ("COMMODITIES" if "=" in idx_sym and not "USD" in idx_sym else "FOREX")
                if cat == "INDICES" and not self.config.TRADE_INDICES:
                    continue
                if cat == "COMMODITIES" and not self.config.TRADE_COMMODITIES:
                    continue
                if cat == "FOREX" and not self.config.TRADE_FOREX:
                    continue

                idx_gap = await self.hft.scan_index_gap(idx_sym)
                if idx_gap:
                    self.latest_hft_feed[idx_sym] = idx_gap
                    await self.hft.execute_subsecond_exploit(idx_gap)
            except Exception:
                pass

        # Crypto Trading & Strategy Execution Sweep (BTC, ETH, SOL)
        if self.config.TRADE_CRYPTO:
            for symbol in self.config.PAIRS:
                try:
                    # Sub-second Crypto Price-Gap & Imbalance Scan
                    gap = await self.hft.scan_crypto_gap(symbol)
                    if gap:
                        self.latest_hft_feed[symbol] = gap
                        await self.hft.execute_subsecond_exploit(gap)

                    # Institutional Whale Order Flow Scan
                    whale = await self.whale_tracker.scan_whale_flow(symbol)
                    if whale:
                        self.latest_whale_feed[symbol] = whale

                    # Live OHLCV candlestick technical computation
                    df = await self.router.fetch_ohlcv(symbol, timeframe=self.config.TIMEFRAME, limit=60)
                    df = self.strategy.compute_indicators(df)
                    current_price = float(df["close"].iloc[-1])

                    # 85%+ Confluence Evaluation
                    confluence = self.strategy.evaluate_supreme_confluence(df, whale)
                    self.latest_confluence_scores[symbol] = confluence

                    # 3. Check existing positions for Exit / Stop-Loss / Take-Profit
                    if symbol in self.router.positions:
                        pos = self.router.positions[symbol]
                        exit_signal = self.risk.check_position_exit(pos, current_price, modifier)
                        
                        if exit_signal:
                            res = await self.router.execute_sell(symbol, exit_signal, current_price)
                            if res:
                                self.defense.record_trade_result(res["pnl"])
                                self.defense.update_balance(self.router.paper_balance)
                        elif confluence["signal"] == "SELL":
                            res = await self.router.execute_sell(symbol, "WHALE_DISTRIBUTION_EXIT", current_price)
                            if res:
                                self.defense.record_trade_result(res["pnl"])
                                self.defense.update_balance(self.router.paper_balance)

                    # 4. Check for New High-Probability 85%+ Sniper Entry
                    else:
                        if confluence["signal"] == "BUY" and confluence["probability_score"] >= 85:
                            size = self.risk.calculate_order_size(self.router.paper_balance, current_price, modifier)
                            await self.router.execute_buy(symbol, size, current_price)
                            self.defense.update_balance(self.router.paper_balance)
                except Exception:
                    pass

    async def start(self, max_cycles: int = 0):
        console.print(Panel(
            "[bold green]INITIATING APEX SOVEREIGN CORE ENGINE[/bold green]\n"
            "[white]Absolute Protocol Active | Defense Layer Engaged | Market Surveillance Online[/white]",
            border_style="gold1"
        ))
        await self.alerts.emit_alert("SYSTEM ONLINE", "Apex Sovereign Terminal initialized and active.", level="INFO")

        cycle_count = 0
        try:
            while True:
                await self.run_cycle()
                console.print(self.generate_dashboard())
                cycle_count += 1
                if max_cycles > 0 and cycle_count >= max_cycles:
                    break
                await asyncio.sleep(3)  # Fast tactical polling cycle
        finally:
            await self.router.close()

if __name__ == "__main__":
    cfg = BotConfig()
    engine = SovereignTerminalEngine(cfg)
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]Engine manually stopped by commander.[/yellow]")
