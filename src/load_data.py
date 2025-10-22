# src/load_data.py
from pathlib import Path
import requests, pandas as pd

# rutas base / base paths
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"; CLEAN.mkdir(parents=True, exist_ok=True)
CKAN = "https://datos.comunidad.madrid/api/3/action/package_show"

# estandariza columnas / standardize column names
def _std(df): df = df.copy(); df.columns = [str(c).lower().strip().replace(" ", "_") for c in df.columns]; return df

# sin coerción / no coercion
def _light(df): return df.copy()

# guarda CSV limpio / save cleaned CSV
def save_clean(df, name): out = CLEAN / name; df.to_csv(out, index=False); return out

# carga desde CKAN / load from CKAN
def fetch_ckan_csv(id, sep=";", enc="latin1", low_memory=True):
    try: r = requests.get(CKAN, params={"id": id}, timeout=20); r.raise_for_status()
    except: return pd.DataFrame()
    res = r.json().get("result", {}).get("resources", [])
    url = next((x.get("url") for x in res if x.get("format", "").lower() == "csv"), None)
    return _light(_std(pd.read_csv(url, sep=sep, encoding=enc, low_memory=low_memory))) if url else pd.DataFrame()

# carga local / load local CSV
def read_local(name, low_memory=False):
    p = RAW / name
    if not p.exists(): raise FileNotFoundError(p)
    return _light(_std(pd.read_csv(p, low_memory=low_memory)))

# -----------------------
# cargadores / dataset loaders
# -----------------------

def load_gei(save=False): return save_clean(fetch_ckan_csv("atm_inventario_gei"), "gei.csv") if save else fetch_ckan_csv("atm_inventario_gei")
def load_ceee(save=False): return save_clean(fetch_ckan_csv("registro_certificados_eficiencia_energetica"), "ceee.csv") if save else fetch_ckan_csv("registro_certificados_eficiencia_energetica")
def load_pst(save=False): return save_clean(fetch_ckan_csv("1911600"), "pst.csv") if save else fetch_ckan_csv("1911600")
def load_gas(save=False): return save_clean(fetch_ckan_csv("950a60f0-498c-48db-84f4-734990d3e253"), "gas.csv") if save else fetch_ckan_csv("950a60f0-498c-48db-84f4-734990d3e253")

def load_air_realtime(page_size=5000, save=False):  # JSON aire tiempo real / realtime air quality JSON
    url = f"https://ciudadesabiertas.madrid.es/dynamicAPI/API/query/calair_tiemporeal.json?pageSize={page_size}"
    try: r = requests.get(url, timeout=20); r.raise_for_status(); data = r.json()
    except: return pd.DataFrame()
    df = pd.json_normalize(data.get("records", [])); df = _light(_std(df))
    return save_clean(df, "air_realtime.csv") if save else df

def load_zbe_cameras(save=False):  # cámaras ZBE / ZBE cameras
    url = "https://datos.madrid.es/egob/catalogo/300342-0-camaras-zona-bajas-emisiones.csv"
    df = pd.read_csv(url, encoding="latin1", sep=";"); df = _light(_std(df))
    return save_clean(df, "zbe_cameras.csv") if save else df

def load_zbe_zones(save=False):  # zonas especiales ZBE / special ZBE zones
    url = "https://datos.madrid.es/egob/catalogo/300343-0-zonas-especiales-zbe.csv"
    df = pd.read_csv(url, encoding="latin1", sep=";"); df = _light(_std(df))
    return save_clean(df, "zbe_zones.csv") if save else df

def load_districts_geoportal(save=False):  # distritos Madrid / Madrid districts
    url = "https://geoportal.madrid.es/IDEAM_WBGEOPORTAL/descargasDisponibles.iam?fileIdent=aebec21d-5cad-11f0-9f8c-9009dfd270e9"
    df = pd.read_csv(url); df = _light(_std(df))
    return save_clean(df, "districts.csv") if save else df

def load_buildings_3d(save=False):  # edificios 3D / 3D buildings
    url = "https://geoportal.madrid.es/IDEAM_WBGEOPORTAL/dataset.iam?id=ece2d15a-d16f-46e8-aaec-9576771b9997"
    df = pd.read_csv(url); df = _light(_std(df))
    return save_clean(df, "buildings_3d.csv") if save else df

def load_heating_specs(save=False):  # tecnologías calefacción / heating tech specs
    path = ROOT / "data" / "tech_specs" / "heating_technologies.csv"
    df = pd.read_csv(path); df = _light(_std(df))
    return save_clean(df, "heating_specs.csv") if save else df

# -----------------------
# CLI test / prueba CLI
# -----------------------

if __name__ == "__main__":
    print("Local raw CSVs:", [p.name for p in RAW.glob("*.csv")])
    for f in RAW.glob("*.csv"):
        try: df = read_local(f.name); out = save_clean(df, f.name.replace(".csv", "_clean.csv")); print(f"Saved {out} rows={len(df)}")
        except Exception as e: print(f"Fail {f.name}: {e}")

    for loader in [load_gei, load_ceee, load_pst, load_gas, load_air_realtime, load_zbe_cameras, load_zbe_zones, load_districts_geoportal, load_buildings_3d, load_heating_specs]:
        try: df = loader(); print(f"{loader.__name__} rows: {len(df)}")
        except Exception as e: print(f"{loader.__name__} failed: {e}")