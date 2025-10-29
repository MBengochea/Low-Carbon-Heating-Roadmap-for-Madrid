# src/formatting.py
"""
Formatting helpers for stakeholder tables
"""

from typing import Any

def fmt_money_eur_eu(x: float) -> str:
    """
    Format euro integer or float as €75.000.000 style
    Rounds to nearest euro before formatting.
    """
    try:
        val = int(round(float(x)))
    except Exception:
        return str(x)
    s = f"€{val:,}".replace(",", ".")
    return s

def fmt_co2_tonsyr(x: float) -> str:
    """
    Format CO2 tons per year as 13.068 tons/yr style
    Rounds to nearest ton before formatting.
    """
    try:
        val = int(round(float(x)))
    except Exception:
        return str(x)
    s = f"{val:,}".replace(",", ".") + " tons/yr"
    return s

def build_total_row(df, cost_col="total_cost", co2_col="weighted_saving"):
    """
    Returns a dict with formatted totals for stakeholder table.
    Expect cost_col in euros and co2_col in kg (will convert to tons).
    """
    total_cost = int(round(df[cost_col].sum()))
    total_co2_tons = int(round(df[co2_col].sum() / 1000.0))
    return {
        "district": "TOTAL",
        "tech": "—",
        "adoption_rate": "—",
        "co2_emissions_reduce": fmt_co2_tonsyr(total_co2_tons),
        "cost": fmt_money_eur_eu(total_cost)
    }
