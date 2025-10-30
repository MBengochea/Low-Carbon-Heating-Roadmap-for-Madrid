# src/io.py
"""Minimal IO and audit helpers / IO mínimo y auditoría"""

from pathlib import Path
import json
import pandas as pd
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]  # repo root / raíz repo
PROC = ROOT / "data" / "processed"
AUDIT = ROOT / "data" / "ingest_audit"
PROC.mkdir(parents=True, exist_ok=True)
AUDIT.mkdir(parents=True, exist_ok=True)

def save_df(df: pd.DataFrame, relpath: str):
    # Save df to repo relative path (CSV) / Guarda df en ruta relativa (CSV)
    p = ROOT.joinpath(relpath)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False, encoding="utf-8")
    return p

def load_df(relpath: str):
    # Load CSV relative to repo root / Carga CSV relativo al repo
    p = ROOT.joinpath(relpath)
    return pd.read_csv(p)

def write_audit_log(source: str, rows_in: int, rows_out: int, transforms: dict):
    # Write simple audit JSON to data/ingest_audit / Escribe JSON de auditoría en data/ingest_audit
    audit = {
        "source": source,
        "pull_date": datetime.utcnow().isoformat() + "Z",
        "rows_in": int(rows_in),
        "rows_out": int(rows_out),
        "transforms": transforms
    }
    fname = AUDIT / f"audit_{Path(source).stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)
    return fname