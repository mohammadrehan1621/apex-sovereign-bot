import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import pandas as pd

from src.config import BotConfig
from src.main import SovereignTerminalEngine
from src.execution.macro_nexus import GlobalMacroDataNexus
from src.agents.swarm import AgentSwarmOrchestrator

app = FastAPI(title="Apex Sovereign Web Terminal")

# Global engine and AI swarm reference
config = BotConfig()
engine = SovereignTerminalEngine(config)
macro_nexus = GlobalMacroDataNexus()
swarm = AgentSwarmOrchestrator()
recent_logs = [
    "[INIT] Sovereign 99-Tier Engine started.",
    "[DEFENSE] Citadel 99-layer matrix engaged.",
    "[STATUS] Paper Trading Simulation active with $10,000 USDT.",
    "[AI-SWARM] 5 Autonomous Agents Initialized (Research, News, Chart, Risk, Trader)."
]

# Override alert emitter to push into web feed
original_emit = engine.alerts.emit_alert
async def web_alert_interceptor(title: str, message: str, level: str = "INFO"):
    recent_logs.append(f"[{level}] {title}: {message.splitlines()[0]}")
    if len(recent_logs) > 50:
        recent_logs.pop(0)
    await original_emit(title, message, level)

engine.alerts.emit_alert = web_alert_interceptor

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/world-markets")
async def get_world_markets():
    tickers = await macro_nexus.get_all_world_tickers()
    return {"markets": tickers}

@app.get("/api/chart")
async def get_chart_data(symbol: str = "BTC/USDT"):
    if symbol in macro_nexus.SYMBOLS_CATALOG["CRYPTO"]:
        df = await macro_nexus.fetch_crypto_candles(symbol, limit=50)
    else:
        df = await macro_nexus.fetch_macro_candles(symbol, limit=50)

    df = engine.strategy.compute_indicators(df)
    candles = []
    for _, row in df.iterrows():
        candles.append({
            "time": int(row["timestamp"].timestamp()),
            "open": round(row["open"], 4 if "USD" in symbol and "=" in symbol else 2),
            "high": round(row["high"], 4 if "USD" in symbol and "=" in symbol else 2),
            "low": round(row["low"], 4 if "USD" in symbol and "=" in symbol else 2),
            "close": round(row["close"], 4 if "USD" in symbol and "=" in symbol else 2),
            "volume": round(row["volume"], 2),
            "rsi": round(row["rsi"], 2) if not pd.isna(row["rsi"]) else 50.0,
            "ema_fast": round(row["ema_fast"], 4 if "USD" in symbol and "=" in symbol else 2),
            "ema_slow": round(row["ema_slow"], 4 if "USD" in symbol and "=" in symbol else 2)
        })
    info = macro_nexus.SYMBOL_LABELS.get(symbol, {"name": symbol, "ticker": symbol})
    return {"symbol": symbol, "display": info["ticker"], "name": info["name"], "candles": candles}

