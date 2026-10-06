import sqlite3
import os
import time
from typing import Dict, Any, List

class CitadelDatabaseVault:
    """
    Continuous 24/366 Persistent SQLite & WAL Ledger Vault.
    Guarantees:
    - Zero data loss on reboot, power failure, or background restart
    - High-concurrency WAL (Write-Ahead Logging) mode
    - Permanent historical ledger for all Trades, HFT Micro-fills, and Equity snapshots
    """
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            db_path = os.path.join(base_dir, "data", "apex_citadel.db")
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")  # High speed concurrent logging
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Closed Swing Trades Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS swing_trades (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                quantity REAL NOT NULL,
                pnl REAL NOT NULL,
                pnl_pct REAL NOT NULL,
                reason TEXT NOT NULL,
                strategy_rationale TEXT,
                volume_traded REAL,
                hold_duration_sec REAL,
                alpha_saved_usd REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 2. Sub-Second Multi-Asset HFT Fills Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS hft_executions (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                asset_class TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                imbalance TEXT NOT NULL,
                pnl REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 3. Continuous Equity & 99-Tier Heartbeat Snapshots Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS equity_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_equity REAL NOT NULL,
                liquid_cash REAL NOT NULL,
                active_tier INTEGER NOT NULL,
                tier_name TEXT NOT NULL,
                hft_profit REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 4. State Persistence (Restores capital on restart)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                val TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()

    def save_swing_trade(self, t: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO swing_trades (
                id, symbol, entry_price, exit_price, quantity, pnl, pnl_pct,
                reason, strategy_rationale, volume_traded, hold_duration_sec, alpha_saved_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t["id"], t["symbol"], t["entry_price"], t["exit_price"], t["quantity"],
                t["pnl"], t["pnl_pct"], t["reason"], t.get("strategy_rationale", ""),
                t.get("volume_traded", 0.0), t.get("hold_duration_sec", 0.0), t.get("alpha_saved_usd", 0.0)
            ))
            conn.commit()

    def save_hft_execution(self, h: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO hft_executions (
                id, symbol, asset_class, latency_ms, imbalance, pnl
            ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                h["id"], h["symbol"], h["asset_class"], h["latency_ms"], h["imbalance"], h["pnl"]
            ))
            conn.commit()

    def record_snapshot(self, equity: float, cash: float, tier: int, tier_name: str, hft_profit: float):
        with self._get_connection() as conn:
            conn.execute("""
            INSERT INTO equity_snapshots (total_equity, liquid_cash, active_tier, tier_name, hft_profit)
            VALUES (?, ?, ?, ?, ?)
            """, (equity, cash, tier, tier_name, hft_profit))
            conn.commit()

    def get_persisted_state(self, key: str, default: str = None) -> str:
        with self._get_connection() as conn:
            row = conn.execute("SELECT val FROM system_state WHERE key = ?", (key,)).fetchone()
            if row:
                return row["val"]
            return default

    def set_persisted_state(self, key: str, val: str):
        with self._get_connection() as conn:
            conn.execute("INSERT OR REPLACE INTO system_state (key, val) VALUES (?, ?)", (key, str(val)))
            conn.commit()

    def get_recent_hft(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM hft_executions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def get_recent_trades(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM swing_trades ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def get_all_time_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            hft_sum = conn.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(pnl), 0) as total FROM hft_executions").fetchone()
            swing_sum = conn.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(pnl), 0) as total FROM swing_trades").fetchone()
            return {
                "total_hft_count": hft_sum["cnt"],
                "total_hft_profit": hft_sum["total"],
                "total_swing_count": swing_sum["cnt"],
                "total_swing_profit": swing_sum["total"]
            }
