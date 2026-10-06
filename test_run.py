import asyncio
from src.config import BotConfig
from src.main import SovereignTerminalEngine

async def run_dry_test():
    print("Testing Apex Sovereign Protocol components...")
    cfg = BotConfig(
        INITIAL_CAPITAL_USDT=10000.0,
        INSOLVENCY_FLOOR_USDT=9000.0,
        PAIRS=["BTC/USDT", "ETH/USDT"],
        TIMEFRAME="1m"
    )
    engine = SovereignTerminalEngine(cfg)
    
    # Run exactly 2 tactical cycles to verify pipeline, math, and rendering
    await engine.start(max_cycles=2)
    print("Dry-run test completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_dry_test())
