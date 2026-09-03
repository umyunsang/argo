#!/usr/bin/env python3
"""Power / MDE calculator for the paired McNemar endpoint of Study B.

LABELLED POWER CALCULATION (instruction-0013 §2 permits simulation only for
instrument fixtures and labelled power/sample-size work). Nothing here is a result.
"""
from __future__ import annotations
import math

def mcnemar_mde(n_pairs: int, p_discordant: float, alpha: float = 0.05, power: float = 0.80) -> float:
    """Smallest detectable |p01 - p10| given n paired episodes and a discordance rate."""
    za = 1.959963984540054 if abs(alpha - 0.05) < 1e-12 else _z(1 - alpha / 2)
    zb = 0.8416212335729143 if abs(power - 0.80) < 1e-12 else _z(power)
    n_d = n_pairs * p_discordant
    if n_d <= 0:
        return float("nan")
    return (za + zb) / math.sqrt(n_d)  # in units of the discordance-normalised effect

def mcnemar_mde_absolute(n_pairs: int, p_discordant: float, alpha=0.05, power=0.80) -> float:
    """MDE expressed as an absolute pass-rate difference between two arms."""
    return mcnemar_mde(n_pairs, p_discordant, alpha, power) * p_discordant

def _z(p: float) -> float:
    lo, hi = -8.0, 8.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < p: lo = mid
        else: hi = mid
    return (lo + hi) / 2

if __name__ == "__main__":
    print(f"{'n_pairs':>8} {'p_disc':>7} {'MDE_abs':>9}")
    for n in (40, 60, 120):
        for pd in (0.20, 0.30, 0.40):
            print(f"{n:8d} {pd:7.2f} {mcnemar_mde_absolute(n, pd):9.3f}")
