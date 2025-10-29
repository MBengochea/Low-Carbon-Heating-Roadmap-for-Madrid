# src/io.py
"""
Minimal IO helpers for the Low-Carbon-Heating project.
Stubs for reading/writing datasets and writing audit logs.
Extend with project-specific paths and validation as needed.
"""

import json
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[1]

def ensure_dirs():
    for d in ["data/processed", "data/ingest_audit", "artifacts", "models"]:
        Path(ROOT.joinpath(d)).mkdir(parents=True, exist_ok=True)

def save_df(df: pd.DataFrame, relpath: str):
    """
    Save dataframe to repo-root relative path (CSV) and return absolute path.
    """
    ensure_dirs()
    p = ROOT.joinpath(relpath)
    df.to_csv(p, index=False)
    return p

def load_df(relpath: str) -> pd.DataFrame:
    """
    Load a CSV from repo-root relative path.
    """
    p = ROOT.joinpath(relpath)
    return pd.read_csv(p)

def write_audit_log(source: str, rows_in: int, rows_out: int, transforms: Dict[str, Any], relpath: str = None):
    """
    Write a simple audit JSON documenting an ingestion / cleaning step.
    """
    ensure_dirs()
    audit = {
        "source": source,
        "pull_date": datetime.utcnow().isoformat() + "Z",
        "rows_in": int(rows_in),
        "rows_out": int(rows_out),
        "transforms": transforms
    }
    filename = f"data/ingest_audit/audit_{Path(source).stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    if relpath:
        filename = relpath
    path = ROOT.joinpath(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)
    return path
