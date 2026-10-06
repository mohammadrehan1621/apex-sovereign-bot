from pydantic import BaseModel, Field
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class BotConfig(BaseModel):
    # Mode & Environment
    MODE: str = Field(default="PAPER", description="PAPER or LIVE")
    EXCHANGE_ID: str = Field(default="binance", description="Exchange name (binance, bybit, kraken, etc.)")
    
    # API credentials (optional in paper mode)
    API_KEY: str = Field(default=os.getenv("EXCHANGE_API_KEY", ""))
    API_SECRET: str = Field(default=os.getenv("EXCHANGE_API_SECRET", ""))
    SANDBOX: bool = Field(default=True, description="Connect to exchange testnet")
    
    # Capital & Portfolio
    INITIAL_CAPITAL_USDT: float = Field(default=10000.0, description="Virtual starting balance for paper trading")
    PAIRS: List[str] = Field(default=["BTC/USDT", "ETH/USDT", "SOL/USDT"])
    TIMEFRAME: str = Field(default="1m")

    # Multi-Asset Market Class Toggles
    BOT_MARKET_FOCUS: str = Field(default="ALL", description="ALL, CRYPTO_ONLY, COMMODITIES_ONLY, INDICES_ONLY, FOREX_ONLY")
    TRADE_CRYPTO: bool = Field(default=True, description="Enable Crypto trading (BTC, ETH, SOL)")
    TRADE_INDICES: bool = Field(default=True, description="Enable Global Indices trading (S&P 500, Nasdaq, Dow, Nikkei)")
    TRADE_COMMODITIES: bool = Field(default=True, description="Enable Commodities trading (Gold, Silver, Crude Oil)")
    TRADE_FOREX: bool = Field(default=True, description="Enable Forex trading (EUR/USD, GBP/USD, USD/JPY)")
    TRADE_SWING_ALLOCATIONS: bool = Field(default=True, description="Enable or disable automated swing allocations")
    
    # Supreme Execution & Risk
    MAX_POSITION_SIZE_PCT: float = Field(default=0.15, description="Max 15% capital per single position")
    STOP_LOSS_PCT: float = Field(default=0.015, description="1.5% fixed stop loss")
    TAKE_PROFIT_PCT: float = Field(default=0.035, description="3.5% take profit (2.3+ R:R ratio)")
    TRAILING_STOP_TRIGGER_PCT: float = Field(default=0.02, description="Activate trailing stop at +2% gain")
    TRAILING_STOP_DELTA_PCT: float = Field(default=0.008, description="Trail behind high watermark by 0.8%")
    
    # Circuit Breakers & "Absolute Protocol Kill-Switch"
    MAX_DAILY_DRAWDOWN_PCT: float = Field(default=0.03, description="Shut down operations if day loss hits 3%")
    MAX_CONSECUTIVE_LOSSES: int = Field(default=4, description="Cool down if 4 losses in a row")
    KILL_ON_INSOLVENCY: bool = Field(default=True, description="Self-destruct state if total capital drops below threshold")
    INSOLVENCY_FLOOR_USDT: float = Field(default=9000.0, description="Absolute hard floor: 10% drawdown kills the bot")
    
    # Webhook Alerting (Telegram/Discord)
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=os.getenv("TELEGRAM_BOT_TOKEN", None))
    TELEGRAM_CHAT_ID: Optional[str] = Field(default=os.getenv("TELEGRAM_CHAT_ID", None))
    DISCORD_WEBHOOK_URL: Optional[str] = Field(default=os.getenv("DISCORD_WEBHOOK_URL", None))
