# streamlit_app.py
"""
Streamlit scaffold for Low Carbon Heating Roadmap for Madrid.
Requires: config.yml, artifacts/pareto_frontier.csv, data/processed/ cleaned datasets.
This scaffold focuses on inputs and placeholders for charts and map.
"""

import streamlit as st
import yaml
import pandas as pd
from pathlib import Path
from src.formatting import fmt_money_eur_eu, fmt_co2_tonsyr

ROOT = Path(__file__).parent

@st.cache_data
def load_config(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@st.cache_data
def load_artifacts(cfg):
    artifacts = {}
    pareto_path = ROOT.joinpath(cfg["artifacts"]["pareto_frontier"])
    if pareto_path.exists():
        artifacts["pareto"] = pd.read_csv(pareto_path)
    else:
        artifacts["pareto"] = pd.DataFrame()
    return artifacts

def main():
    st.set_page_config(page_title="Low Carbon Heating Roadmap", layout="wide")
    st.title("Low Carbon Heating Roadmap for Madrid")

    # Load config
    cfg_path = ROOT.joinpath("config.yml")
    if not cfg_path.exists():
        st.error("config.yml not found at repo root. Add config.yml and restart.")
        return
    cfg = load_config(cfg_path)

    # Sidebar controls
    st.sidebar.header("Scenario inputs")
    budget = st.sidebar.number_input(
        "Budget in euros", min_value=0, value=cfg["optimization"]["budget_eur_default"], step=1_000_000
    )
    capex_subsidy = st.sidebar.slider(
        "CAPEX subsidy percent", min_value=0, max_value=100, value=int(cfg["optimization"]["capex_subsidy_pct_default"])
    )
    opex_factor = st.sidebar.number_input(
        "OPEX multiplier", min_value=0.0, value=cfg["optimization"]["opex_factor_default"], step=0.1, format="%.2f"
    )
    co2_factor = st.sidebar.number_input(
        "CO2 multiplier", min_value=0.0, value=cfg["optimization"]["co2_factor_default"], step=0.05, format="%.2f"
    )
    st.sidebar.markdown("Priority districts (top-first)")
    prio_defaults = cfg["defaults"]["priority_districts"]
    prio_input = st.sidebar.multiselect(
        "Priority district IDs", options=list(range(1, 22)), default=prio_defaults
    )

    # Load artifacts
    artifacts = load_artifacts(cfg)

    st.header("Inputs summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Budget", fmt_money_eur_eu(budget))
    col2.metric("CAPEX subsidy", f"{capex_subsidy}%")
    col3.metric("OPEX ×", f"{opex_factor:.2f}")

    st.header("Pareto frontier preview")
    if artifacts["pareto"].empty:
        st.info("Pareto frontier artifact not found. Run 01_emissions_pareto to produce artifacts/pareto_frontier.csv")
    else:
        st.dataframe(artifacts["pareto"].head(50))

    st.header("Simulation result")
    st.write("Placeholder: run optimization backend and display selected districts, costs and CO2 savings.")
    st.write("Use src/optimization.run_priority_greedy to compute selection given sidebar inputs.")
    st.info("This scaffold expects processed data in data/processed and artifacts/pareto_frontier.csv")

    st.header("Visualizations")
    st.write("Placeholder map and charts will appear here. Use pydeck and plotly for maps and interactive charts.")

if __name__ == "__main__":
    main()
