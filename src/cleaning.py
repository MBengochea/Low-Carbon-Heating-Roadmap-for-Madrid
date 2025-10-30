# src/cleaning.py
# Reusable cleaning helpers / Funciones reutilizables de limpieza

import pandas as pd, numpy as np, geopandas as gpd

# --- schema validation / validación de esquema ---
def validate_schema(df, required_cols):
    # assert required columns exist / asegurar columnas requeridas
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise AssertionError(f"Missing columns / Faltan columnas: {missing}")
    return True

# --- data quality report / informe de calidad de datos ---
def dq_report(df):
    n = len(df)
    dup = n - df.drop_duplicates().shape[0]
    cols = {}
    for c in df.columns:
        nulls = int(df[c].isna().sum())
        null_pct = round(nulls/n*100, 2) if n else 0
        uniq = int(df[c].nunique(dropna=True))
        cols[c] = {"null_count": nulls, "null_pct": null_pct, "unique_nonnull": uniq}
    return {"rows_in": n, "duplicate_rows": dup, "columns": cols}

# --- cleaning helpers / ayudantes de limpieza ---
def clip_negatives(df, cols, min_value=0):
    # clip negatives to min_value / recortar negativos a min_value
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = out[c].clip(lower=min_value)
    return out

def convert_units(df, col, unit_col, target_unit="kwh"):
    # normalize units if unit_col exists / normalizar unidades si existe unit_col
    out = df.copy()
    if col in out.columns and unit_col in out.columns:
        mask = out[unit_col].str.lower().eq("mwh")
        out.loc[mask, col] = out.loc[mask, col] * 1000
        out[unit_col] = target_unit
    return out

def assign_district_from_postal(df, postal_col="postal_code", district_map=None):
    # map postal codes to districts / mapear códigos postales a distritos
    out = df.copy()
    if postal_col in out.columns and district_map is not None:
        mapping = dict(zip(district_map["postal_code"], district_map["district_id"]))
        out["district_id"] = out.get("district_id", pd.Series([np.nan]*len(out)))
        out["district_id"] = out["district_id"].fillna(out[postal_col].map(mapping))
    return out

def ensure_crs(gdf, crs="EPSG:4326"):
    # enforce CRS / forzar CRS
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError("Input must be GeoDataFrame")
    if gdf.crs is None:
        gdf = gdf.set_crs(crs)
    else:
        gdf = gdf.to_crs(crs)
    return gdf

def impute_adoption_rate(df, default=0.30):
    # fill missing adoption_rate / rellenar adoption_rate faltante
    out = df.copy()
    if "adoption_rate" not in out.columns:
        out["adoption_rate"] = default
    else:
        out["adoption_rate"] = out["adoption_rate"].fillna(default)
    return out

def flag_imputed(df, cols):
    # add boolean flags for imputed cols / añadir banderas booleanas
    out = df.copy()
    for c in cols:
        flag = f"{c}_imputed"
        out[flag] = out[c].isna()
    return out

def drop_exact_duplicates(df):
    # drop exact duplicate rows / eliminar filas duplicadas exactas
    return df.drop_duplicates()

def inspect_dataframe(df, name="df"):
    """
    Print bilingual summary of a DataFrame: shape, head, tail, info, describe(include='all')
    """
    print(f"\n {name}.shape → {df.shape[0]} rows × {df.shape[1]} columns")
    print("\n head ()")
    display(df.head())

    print("\n tail ()")
    display(df.tail())

    print("\n info ():")
    df.info()

    print("\n describe all")
    display(df.describe(include="all"))