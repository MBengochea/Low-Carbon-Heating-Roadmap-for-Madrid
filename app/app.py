# streamlit_app.py
# Self-contained demo with sample data / Demo autocontenida con datos de ejemplo

# streamlit_app.py
# Minimal, robust Streamlit app that runs without optional heavy deps
# Works with only streamlit, pandas, numpy installed / Funciona con solo streamlit, pandas, numpy

import streamlit as st  # UI / interfaz
import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path(__file__).parent

# ---------- safe optional imports / importaciones opcionales seguras ----------
# Try pydeck for rich maps, otherwise None / intenta pydeck, si no None
try:
    import pydeck as pdk  # optional / opcional
except Exception:
    pdk = None

# ---------- helpers / ayudantes ----------
def fmt_money(x): return "€" + f"{int(round(float(x))):,}".replace(",", ".")  # money format / formato euros
def fmt_co2_tons(x): return f"{int(round(float(x))):,}".replace(",", ".") + " tons/yr"  # CO2 format / formato CO2

# Tiny sample data generator used when no artifacts present / Generador de muestra si faltan artefactos
def make_sample():
    districts = [10,11,12,13,15,1,2,3]
    techs = ["Air Source Heat Pump","Ground Source Heat Pump","District Heating","Efficient Boiler"]
    rng = np.random.default_rng(42)
    rows = []
    for d in districts:
        for t in techs:
            area = int(rng.integers(50_000, 250_000))
            saving = int(rng.integers(1_000_000, 7_000_000))
            adopt = float(rng.uniform(0.25,0.50) if d in [10,11,12,13,15] else rng.uniform(0.20,0.35))
            capex = int(rng.integers(800_000, 2_500_000))
            opex = int(capex * 0.08)
            rows.append({
                "district_id": d, "tech": t, "area_m2": area,
                "expected_saving_kg": saving, "adoption_rate": adopt,
                "capex_eur_kw": capex, "OPEX": opex
            })
    bld = pd.DataFrame(rows)
    centroids = pd.DataFrame({
        "district_id": districts,
        "lat": [40.39,40.37,40.36,40.38,40.45,40.42,40.41,40.43],
        "lon": [-3.75,-3.72,-3.70,-3.67,-3.63,-3.69,-3.71,-3.66]
    })
    return bld, centroids

# Minimal, deterministic greedy selector / Selector greedy mínimo y determinista
def run_priority_greedy(df, budget, priority, capex_subsidy_pct=0.0, opex_factor=1.0, co2_factor=1.0, adoption_default=0.30):
    d = df.copy()
    d["adoption_rate"] = d.get("adoption_rate", adoption_default).fillna(adoption_default)
    d["expected_capex_eur"] = d.get("capex_eur_kw", 0)
    d["OPEX"] = d.get("OPEX", 0) * opex_factor
    d["expected_capex_eur_subsidized"] = d["expected_capex_eur"] * (1 - capex_subsidy_pct/100.0)
    d["total_cost"] = d["expected_capex_eur_subsidized"] + d["OPEX"]
    d["weighted_saving"] = d["expected_saving_kg"] * d["adoption_rate"] * co2_factor

    selected = []
    budget_left = float(budget)
    # priority first (one cheapest entry per district) / prioridad primero (una entrada más barata por distrito)
    for did in priority:
        cand = d[d["district_id"]==did].sort_values("total_cost")
        if not cand.empty:
            row = cand.iloc[0]
            if row["total_cost"] <= budget_left:
                selected.append(row); budget_left -= row["total_cost"]
    # then others ascending district id / luego otros por id ascendente
    for did in sorted(set(d["district_id"].unique()) - set(priority)):
        cand = d[d["district_id"]==did].sort_values("total_cost")
        if not cand.empty:
            row = cand.iloc[0]
            if row["total_cost"] <= budget_left:
                selected.append(row); budget_left -= row["total_cost"]
    return pd.DataFrame(selected)

