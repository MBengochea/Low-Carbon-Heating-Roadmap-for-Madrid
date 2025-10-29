# src/formatting.py
"""Formatting helpers / Ayudantes de formato"""

def fmt_money_eur_eu(x):
    # Format euro as €75.000.000 / Formatea euros como €75.000.000
    try:
        v = int(round(float(x)))
    except Exception:
        return str(x)
    return "€" + f"{v:,}".replace(",", ".")

def fmt_co2_tonsyr(x):
    # Format CO2 as 13.068 tons/yr / Formatea CO2 como 13.068 tons/yr
    try:
        v = int(round(float(x)))
    except Exception:
        return str(x)
    return f"{v:,}".replace(",", ".") + " tons/yr"