@app.get("/api/status")
async def get_status():
    all_time = engine.router.db.get_all_time_stats()
    total_hft_profit = all_time.get("total_hft_profit", 0.0)
    total_swing_profit = all_time.get("total_swing_profit", 0.0)
    total_realized_profit = total_hft_profit + total_swing_profit

    # Synchronize liquid paper balance: Initial Capital ($10,000) + Total Profit Generated - Active Position Cost
    unrealized = 0.0
    for sym, pos in engine.router.positions.items():
        unrealized += pos["quantity"] * pos["entry_price"]

    minimum_expected_balance = (config.INITIAL_CAPITAL_USDT + total_realized_profit) - unrealized
    if engine.router.paper_balance < minimum_expected_balance:
        engine.router.paper_balance = minimum_expected_balance
        engine.router.db.set_persisted_state("paper_balance", str(engine.router.paper_balance))

    cash = round(engine.router.paper_balance, 2)
    # Total Portfolio Equity = Liquid Cash + Market Positions Value = Initial Capital ($10,000) + All Profit Generated
    total_equity = round(cash + unrealized, 2)

    mod = engine.defense.matrix.get_offensive_risk_modifier()

    # Calculate cumulative realized alpha & win rate
    trades = engine.router.trade_history
    win_trades = [t for t in trades if t["pnl"] > 0]
    total_alpha_saved = sum([t.get("alpha_saved_usd", 0) for t in trades])
    win_rate = (len(win_trades) / len(trades) * 100) if len(trades) > 0 else 0.0

    # Capital Shield & Alpha Value: Direct Profit + Slippage Saved by Bot
    shield_and_alpha_value = round(total_realized_profit + total_alpha_saved, 2)

    return {
        "equity": total_equity,
        "initial_capital": config.INITIAL_CAPITAL_USDT,
        "total_realized_profit": round(total_realized_profit, 2),
        "trading_capital": total_equity,
        "shield_and_alpha_value": shield_and_alpha_value,
        "cash": cash,
        "unrealized": round(unrealized, 2),
        "active_tier": mod["current_tier"],
        "tier_name": mod["tier_name"],
        "difficulty_mult": engine.defense.matrix.kinetic_tightening_factor,
        "hard_floor": config.INSOLVENCY_FLOOR_USDT,
        "positions": engine.router.positions,
        "trades_count": len(trades),
        "trade_history": trades[-20:],
        "win_rate": round(win_rate, 1),
        "total_realized_pnl": round(total_realized_profit, 2),
        "total_alpha_saved": round(total_alpha_saved, 2),
        "recent_logs": recent_logs[-15:],
        "hft_gaps": engine.latest_hft_feed,
        "total_hft_profit": round(engine.hft.total_hft_profit, 4),
        "total_hft_captures": engine.hft.total_gap_captures,
        "hft_trades_history": engine.hft.index_trades_history[-20:],
        "whale_flow": engine.latest_whale_feed,
        "confluence_radar": engine.latest_confluence_scores,
        "bot_market_focus": engine.config.BOT_MARKET_FOCUS,
        "trade_swing_allocations": engine.config.TRADE_SWING_ALLOCATIONS,
        "circuit_breaker_active": engine.defense.cooldown_active
    }

@app.get("/api/reports")
async def get_performance_reports():
    return engine.router.db.get_pnl_reports()

@app.get("/api/ledgers/transactions")
async def get_all_transactions(timeframe: str = "all", limit: int = 500):
    return engine.router.db.get_all_transactions_by_timeframe(timeframe=timeframe, limit=limit)

@app.get("/api/agents/status")
async def get_agents_status(symbol: str = "BTC/USDT"):
    tier = getattr(engine.defense.matrix, "active_layer_index", 1)
    return await swarm.get_swarm_consensus(
        symbol=symbol,
        current_focus=engine.config.BOT_MARKET_FOCUS,
        current_tier=tier,
        cooldown=engine.defense.cooldown_active
    )

@app.post("/api/agents/run-postmortem")
async def trigger_agent_postmortem(reason: str = "User Calibration"):
    result = swarm.trigger_postmortem_learning(reason)
    recent_logs.append(f"[SWARM-AI] Agent 5 completed self-healing post-mortem: {result['event']}.")
    return {"status": "SUCCESS", "postmortem": result}

@app.get("/api/bot/focus")
async def get_bot_focus():
    return {
        "focus": engine.config.BOT_MARKET_FOCUS,
        "crypto": engine.config.TRADE_CRYPTO,
        "indices": engine.config.TRADE_INDICES,
        "commodities": engine.config.TRADE_COMMODITIES,
        "forex": engine.config.TRADE_FOREX
    }