# ---------- Streamlit app layout / Diseño de la app ----------
def main():
    st.set_page_config(page_title="Madrid Heating Roadmap (Light)", layout="wide")
    st.title("Low-Carbon Heating Roadmap — Lightweight Demo")

    # sidebar inputs / entradas barra lateral
    st.sidebar.header("Scenario / Escenario")
    budget = st.sidebar.number_input("Budget (EUR) / Presupuesto", min_value=0, value=60_000_000, step=1_000_000)
    subsidy = st.sidebar.slider("CAPEX subsidy % / Subsidio CAPEX %", 0, 100, 20)
    opex = st.sidebar.number_input("OPEX ×", min_value=0.0, value=1.10, step=0.1, format="%.2f")
    co2f = st.sidebar.number_input("CO₂ ×", min_value=0.0, value=1.0, step=0.05, format="%.2f")
    prio_default = [10,11,12,13,15]
    prio = st.sidebar.multiselect("Priority districts / Distritos prioritarios", options=[10,11,12,13,15,1,2,3], default=prio_default)

    # load artifacts if present else sample / cargar artefactos si existen, si no usar muestra
    proc_dir = ROOT / "data" / "processed"
    bld_path = proc_dir / "cleaned_buildings.csv"
    try:
        if bld_path.exists():
            df = pd.read_csv(bld_path)
            # ensure minimal expected cols exist / asegurar columnas mínimas
            for c in ["expected_saving_kg","capex_eur_kw","OPEX","adoption_rate","district_id","tech"]:
                if c not in df.columns: df[c] = 0
            centroids = pd.DataFrame({"district_id": df["district_id"].unique()})
            centroids["lat"] = 40.4168; centroids["lon"] = -3.7038
            data_source = f"Loaded {bld_path.name}"
        else:
            df, centroids = make_sample()
            data_source = "Using synthetic sample data"
    except Exception:
        df, centroids = make_sample()
        data_source = "Using synthetic sample data (load error)"

    # tabs / pestañas
    tab1, tab2, tab3 = st.tabs(["Overview","Simulation","Map & Charts"])

    with tab1:
        st.subheader("Data source / Fuente de datos")
        st.write(data_source)
        st.write("Rows (aggregated district-tech):", len(df))
        st.dataframe(df.head(10))

    with tab2:
        st.subheader("Run simulation / Ejecutar simulación")
        sel = run_priority_greedy(df, budget, prio, capex_subsidy_pct=subsidy, opex_factor=opex, co2_factor=co2f, adoption_default=0.30)
        if sel.empty:
            st.warning("No selection fits the budget / Ninguna selección cabe en el presupuesto")
        else:
            sel = sel.reset_index(drop=True)
            sel["co2_tons"] = (sel["weighted_saving"]/1000).round(0)
            sel["cost_eur"] = sel["total_cost"].round(0)
            out = sel[["district_id","tech","adoption_rate","co2_tons","cost_eur"]].copy()
            out["co2_tons"] = out["co2_tons"].apply(fmt_co2_tons)
            out["cost_eur"] = out["cost_eur"].apply(fmt_money)
            st.dataframe(out, use_container_width=True)
            st.metric("Total cost / Coste total", fmt_money(sel["total_cost"].sum()))
            st.metric("Annual CO₂ reduced / CO₂ anual reducido", fmt_co2_tons(sel["weighted_saving"].sum()/1000.0))

    with tab3:
        st.subheader("Map & Charts / Mapa y gráficos")
        if sel is None or sel.empty:
            st.info("Run simulation first / Ejecute la simulación primero")
        else:
            # prepare aggregated by district / agregado por distrito
            agg = sel.groupby("district_id", as_index=False).agg(
                co2_tons=("weighted_saving", lambda s: s.sum()/1000.0),
                cost_eur=("total_cost","sum")
            ).reset_index(drop=True)
            agg = agg.merge(centroids, on="district_id", how="left")
            # Map: pydeck if available, else st.map / pydeck si disponible, si no st.map
            if pdk is not None and not agg[["lat","lon"]].isnull().any().any():
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=agg,
                    get_position='[lon, lat]',
                    get_radius=2000,
                    get_fill_color='[255, 140, 0, 180]'
                )
                view = pdk.ViewState(latitude=agg["lat"].mean(), longitude=agg["lon"].mean(), zoom=11)
                st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=view, layers=[layer]))
            else:
                # st.map needs columns latitude and longitude / st.map requiere latitude/longitude
                map_df = agg.rename(columns={"lat":"latitude","lon":"longitude"})[["latitude","longitude"]].dropna()
                if not map_df.empty:
                    st.map(map_df)
                else:
                    st.info("No coordinates available to plot map / No hay coordenadas para graficar mapa")
            # simple charts / gráficos simples
            c1, c2 = st.columns(2)
            c1.bar_chart(agg.set_index("district_id")["co2_tons"])
            c2.bar_chart(agg.set_index("district_id")["cost_eur"])

    st.caption("Lightweight demo — no optional heavy libs required. / Demo liviano — no necesita librerías pesadas opcionales.")

if __name__ == "__main__":
    main()
