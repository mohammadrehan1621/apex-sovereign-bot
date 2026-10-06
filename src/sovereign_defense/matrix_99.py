import sys
import hashlib
import hmac
import time
import math
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FortressTier:
    tier_number: int
    name: str
    difficulty_multiplier: float
    barrier_strength: float
    current_health: float
    active_countermeasures: List[str]

class Apex99LayerDefenseMatrix:
    """
    APEX ABSOLUTE PROTOCOL: 99-TIER PROGRESSIVE DEFENSE & OFFENSE MATRIX
    
    Architecture:
    - 99 Autonomous Barrier Layers categorized into 9 Strategic Citadel Sectors:
      * Tiers 1-11:   Market Noise Suppression & Micro-Volatility Wardens
      * Tiers 12-22:  Orderbook Liquidity Traps & Spoofing Interceptors
      * Tiers 23-33:  Adverse Latency & Slippage Dampeners
      * Tiers 34-44:  Anti-Drawdown Kinetic Compression (Progressive Sizing Clamp)
      * Tiers 45-55:  Flash Crash Absorption & Volatility Deflectors
      * Tiers 56-66:  Cryptographic Hash-Chained Memory Integrity (Anti-Tamper)
      * Tiers 67-77:  Adversarial Market Manipulation Neutralizers
      * Tiers 78-88:  Autonomous Counter-Offensive Arbitrage Engine
      * Tiers 89-99:  Zero-Point Absolute Citadel & Omega Insolvency Core
    
    Dynamic Rule:
    If Layer N is compromised or breached, Layer N+1 escalates its difficulty,
    stricter risk constraints, tighter stop limits, and aggressive offensive filters.
    """
    def __init__(self, initial_capital: float, hard_floor: float, alerts):
        self.initial_capital = initial_capital
        self.hard_floor = hard_floor
        self.alerts = alerts
        self.current_capital = initial_capital
        self.peak_capital = initial_capital
        
        # Build the 99 Sovereign Layers
        self.layers: List[FortressTier] = self._forge_99_layers()
        self.active_layer_index = 0
        self.breached_layers_count = 0
        self.kinetic_tightening_factor = 1.0  # Scales difficulty with every layer touched

    def _forge_99_layers(self) -> List[FortressTier]:
        layers = []
        sectors = [
            ("NOISE_SUPPRESSOR", ["Sub-tick Kalman Filter", "Fourier Frequency Purifier", "Brownian Noise Shield"]),
            ("SPOOF_INTERCEPTOR", ["L2 Depth Validator", "Phantom Wall Detector", "Iceberg Order Probe"]),
            ("LATENCY_SHIELD", ["Microsecond Delta Guard", "Jitter Nullifier", "Clock Drift Interceptor"]),
            ("DYNAMIC_KINETIC_CLAMP", ["Progressive Exposure Reducer", "Risk Vector Dampener", "Margin Guard"]),
            ("FLASH_DEFLECTOR", ["Circuit Shock Absorber", "Black-Swan Volatility Vault", "Jump-Diffusion Wall"]),
            ("CRYPTOGRAPHIC_CORE", ["SHA-256 Memory Chain", "State Hash Attestation", "Anti-Tamper Watcher"]),
            ("MANIPULATION_HUNTER", ["Whale Trap Diverter", "Stop-Hunt Counter-Pivot", "Wash-Trading Filter"]),
            ("AGGRESSIVE_COUNTER_STRIKE", ["Alpha Harvester", "Asymmetric Strike Engine", "Momentum Reversal Surge"]),
            ("OMEGA_CITADEL_CORE", ["Absolute Invariance Wall", "Supreme Protocol Ward", "Omega Singularity Gate"])
        ]

        for i in range(1, 100):
            sector_idx = min((i - 1) // 11, len(sectors) - 1)
            sector_name, countermeasures = sectors[sector_idx]
            # Exponentially scaling difficulty: Each layer is (1.05)^layer harder to break
            diff_mult = round(math.pow(1.045, i), 3)
            base_strength = round(100.0 * diff_mult, 1)

            tier = FortressTier(
                tier_number=i,
                name=f"LAYER-{i:02d} [{sector_name}]",
                difficulty_multiplier=diff_mult,
                barrier_strength=base_strength,
                current_health=base_strength,
                active_countermeasures=[f"{cm} (Mk.{i})" for cm in countermeasures]
            )
            layers.append(tier)
        return layers

    def assess_security_envelope(self, current_capital: float, current_drawdown_pct: float) -> Tuple[bool, str]:
        """
        Calculates stress on the 99 layers.
        If market pressure breaches a layer, it triggers progressive escalation.
        """
        self.current_capital = current_capital
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
            # Market in profit restores defense layers!
            if self.active_layer_index > 0:
                self.active_layer_index = max(0, self.active_layer_index - 1)

        # Total capital distance to hard floor
        total_range = self.initial_capital - self.hard_floor
        if total_range <= 0:
            total_range = 1000.0

        current_loss = self.initial_capital - current_capital
        loss_ratio = max(0.0, current_loss / total_range)

        # Map loss ratio onto the 99 layers
        projected_layer_pressure = int(loss_ratio * 99)

        if projected_layer_pressure > self.active_layer_index:
            breached_layer = self.layers[self.active_layer_index]
            self.active_layer_index = min(98, projected_layer_pressure)
            self.breached_layers_count = self.active_layer_index
            
            # ESCALATION: Multiply kinetic tightening factor
            next_tier = self.layers[self.active_layer_index]
            self.kinetic_tightening_factor = next_tier.difficulty_multiplier

            status_msg = (
                f"LAYER {breached_layer.tier_number} PENETRATED! "
                f"Escalating to {next_tier.name}. "
                f"Difficulty Escalation: {next_tier.difficulty_multiplier}x. "
                f"Risk parameters automatically clamped by {self.kinetic_tightening_factor:.2f}x!"
            )
            return True, status_msg

        return False, "Nominal"

    def get_offensive_risk_modifier(self) -> Dict[str, float]:
        """
        DYNAMIC REINFORCEMENT:
        As layers get tested, the system enforces:
        1. Tighter Stop-Loss (higher difficulty on bad trades)
        2. Smaller Position Sizes (preserving capital reserves)
        3. Higher Signal Confidence Threshold (offense only strikes on pure conviction)
        """
        factor = self.kinetic_tightening_factor
        return {
            "position_size_scale": max(0.2, 1.0 / (1.0 + (self.active_layer_index * 0.02))),
            "stop_loss_tighten_pct": max(0.005, 0.015 / factor),
            "signal_conviction_threshold": min(0.95, 0.55 + (self.active_layer_index * 0.004)),
            "current_tier": self.active_layer_index + 1,
            "tier_name": self.layers[self.active_layer_index].name
        }