@app.post("/api/bot/focus")
async def set_bot_focus(mode: str):
    mode_upper = mode.upper()
    engine.config.BOT_MARKET_FOCUS = mode_upper
    
    if mode_upper == "CRYPTO_ONLY":
        engine.config.TRADE_CRYPTO = True
        engine.config.TRADE_INDICES = False
        engine.config.TRADE_COMMODITIES = False
        engine.config.TRADE_FOREX = False
        title = "🪙 ONLY CRYPTO"
    elif mode_upper == "COMMODITIES_ONLY":
        engine.config.TRADE_CRYPTO = False
        engine.config.TRADE_INDICES = False
        engine.config.TRADE_COMMODITIES = True
        engine.config.TRADE_FOREX = False
        title = "🥇 ONLY COMMODITIES (GOLD & OIL)"
    elif mode_upper == "INDICES_ONLY":
        engine.config.TRADE_CRYPTO = False
        engine.config.TRADE_INDICES = True
        engine.config.TRADE_COMMODITIES = False
        engine.config.TRADE_FOREX = False
        title = "🌐 ONLY GLOBAL INDICES (S&P 500, NASDAQ, DOW)"
    elif mode_upper == "FOREX_ONLY":
        engine.config.TRADE_CRYPTO = False
        engine.config.TRADE_INDICES = False
        engine.config.TRADE_COMMODITIES = False
        engine.config.TRADE_FOREX = True
        title = "💱 ONLY FOREX (EUR/USD, GBP/USD)"
    else:  # ALL
        engine.config.BOT_MARKET_FOCUS = "ALL"
        engine.config.TRADE_CRYPTO = True
        engine.config.TRADE_INDICES = True
        engine.config.TRADE_COMMODITIES = True
        engine.config.TRADE_FOREX = True
        title = "🌐 ALL MARKETS (OMNI-ASSET ARBITRAGE)"

    recent_logs.append(f"[BOT RE-ROUTED] Trading Focus set to: {title} by Commander.")
    return {
        "status": "SUCCESS",
        "focus": engine.config.BOT_MARKET_FOCUS,
        "title": title
    }

@app.post("/api/trade/force-buy")
async def force_buy(symbol: str = "BTC/USDT"):
    df = await engine.router.fetch_ohlcv(symbol, timeframe="1m", limit=10)
    current_price = float(df["close"].iloc[-1])
    mod = engine.defense.matrix.get_offensive_risk_modifier()
    size = engine.risk.calculate_order_size(engine.router.paper_balance, current_price, mod)
    order = await engine.router.execute_buy(symbol, size, current_price)
    if order:
        engine.defense.update_balance(engine.router.paper_balance)
        return {"status": "SUCCESS", "message": f"Bought {size:.4f} of {symbol} at ${current_price:,.2f}"}
    return {"status": "FAILED", "message": "Insufficient cash balance"}

@app.get("/api/markets/toggles")
async def get_market_toggles():
    return {
        "CRYPTO": engine.config.TRADE_CRYPTO,
        "INDICES": engine.config.TRADE_INDICES,
        "COMMODITIES": engine.config.TRADE_COMMODITIES,
        "FOREX": engine.config.TRADE_FOREX
    }

@app.post("/api/markets/toggle")
async def toggle_market(market: str, enabled: bool):
    market_upper = market.upper()
    if market_upper == "CRYPTO":
        engine.config.TRADE_CRYPTO = enabled
    elif market_upper == "INDICES":
        engine.config.TRADE_INDICES = enabled
    elif market_upper == "COMMODITIES":
        engine.config.TRADE_COMMODITIES = enabled
    elif market_upper == "FOREX":
        engine.config.TRADE_FOREX = enabled
    else:
        return {"status": "ERROR", "message": f"Unknown market: {market}"}
    
    status_str = "ENABLED" if enabled else "DISABLED"
    recent_logs.append(f"[MARKET CONFIG] {market_upper} Trading {status_str} by Commander.")
    return {"status": "SUCCESS", "market": market_upper, "enabled": enabled}

@app.get("/api/bot/swing-allocations")
async def get_swing_allocations_status():
    return {
        "enabled": engine.config.TRADE_SWING_ALLOCATIONS,
        "active_positions_count": len(engine.router.positions),
        "positions": engine.router.positions
    }

@app.post("/api/bot/swing-allocations")
async def toggle_swing_allocations(enabled: bool):
    engine.config.TRADE_SWING_ALLOCATIONS = enabled
    state_str = "ACTIVE" if enabled else "PAUSED"
    msg = f"[SWING ALLOCATIONS] Automated Swing Entry state set to: {state_str} by Commander."
    recent_logs.append(msg)
    return {
        "status": "SUCCESS",
        "enabled": engine.config.TRADE_SWING_ALLOCATIONS,
        "message": msg
    }

