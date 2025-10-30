# streamlit_app.py
# Decision-grade Streamlit app / App de decisión en Streamlit

import streamlit as st, yaml, pandas as pd, numpy as np, pydeck as pdk
from pathlib import Path
from src.formatting import fmt_money_eur_eu, fmt_co2_tonsyr  # formatting / formato
from src.optimization import run_priority_greedy              # optimizer / optimizador
from src.io import load_df                                    # artifact loader / cargador

ROOT = Path(__file__).parent  # repo root relative / relativo a raíz

# ---------- cache loaders / cargadores caché ----------
@st.cache_data
def load_config():
    p = ROOT / "config.yml"
    return yaml.safe_load(p.read_text()) if p.exists() else {}

@st.cache_data
def load_processed(cfg):
    # load minimal artifacts if present / cargar artefactos mínimos si existen
    path_build = ROOT / cfg.get("data", {}).get("processed_dir", "data/processed") / "cleaned_buildings.csv"
    path_spec = ROOT / cfg.get("data", {}).get("processed_dir", "data/processed") / "heating_specs.csv"
    dfb = pd.read_csv(path_build) if path_build.exists() else pd.DataFrame()
    dfs = pd.read_csv(path_spec) if path_spec.exists() else pd.DataFrame()
    return dfb, dfs

@st.cache_data
def load_pareto(cfg):
    path = ROOT / cfg.get("artifacts", {}).get("pareto_frontier", "artifacts/pareto_frontier.csv")
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

