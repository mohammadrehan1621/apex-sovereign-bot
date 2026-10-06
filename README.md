# 👑 APEX SOVEREIGN ALGORITHMIC TERMINAL (v1.0.0)
> *The Supreme Algorithmic Market Execution & Defense Protocol.*

---

## 🏛️ Architecture Overview

The **Apex Sovereign Terminal** is architected to operate at institutional standards, integrating multi-factor quantitative modeling, active volatility envelope positioning, and an **Absolute Protocol Defense Layer**.

```
                           ┌───────────────────────────┐
                           │      MARKET DATA FEED     │
                           │  (Binance / Bybit / CCXT) │
                           └─────────────┬─────────────┘
                                         │
                                         ▼
                           ┌───────────────────────────┐
                           │   SUPREME ALPHA STRATEGY  │
                           │ (EMA Cross + RSI + BBands)│
                           └─────────────┬─────────────┘
                                         │
                                         ▼
                           ┌───────────────────────────┐
                           │   ABSOLUTE DEFENSE LAYER  │
                           │  • Insolvency Floor       │
                           │  • Daily Drawdown Circuit │
                           │  • Consecutive Loss Limit │
                           └─────────────┬─────────────┘
                                         │
                                         ▼
                           ┌───────────────────────────┐
                           │      RISK & SIZING        │
                           │  • Max Exposure (15%)     │
                           │  • Hard Stop Loss (1.5%)  │
                           │  • Trailing Stop Profit   │
                           └─────────────┬─────────────┘
                                         │
                                         ▼
                           ┌───────────────────────────┐
                           │     EXECUTION ROUTER      │
                           │  [PAPER SIM]  /  [LIVE]   │
                           └───────────────────────────┘
```

---

## 🛡️ The Absolute Defense Protocol (Kill-Switch)

In alignment with your supreme mandate:

1. **Hard Insolvency Floor (`INSOLVENCY_FLOOR_USDT`)**:
   - If capital ever breaches the critical threshold (e.g., dropping to \$9,000 from \$10,000), the bot **kills its own process immediately (`sys.exit(101)`)**, preventing catastrophic account liquidation.
2. **Circuit Breaker (`MAX_DAILY_DRAWDOWN_PCT`)**:
   - Halts all trading if current day loss hits 3%.
3. **Streak Limiter (`MAX_CONSECUTIVE_LOSSES`)**:
   - Enforces a tactical cooldown after 4 consecutive losses.
4. **Instant Telemetry Broadcast**:
   - Dispatches instant alerts via **Telegram** and **Discord Webhooks** on every trade, liquidation, or defense trigger.

---

## 🚀 How to Run the Bot

### 1. Launch Paper Mode (Zero Risk, Live Simulation)
Run directly from your workspace:
```powershell
cd c:\Users\rehan\Downloads\Programs\Apex-Sovereign-Bot
python -m src.main
```

### 2. Configure Your Parameters & Live Keys
Copy `.env.example` to `.env` and configure credentials:
```env
MODE=PAPER                  # Change to LIVE when ready
EXCHANGE_ID=binance         # Or bybit, kraken, okx
EXCHANGE_API_KEY=your_key
EXCHANGE_API_SECRET=your_secret
SANDBOX=True                # True connects to testnet

INITIAL_CAPITAL_USDT=10000.0
INSOLVENCY_FLOOR_USDT=9000.0

# Optional Webhooks
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=
```

---

## ☁️ Cloud Deployment (Docker)

To deploy to any cloud server (AWS EC2, GCP Compute Engine, DigitalOcean Droplet):

```bash
docker build -t apex-sovereign-bot .
docker run -d --name sovereign-trader --restart unless-stopped --env-file .env apex-sovereign-bot
```