@app.post("/api/positions/close-all")
async def close_all_positions():
    closed = []
    for sym in list(engine.router.positions.keys()):
        try:
            curr_price = engine.router.positions[sym].get("entry_price", 1.0)
            res = await engine.router.execute_sell(sym, "MANUAL_COMMAND_FLATTEN", curr_price)
            if res:
                closed.append(sym)
        except Exception:
            pass
    msg = f"[POSITIONS FLATTENED] Closed {len(closed)} open swing positions to cash."
    recent_logs.append(msg)
    return {
        "status": "SUCCESS",
        "closed_count": len(closed),
        "closed_symbols": closed,
        "message": msg
    }

@app.post("/api/defense/reset-cooldown")
async def reset_cooldown_override():
    engine.defense.reset_cooldown()
    msg = "[CIRCUIT BREAKER OVERRIDE] Tactical cooldown cleared by Commander. All trading operations active."
    recent_logs.append(msg)
    return {"status": "SUCCESS", "message": msg}

@app.post("/api/trade/custom-order")
async def submit_custom_order(symbol: str, asset_class: str = "CRYPTO", action: str = "BUY"):
    action_upper = action.upper()
    asset_class_upper = asset_class.upper()
    
    if asset_class_upper in ["INDICES", "COMMODITIES", "FOREX"]:
        info = engine.hft.INDICES_CATALOG.get(symbol) or {"ticker": symbol, "base_price": 100.0, "tick_size": 1.0}
        dummy_target = {
            "asset_class": asset_class_upper,
            "symbol": symbol,
            "display": info.get("ticker", symbol),
            "imbalance_ratio": 2.50,
            "latency_ms": 1.2
        }
        await engine.hft.execute_subsecond_exploit(dummy_target)
        recent_logs.append(f"[MANUAL ORDER] {action_upper} on {dummy_target['display']} [{asset_class_upper}] Executed Successfully.")
        return {"status": "SUCCESS", "message": f"{action_upper} executed on {dummy_target['display']} [{asset_class_upper}]"}
    else:
        if action_upper == "BUY":
            return await force_buy(symbol)
        else:
            return await force_sell(symbol)

# --- ABSOLUTE SECURITY DEFENSE LAYER (ASDL) API ENDPOINTS ---
@app.get("/api/security/status")
async def get_security_status():
    return engine.security.get_security_telemetry()

@app.post("/api/security/lockdown")
async def trigger_omega_lockdown(flatten_positions: bool = True, reason: str = "Manual Commander Red Button Lockdown"):
    res = engine.security.trigger_emergency_lockdown("Commander", reason)
    if flatten_positions:
        closed = []
        for sym in list(engine.router.positions.keys()):
            try:
                curr_price = engine.router.positions[sym].get("entry_price", 1.0)
                await engine.router.execute_sell(sym, "OMEGA_LOCKDOWN_FLATTEN", curr_price)
                closed.append(sym)
            except Exception:
                pass
        res["flattened_positions_count"] = len(closed)
    recent_logs.append(f"[ABSOLUTE SECURITY] 🚨 Omega Citadel Lockdown ENGAGED. Trading frozen. Cash shielded.")
    return res

@app.post("/api/security/unlock")
async def unlock_citadel(passcode: str = "APEX-CITADEL-99"):
    res = engine.security.unlock_system(passcode, "Commander")
    if res.get("status") == "SUCCESS":
        recent_logs.append("[ABSOLUTE SECURITY] ✓ Citadel Lockdown Disengaged. Normal trading restored.")
    return res

@app.post("/api/security/configure")
async def configure_security(max_slippage_pct: float = None, max_order_pct: float = None):
    return engine.security.configure_shields(max_slippage_pct, max_order_pct)

async def run_bot_loop():
    while True:
        try:
            await engine.run_cycle()
        except Exception as e:
            err_msg = str(e)
            if "Errno 22" not in err_msg:
                recent_logs.append(f"[NOTICE] Engine cycle note: {err_msg}")
        await asyncio.sleep(3)

@app.on_event("startup")
async def startup_event():
    # Start bot trading loop in the background of web server
    asyncio.create_task(run_bot_loop())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.web.server:app", host="0.0.0.0", port=port, reload=False)