# ---------- app ----------
def main():
    st.set_page_config(page_title="Madrid Heating Roadmap", layout="wide")
    cfg = load_config()
    PROC = cfg.get("data", {}).get("processed_dir", "data/processed")

    # Sidebar / Barra lateral
    st.sidebar.header("Scenario inputs / Entradas de escenario")
    budget = st.sidebar.number_input("Budget (EUR) / Presupuesto (EUR)", min_value=0, value=cfg.get("optimization", {}).get("budget_eur_default", 90_000_000), step=1_000_000)
    subsidy = st.sidebar.slider("CAPEX subsidy % / Subsidio CAPEX %", 0, 100, int(cfg.get("optimization", {}).get("capex_subsidy_pct_default", 0)))
    opex = st.sidebar.number_input("OPEX × / OPEX ×", min_value=0.0, value=float(cfg.get("optimization", {}).get("opex_factor_default", 1.0)), step=0.1, format="%.2f")
    co2f = st.sidebar.number_input("CO₂ × / CO₂ ×", min_value=0.0, value=float(cfg.get("optimization", {}).get("co2_factor_default", 1.0)), step=0.05, format="%.2f")
    prio_default = cfg.get("defaults", {}).get("priority_districts", [10, 11, 12, 13, 15])
    prio = st.sidebar.multiselect("Priority districts / Distritos prioritarios", options=list(range(1, 22)), default=prio_default)
    st.sidebar.caption("Format: €xx.xxx.xxx, tons/yr shown in tables / Formato: €xx.xxx.xxx, tons/año en tablas")

    # Tabs / Pestañas
    tab_intro, tab_data, tab_sim, tab_viz, tab_rec = st.tabs([
        "Intro", "Data", "Simulation", "Visualizations", "Recommendations"
    ])

    # Intro / Introducción
    with tab_intro:
        st.title("Low-Carbon Heating Roadmap for Madrid")
        c1, c2, c3 = st.columns(3)
        c1.metric("Budget / Presupuesto", fmt_money_eur_eu(budget))
        c2.metric("CAPEX subsidy / Subsidio CAPEX", f"{subsidy}%")
        c3.metric("OPEX × / OPEX ×", f"{opex:.2f}")
        st.write("Select scenario inputs on the left, then view the Simulation tab for results. Pareto frontier preview and final tables are provided for decision-making. This app consumes notebook artifacts for reproducibility. / Seleccione entradas a la izquierda y consulte la pestaña de Simulación para resultados. La frontera de Pareto y tablas finales están listas para la toma de decisiones.")
        st.info("Artifacts required: data/processed/cleaned_buildings.csv, data/processed/heating_specs.csv, artifacts/pareto_frontier.csv  / Artefactos requeridos: ...")

    # Data / Datos
    with tab_data:
        bld, spec = load_processed(cfg)
        pareto = load_pareto(cfg)
        st.subheader("Processed datasets / Conjuntos procesados")
        st.write(f"{PROC}/cleaned_buildings.csv → {len(bld)} rows") if not bld.empty else st.warning("cleaned_buildings.csv not found")
        st.write(f"{PROC}/heating_specs.csv → {len(spec)} rows") if not spec.empty else st.warning("heating_specs.csv not found")
        st.subheader("Pareto frontier preview / Vista de frontera de Pareto")
        st.dataframe(pareto.head(50)) if not pareto.empty else st.info("Run notebook 01 to generate artifacts/pareto_frontier.csv")

    # Simulation / Simulación
    with tab_sim:
        st.subheader("Portfolio selection / Selección de cartera")
        if bld.empty or spec.empty:
            st.error("Missing processed artifacts. Run 00_data_cleaning first. / Faltan artefactos procesados.")
        else:
            # Minimal join for optimizer / Unión mínima para optimizador
            df = bld.merge(spec, how="left", left_on="heating_type", right_on="tech")
            # Expected columns for optimizer / Columnas esperadas por el optimizador
            for col in ["district_id","expected_capex_eur","OPEX","expected_saving_kg"]:
                if col not in df.columns: df[col] = 0  # fallback / respaldo
            # Run greedy / Ejecutar greedy
            sel = run_priority_greedy(
                df=df,
                budget=float(budget),
                priority_list=prio,
                capex_subsidy_pct=float(subsidy),
                opex_factor=float(opex),
                co2_factor=float(co2f),
                adoption_rate_default=float(cfg.get("defaults", {}).get("adoption_rate_default", 0.30))
            )
            if sel.empty:
                st.warning("No selection within budget / Sin selección dentro del presupuesto")
            else:
                # Derived metrics / Métricas derivadas
                sel["co2_tons"] = (sel["weighted_saving"] / 1000).round(0)
                sel["cost_eur"] = sel["total_cost"].round(0)
                # Display table / Mostrar tabla
                report = sel[["district_id","tech","adoption_rate","co2_tons","cost_eur"]].copy()
                report["co2_tons"] = report["co2_tons"].apply(fmt_co2_tonsyr)
                report["cost_eur"] = report["cost_eur"].apply(fmt_money_eur_eu)
                st.markdown("**Selected portfolio / Cartera seleccionada**")
                st.dataframe(report, use_container_width=True)
                # Totals / Totales
                tot_cost = fmt_money_eur_eu(float(sel["total_cost"].sum()))
                tot_co2 = fmt_co2_tonsyr(float(sel["weighted_saving"].sum()/1000))
                st.metric("Total cost / Coste total", tot_cost)
                st.metric("Annual CO₂ reduced / CO₂ anual reducido", tot_co2)

    # Visualizations / Visualizaciones
    with tab_viz:
        st.subheader("CO₂ by district / CO₂ por distrito")
        if 'sel' in locals() and not sel.empty:
            by_d = sel.groupby("district_id", as_index=False).agg(
                co2_tons=("weighted_saving", lambda s: (s.sum()/1000.0)),
                cost_eur=("total_cost","sum")
            )
            cA, cB = st.columns(2)
            cA.bar_chart(by_d.set_index("district_id")["co2_tons"])
            cB.bar_chart(by_d.set_index("district_id")["cost_eur"])
            st.caption("Units: CO₂ tons/yr, cost EUR / Unidades: CO₂ ton/año, coste EUR")

            # Simple map (center Madrid) / Mapa simple (centro Madrid)
            st.subheader("Map / Mapa")
            # If lat/lon per district available, plot; else center placeholder / si hay lat/lon, graficar
            center = [40.4168, -3.7038]  # Madrid center / centro Madrid
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=by_d.assign(lat=center[0], lon=center[1]),
                get_position='[lon, lat]',
                get_radius=2000,
                get_fill_color='[255, 140, 0, 140]'
            )
            st.pydeck_chart(pdk.Deck(map_style="light", initial_view_state=pdk.ViewState(latitude=center[0], longitude=center[1], zoom=11), layers=[layer]))
        else:
            st.info("Run Simulation to view charts / Ejecute Simulación para ver gráficos")

    # Recommendations / Recomendaciones
    with tab_rec:
        st.subheader("Actionable recommendations / Recomendaciones accionables")
        if 'sel' in locals() and not sel.empty:
            # Highlight first priorities and remaining budget / Prioridades y presupuesto restante
            spent = float(sel["total_cost"].sum()); rem = float(budget) - spent
            st.write(f"- Prioritize districts: {prio} first; remaining budget: {fmt_money_eur_eu(rem)}  / Priorizar distritos: {prio} primero; presupuesto restante: {fmt_money_eur_eu(rem)}")
            # Cost-per-ton leaderboard / Ranking coste/ton
            leaderboard = sel.assign(cpt = sel["total_cost"] / (sel["weighted_saving"]/1000)).sort_values("cpt")
            st.write("- Cost per ton ranking (lower is better) / Ranking de coste por tonelada (menor es mejor)")
            st.dataframe(leaderboard[["district_id","tech","cpt"]].assign(cpt=lambda s: s["cpt"].round(0)), use_container_width=True)
        else:
            st.info("Run Simulation to get recommendations / Ejecute Simulación para ver recomendaciones")

    # Footer / Pie
    st.caption("This app consumes notebook artifacts for reproducibility. / Esta app consume artefactos de notebooks para reproducibilidad.")

if __name__ == "__main__":
    main()