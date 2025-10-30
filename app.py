# streamlit_app.py
# Decision-grade Streamlit app / App de decisión en Streamlit

import streamlit as st, yaml, pickle, inspect
from pathlib import Path
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import cvxpy as cp

ROOT = Path(__file__).parent

@st.cache_data
def load_config():
    p = ROOT / "config.yml"
    return yaml.safe_load(p.read_text()) if p.exists() else {}

# --- Helper: generic choropleth with labels ---
def plot_map(gdf, column, title, cmap="OrRd"):
    fig, ax = plt.subplots(figsize=(6,8), dpi=100)
    gdf.plot(
        column=column, cmap=cmap, legend=True, ax=ax,
        edgecolor="0.8", linewidth=0.5
    )
    reps = gdf.geometry.representative_point()
    for (x, y), name in zip(reps.apply(lambda p: (p.x, p.y)), gdf["NOMBRE"]):
        ax.text(x, y, name, ha="center", va="center", fontsize=5, color="black")
    ax.set_title(title, fontsize=10)
    ax.axis("off")
    st.pyplot(fig, clear_figure=True, use_container_width=False)

# --- Helper: priority districts map ---
def plot_priority_map(gdf):
    df = gdf.copy()
    median_income = df['avg_income'].median()
    priority = df[(df['pareto_flag']==1) & (df['avg_income'] < median_income)].copy()
    priority = priority.sort_values('intensity_kg_m2', ascending=False)

    df['centroid'] = df.geometry.representative_point()
    priority['centroid'] = priority.geometry.representative_point()

    fig, ax = plt.subplots(figsize=(4,4), dpi=100)
    df.plot(ax=ax, color="#f0f0f0", edgecolor="0.8")

    cmap = mpl.cm.get_cmap("coolwarm")
    norm = mpl.colors.Normalize(vmin=priority['intensity_kg_m2'].min(),
                                vmax=priority['intensity_kg_m2'].max())
    priority.plot(ax=ax, column='intensity_kg_m2', cmap=cmap, norm=norm,
                  edgecolor="black", linewidth=1.0, legend=True)

    for _, row in priority.iterrows():
        ax.text(row['centroid'].x, row['centroid'].y, row['NOMBRE'],
                ha='center', va='center', fontsize=6, color='black', fontweight='bold')

    ax.set_title("Priority Districts", fontsize=10)
    ax.axis("off")

    comment = ("Priority districts:\n"
               "- Top ≈80% cumulative CO₂,\n"
               "- Below median income,\n"
               "- Highest emission intensity.")
    plt.gcf().text(0.5, -0.05, comment, ha='center', va='top', fontsize=7)

    st.pyplot(fig, clear_figure=True, use_container_width=False)

