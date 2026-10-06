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

app = FastAPI(title="Apex Sovereign Web Terminal")

# Global engine reference
config = BotConfig()
engine = SovereignTerminalEngine(config)
macro_nexus = GlobalMacroDataNexus()
recent_logs = [
    "[INIT] Sovereign 99-Tier Engine started.",
    "[DEFENSE] Citadel 99-layer matrix engaged.",
    "[STATUS] Paper Trading Simulation active with $10,000 USDT."
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
    cash = engine.router.paper_balance
    unrealized = 0.0
    for sym, pos in engine.router.positions.items():
        unrealized += pos["quantity"] * pos["entry_price"]
    total_equity = cash + unrealized

    mod = engine.defense.matrix.get_offensive_risk_modifier()

    # Calculate cumulative realized alpha & win rate
    trades = engine.router.trade_history
    win_trades = [t for t in trades if t["pnl"] > 0]
    total_realized_pnl = sum([t["pnl"] for t in trades])
    total_alpha_saved = sum([t.get("alpha_saved_usd", 0) for t in trades])
    win_rate = (len(win_trades) / len(trades) * 100) if len(trades) > 0 else 0.0

    return {
        "equity": total_equity,
        "cash": cash,
        "active_tier": mod["current_tier"],
        "tier_name": mod["tier_name"],
        "difficulty_mult": engine.defense.matrix.kinetic_tightening_factor,
        "hard_floor": config.INSOLVENCY_FLOOR_USDT,
        "positions": engine.router.positions,
        "trades_count": len(trades),
        "trade_history": trades[-20:],
        "win_rate": round(win_rate, 1),
        "total_realized_pnl": round(total_realized_pnl, 2),
        "total_alpha_saved": round(total_alpha_saved, 2),
        "recent_logs": recent_logs[-15:],
        "hft_gaps": engine.latest_hft_feed,
        "total_hft_profit": round(engine.hft.total_hft_profit, 4),
        "total_hft_captures": engine.hft.total_gap_captures,
        "hft_trades_history": engine.hft.index_trades_history[-20:],
        "whale_flow": engine.latest_whale_feed,
        "confluence_radar": engine.latest_confluence_scores
    }

@app.get("/api/reports")
async def get_performance_reports():
    return engine.router.db.get_pnl_reports()

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

@app.post("/api/trade/force-sell")
async def force_sell(symbol: str = "BTC/USDT"):
    if symbol in engine.router.positions:
        df = await engine.router.fetch_ohlcv(symbol, timeframe="1m", limit=10)
        current_price = float(df["close"].iloc[-1])
        res = await engine.router.execute_sell(symbol, "MANUAL_COMMAND", current_price)
        if res:
            engine.defense.record_trade_result(res["pnl"])
            engine.defense.update_balance(engine.router.paper_balance)
            return {"status": "SUCCESS", "message": f"Sold {symbol} at ${current_price:,.2f} with PnL ${res['pnl']:+,.2f}"}
    return {"status": "FAILED", "message": f"No open position found for {symbol}"}

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
