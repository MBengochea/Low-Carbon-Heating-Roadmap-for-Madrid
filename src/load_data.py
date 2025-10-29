# src/load_data.py
# Minimal dataset loader and inspectors / Cargador mínimo y herramientas de inspección

from pathlib import Path
import json, requests, pandas as pd, yaml  # compact imports / importaciones compactas

# config / carga config.yml si existe / load config.yml if present
ROOT = Path(__file__).resolve().parents[1]  # repo root / raíz repo
CFG_PATH = ROOT / "config.yml"
if CFG_PATH.exists(): 
    cfg = yaml.safe_load(CFG_PATH.read_text())  # load config / cargar configuración
else:
    cfg = {
        "data": {"raw_dir": "data/raw", "processed_dir": "data/processed", "audit_dir": "data/ingest_audit"},
        "defaults": {"adoption_rate_default": 0.30, "priority_districts": [10,11,12,13,15]},
        "optimization": {"budget_eur_default": 90000000}
    }  # fallback config / configuración por defecto

RAW = ROOT / cfg["data"]["raw_dir"]  # raw data dir / dir datos crudos
PROC = ROOT / cfg["data"]["processed_dir"]  # processed dir / dir procesados
AUDIT = ROOT / cfg["data"]["audit_dir"]  # audit dir / dir auditoría
PROC.mkdir(parents=True, exist_ok=True); AUDIT.mkdir(parents=True, exist_ok=True)  # ensure dirs / asegurar dirs

CKAN = "https://datos.comunidad.madrid/api/3/action/package_show"  # CKAN base / CKAN base

# --- simple pure helpers / ayudantes puros ---
def _std(df):
    # standardize column names / estandariza nombres columnas
    df = df.copy()
    df.columns = [str(c).lower().strip().replace(" ", "_") for c in df.columns]
    return df

def _light(df): 
    # no coercion, shallow copy / copia superficial sin coerción
    return df.copy()

# --- IO small wrappers using src.io if available / wrappers que usan src.io si está disponible
try:
    from src.io import save_df as _save_df  # prefer canonical IO / preferir IO canónico
    from src.io import load_df as _load_df
    from src.io import write_audit_log as _write_audit
except Exception:
    _save_df = lambda df, p: (PROC.joinpath(Path(p).name) if PROC else Path(p)) and df.to_csv(PROC.joinpath(Path(p).name), index=False)  # fallback save
    _load_df = lambda p: pd.read_csv(ROOT.joinpath(p))
    _write_audit = lambda source, rows_in, rows_out, transforms: (AUDIT.joinpath(f"audit_{Path(source).stem}.json").write_text(json.dumps({
        "source": source, "pull_date": pd.Timestamp.utcnow().isoformat(), "rows_in": int(rows_in), "rows_out": int(rows_out), "transforms": transforms
    }, indent=2)), AUDIT.joinpath(f"audit_{Path(source).stem}.json"))  # fallback audit

# --- CKAN csv fetcher / obtén CSV desde CKAN (returns empty DF on error)
def fetch_ckan_csv(package_id, sep=";", enc="latin1", low_memory=True):
    try:
        r = requests.get(CKAN, params={"id": package_id}, timeout=20); r.raise_for_status()
        res = r.json().get("result", {}).get("resources", [])
        url = next((x.get("url") for x in res if x.get("format","").lower()=="csv"), None)
        if not url: return pd.DataFrame()
        return _light(_std(pd.read_csv(url, sep=sep, encoding=enc, low_memory=low_memory)))
    except Exception:
        return pd.DataFrame()

# --- local loader / carga local con estandarización
def read_local(relpath, low_memory=False):
    p = RAW.joinpath(relpath)
    if not p.exists(): raise FileNotFoundError(p)  # explicit error / error explícito
    return _light(_std(pd.read_csv(p, low_memory=low_memory)))

# --- consistent loader signature examples / ejemplos de loaders con firma consistente ---
def load_heating_specs(save=False):
    # heating tech specs (local) / especificaciones tecnológicas (local)
    path = ROOT / "data" / "tech_specs" / "heating_technologies.csv"
    df = _light(_std(pd.read_csv(path)))
    if save:
        _save_df(df, str(PROC.joinpath("heating_specs.csv")))
    return df

def load_districts_geoportal(save=False):
    # districts (remote) / distritos (remoto)
    url = "https://geoportal.madrid.es/IDEAM_WBGEOPORTAL/descargasDisponibles.iam?fileIdent=aebec21d-5cad-11f0-9f8c-9009dfd270e9"
    try: df = _light(_std(pd.read_csv(url)))
    except Exception: df = pd.DataFrame()
    if save and not df.empty: _save_df(df, str(PROC.joinpath("districts.csv")))
    return df

def load_air_realtime(page_size=5000, save=False):
    # realtime air quality JSON / JSON calidad aire tiempo real
    url = f"https://ciudadesabiertas.madrid.es/dynamicAPI/API/query/calair_tiemporeal.json?pageSize={page_size}"
    try:
        r = requests.get(url, timeout=20); r.raise_for_status(); data = r.json()
        df = pd.json_normalize(data.get("records", [])); df = _light(_std(df))
    except Exception:
        df = pd.DataFrame()
    if save and not df.empty: _save_df(df, str(PROC.joinpath("air_realtime.csv")))
    return df

# --- inspector utility / utilidad de inspección compacta ---
def inspect_columns(df, name="df"):
    # print compact stats / imprime estadísticas compactas
    n = len(df); identical = n - df.drop_duplicates().shape[0]
    print(f"Inspect {name} shape={df.shape} identical_rows={identical}")  # concise output / salida concisa
    for c in df.columns:
        nulls = int(df[c].isna().sum()); uniques = int(df[c].nunique(dropna=True))
        print(f"  {c}: nulls={nulls} uniques={uniques}")

# --- CLI smoke test (safe) / prueba CLI (segura)
if __name__ == "__main__":
    print("Raw CSVs:", [p.name for p in RAW.glob("*.csv")])  # list raw files / lista archivos crudos
    # do not auto-download large remote files / no descargar archivos remotos automáticamente