def main():
    st.set_page_config(page_title="Low-Carbon Heating Roadmap", layout="wide")

    # --- Custom CSS for colors ---
    st.markdown(
        """
        <style>
        .stTabs [role="tablist"] {
            background-color: rgb(8,128,204);
            padding: 0.5rem;
            border-radius: 5px;
        }
        .stTabs [role="tab"] {
            color: white;
            font-weight: bold;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgb(249,235,200);
            color: black !important;
            border-radius: 5px;
        }
        .stTabs [role="tabpanel"] {
            background-color: rgb(249,235,200);
            padding: 0.5rem;
            border-radius: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Header with logo + title ---
    logo_path = ROOT / "assets" / "ayunta.madrid.png"
    col1, col2 = st.columns([1, 8])
    with col1:
        if logo_path.exists():
            st.image(str(logo_path), width=60)
    with col2:
        st.markdown("## Low-Carbon Heating Roadmap for Madrid")

    # --- Tabs ---
    tabs = st.tabs(["Present", "EDA", "D", "M", "A", "I", "C"])

    # Present
    with tabs[0]:
        st.header("Presentation")
        st.subheader("Problem")
        st.markdown("- For buildings registered in the certificated efficiency data.")
        st.subheader("Which set of district → technology rollouts maximizes annual CO₂ reduction subject to a municipal budget X and stakeholder levers?")
        st.markdown("- **Hypothesis:** A 20% CAPEX subsidy increases CO₂ reduction by ≥10% for top Madrid priority districts.")

    # EDA
    with tabs[1]:
        st.header("Exploratory Data Analysis (EDA) & Justification")
        st.subheader("Independent Datasets")
        st.markdown(
            """
            - Green House Gas Emissions in Madrid 1990-2023  
            - Particulate Matter PST Emissions in Madrid 2000-2021  
            - CEEE, Buildings Energy Efficiency Certificates in Madrid 2025  
            """
        )
        st.subheader("Heating is the common denominator for climate and health impacts.")

    # Define
    with tabs[2]:
        st.header("(D) Define")
        sub_tabs = st.tabs(["Pareto (Interactive)", "Pareto (Choropleths)", "Techs", "Stakeholders"])
        with sub_tabs[0]:
            st.subheader("Interactive Folium Map")
            gdf = gpd.read_file(ROOT / "assets" / "madrid_districts.geojson")
            m = folium.Map(location=[40.4168, -3.7038], zoom_start=11)
            folium.GeoJson(
                gdf,
                name="districts",
                tooltip=folium.GeoJsonTooltip(
                    fields=["NOMBRE", "total_co2_kg", "avg_income", "intensity_kg_m2"],
                    aliases=["District", "Total CO₂ (kg)", "Avg Income", "Intensity (kg/m²)"],
                    localize=True
                )
            ).add_to(m)
            st_map = st_folium(m, width=500, height=350)
            if st_map and st_map.get("last_active_drawing"):
                props = st_map["last_active_drawing"]["properties"]
                st.write("### Selected district")
                st.json(props)
        with sub_tabs[1]:
            st.subheader("Static Choropleth Maps with Selector")
            gdf = gpd.read_file(ROOT / "assets" / "madrid_districts.geojson")
            choice = st.radio(
                "Select a map to display:",
                ["Total CO₂", "Emissions Intensity", "Average Income", "Priority Districts"],
                horizontal=True
            )
            if choice == "Total CO₂":
                plot_map(gdf, "total_co2_kg", "Total CO₂ (kg)", cmap="OrRd")
            elif choice == "Emissions Intensity":
                plot_map(gdf, "intensity_kg_m2", "Emissions Intensity (kg/m²)", cmap="OrRd")
            elif choice == "Average Income":
                plot_map(gdf, "avg_income", "Average Income (€)", cmap="PuOr")
            elif choice == "Priority Districts":
                plot_priority_map(gdf)
        with sub_tabs[2]:
            st.subheader("Technologies")
            tech_img = ROOT / "assets" / "heating_technologies_diagram.png"
            if tech_img.exists():
                st.image(str(tech_img), caption="Heating Technologies", use_container_width=True)
        with sub_tabs[3]:
            st.subheader("Stakeholders")
            stake_img = ROOT / "assets" / "stakeholders.png"
            if stake_img.exists():
                st.image(str(stake_img))

    # Measure
    with tabs[3]:
        st.header("(M) Measure")
        st.markdown("""
        **Measure Inputs**

        - Heating demand per square meter (kWh/m²·year)  
        - Final heating energy use (kWh/m²·year)  
        - Non-renewable CO₂ emissions intensity (kg/m²·year)  
        - Average household income (€)  
        - Retrofit readiness and associated costs  
        """)

        # Analyze
    with tabs[4]:
        st.header("(A) Analyze")

        analyze_tabs = st.tabs(["Overview", "Model Details"])

        with analyze_tabs[0]:
            st.subheader("Overview")
            st.write("Analysis overview content goes here.")

        with analyze_tabs[1]:
            st.subheader("Logistic Regression Tuned Model Details")

            model_path = ROOT / "assets" / "logreg_tuned_model.pkl"
            if model_path.exists():
                with open(model_path, "rb") as f:
                    model_obj = pickle.load(f)

                st.write(f"**Model type:** {type(model_obj)}")

                # Parameters
                if hasattr(model_obj, "get_params"):
                    st.write("**Parameters:**")
                    st.json(model_obj.get_params())

                # Coefficients
                if hasattr(model_obj, "coef_"):
                    st.write("**Coefficients:**")
                    st.write(model_obj.coef_)

                # Intercept
                if hasattr(model_obj, "intercept_"):
                    st.write("**Intercept:**")
                    st.write(model_obj.intercept_)

                # If you stored metrics in a dict
                if isinstance(model_obj, dict) and "metrics" in model_obj:
                    st.write("**Stored Metrics:**")
                    st.json(model_obj["metrics"])
            else:
                st.error("Model file not found in assets.")

    with tabs[5]:
        st.header("(I) Improve")
    with tabs[6]:
        st.header("(C) Control")

    # --- Scenario inputs ---
    budget = st.number_input("Budget (EUR)", min_value=0, value=50_000_000, step=1_000_000)
    subsidy_pct = st.slider("Subsidy % CAPEX", 0, 100, 0)
    opex_factor = st.number_input("OPEX ×", min_value=0.0, value=1.0, step=0.1, format="%.2f")
    co2_factor = st.number_input("CO₂ ×", min_value=0.0, value=1.0, step=0.05, format="%.2f")

    # --- Load your real data ---
    df = pd.read_csv("assets/df.csv")

    # Adoption rates (fill missing with default 0.3)
    adoption_rates = {10:0.420, 11:0.437, 12:0.437, 13:0.345, 15:0.343}
    df["adoption_rate"] = df["district_id"].map(adoption_rates).fillna(0.3)

    # Apply scenario levers
    df["OPEX"] = df.get("OPEX", 0) * opex_factor
    df["expected_capex_eur_subsidized"] = df["expected_capex_eur"] * (1 - subsidy_pct/100)
    df["total_cost"] = df["expected_capex_eur_subsidized"] + df["OPEX"]
    df["weighted_saving"] = df["expected_saving_kg"] * df["adoption_rate"] * co2_factor

    # --- Priority-first greedy selection ---
    priority = [10,11,12,13,15]
    others = sorted(set(df["district_id"]) - set(priority))

    selected = []
    budget_left = budget

    # Always include priority if budget allows
    for d in priority:
        cand = df[df["district_id"]==d].sort_values("total_cost")
        if not cand.empty:
            row = cand.iloc[0]
            if row["total_cost"] <= budget_left:
                selected.append(row)
                budget_left -= row["total_cost"]

    # Then greedy by district ID
    for d in others:
        cand = df[df["district_id"]==d].sort_values("total_cost")
        if not cand.empty:
            row = cand.iloc[0]
            if row["total_cost"] <= budget_left:
                selected.append(row)
                budget_left -= row["total_cost"]

    sel_df = pd.DataFrame(selected)

    # --- Format output ---
    sel_df["co2_emissions_reduce"] = (sel_df["weighted_saving"]/1000).round(0)
    sel_df["cost"] = sel_df["total_cost"].round(0)

    def fmt_money(x): return f"€{x:,.0f}".replace(",",".")
    def fmt_co2(x): return f"{int(x):,}".replace(",",".")+" tons/yr"

    report = sel_df[["district_id","tech","adoption_rate","co2_emissions_reduce","cost"]].copy()
    report["co2_emissions_reduce"] = report["co2_emissions_reduce"].apply(fmt_co2)
    report["cost"] = report["cost"].apply(fmt_money)

    total_cost = fmt_money(sel_df["total_cost"].sum())
    total_saving = fmt_co2(sel_df["co2_emissions_reduce"].sum())
    summary_row = pd.DataFrame([{
        "district_id":"TOTAL","tech":"—","adoption_rate":"—",
        "co2_emissions_reduce": total_saving,"cost": total_cost
    }])
    report = pd.concat([report, summary_row], ignore_index=True)

    st.subheader("Greedy rollout under budget")
    st.dataframe(report, use_container_width=True)
    st.metric("Total cost", total_cost)
    st.metric("Annual CO₂ reduced", total_saving)

    # --- Map view with st.map ---
    # You need a centroids table with lat/lon for each district
    centroids = pd.DataFrame({
        "district_id":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21],
        "lat":[40.42,40.40,40.41,40.43,40.45,40.47,40.44,40.50,40.46,
               40.39,40.37,40.36,40.38,40.41,40.35,40.48,40.34,40.35,
               40.37,40.44,40.49],
        "lon":[-3.70,-3.69,-3.68,-3.67,-3.68,-3.70,-3.71,-3.74,-3.72,
               -3.75,-3.72,-3.70,-3.67,-3.65,-3.63,-3.64,-3.69,-3.66,
               -3.61,-3.60,-3.62]
    })

    agg = sel_df.groupby("district_id", as_index=False).agg(
        co2_tons=("weighted_saving", lambda s: s.sum()/1000.0),
        cost_eur=("total_cost","sum")
    )
    agg = agg.merge(centroids, on="district_id", how="left")

    st.subheader("Map of selected districts")
    map_df = agg.rename(columns={"lat":"latitude","lon":"longitude"})[["latitude","longitude"]].dropna()
    if not map_df.empty:
        st.map(map_df)
    else:
        st.info("No coordinates available to plot map")
if __name__ == "__main__":
    main()
