# Low-Carbon Heating Roadmap for Madrid

General Objective:
---
Design a practical roadmap to evaluate how Madrid can adopt low-carbon heating systems, aligning technology rollout with mid-term policies, business goals, and investment priorities.

Specific Objectives:
1. Identify priority zones: Analyze historical emissions using public datasets and apply Pareto analysis to find the top 20% of districts responsible for 80% of heating-related emissions. Prioritize zones based on emissions intensity and socio-economic vulnerability.

2. Model technology adoption: Forecast adoption trends for heat pumps, district heating, gas boilers, and biomass boilers using predictive analytics and stochastic optimization — inspired by Toyota Production System and Six Sigma principles.

3. Build an interactive dashboard: Develop a Streamlit + Tableau dashboard to visualize emissions hotspots, simulate technology rollout, and present cost-benefit tradeoffs in € and % of emissions gap closed by 2030 — tailored for policymakers, citizens, and retrofit planners.

---

## Table of Contents

1. [Repo Structure](#repo-structure)  
2. [Quick Start](#quick-start)  
3. [Key Deliverables](#key-deliverables)  
4. [Data Sources](#data-sources)  
5. [License](#license)

---

## Repo Structure

```
├── .gitignore
├── README.md
├── config.yml
├── dashboard/
│   └── streamlit_app.py
├── data/
│   ├── raw/
│   │   ├── camaras_mc.csv
│   │   └── zbe_lpr.csv
│   └── spatial/
│       ├── Madrid_Central/              
│       │   ├── Madrid_Central.shp
│       │   └── Madrid_Central.shx
│       ├── PANEL_HOGARES/
│       │   ├── PANEL_HOGARES.shp
│       │   └── PANEL_HOGARES.shx
│       └── ZBE_MADRID/
│           ├── ZBE_MADRID_CAMARAS.shp
│           ├── ZBE_MADRID_CAMARAS.shx
│           ├── ZBE_MADRID_FOTO_ROJOS.shp
│           ├── ZBE_MADRID_FOTO_ROJOS.shx
│           ├── ZBE_TM.shp
│           └── ZBE_TM.shx
├── figures/
│   └── idae_madrid_heatmap.png
├── notebooks/
│   └── 01_load_datasets.ipynb
├── requirements.txt
├── sql/
│   ├── create_database.sql
│   └── query_database.sql
└── src/
    └── __init__.py
```
---
## Quick Start

1. **Clone the repository w/ terminal**:

```bash
git clone https://github.com/MBengochea/Low-Carbon-Heating-Roadmap-for-Madrid.git
```

2. **Install UV if you dont have it**

If you're a MacOS/Linux user type:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If you're a Windows user open an Anaconda Powershell Prompt and type :

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. **If you have UV, create an environment**

```bash
uv venv 
```

4. **Activate the environment**

If you're a MacOS/Linux user type (if you're using a bash shell):

```bash
source ./venv/bin/activate
```

If you're a MacOS/Linux user type (if you're using a csh/tcsh shell):

```bash
source ./venv/bin/activate.csh
```

If you're a Windows user type:

```bash
.venv\Scripts\activate
```

5. **Install dependencies**:

```bash
uv pip install -r requirements.txt
```
---
## **Data Sources**

1. **Greenhouse Gas Emissions Inventory – Comunidad de Madrid**  
   https://datos.comunidad.madrid/dataset/atm_inventario_gei  
   Provides sectoral emissions data across the region since 1990.  
   → Use to identify high-emission zones and quantify heating-related emissions for Pareto.

2. **Emissions by Sector – Particulate Matter (PST)**  
   https://datos.comunidad.madrid/dataset/1911600  
   Breaks down emissions by activity and pollutant type.  
   → Supports air quality validation and helps correlate heating sources with pollution hotspots.

3. **Energy Efficiency Certificates – Buildings**  
   https://datos.comunidad.madrid/catalogo/dataset/registro_certificados_eficiencia_energetica  
   Contains energy ratings for buildings.  
   → Filter by “Madrid” and join with district shapefiles to estimate heating demand.

4. **Final Gas Consumption by Sector**  
   https://datos.comunidad.madrid/dataset/950a60f0-498c-48db-84f4-734990d3e253  
   Shows fossil fuel usage by sector.  
   → Use to estimate current heating fuel dependency and model transition scenarios to low-carbon alternatives.

5. **Real-Time Air Quality – Madrid**  
   https://ciudadesabiertas.madrid.es/dynamicAPI/API/query/calair_tiemporeal.json?pageSize=5000  
   Live pollution data by station.  
   → Use to validate the impact of heating interventions on air quality and correlate with emissions zones.

6. **Low Emission Zone Cameras – Madrid ZBE**  
   https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=1e4991bfd349b810VgnVCM1000001d4a900aRCRD  
   Geolocated camera data and zone boundaries.  
   → Useful for mapping enforcement zones and aligning heating upgrades with air quality policies.

7. **Special Low Emission Zones – ZBEDEP Centro**  
   https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=019f24aaef3d3610VgnVCM1000001d4a900aRCRD  
   Shapefiles for protected zones.  
   → Use to overlay retrofit priorities and visualize policy-aligned intervention areas.

8. **District-Level Shapefiles – Geoportal Madrid**  
   https://geoportal.madrid.es/IDEAM_WBGEOPORTAL/descargasDisponibles.iam?fileIdent=aebec21d-5cad-11f0-9f8c-9009dfd270e9  
   Provides official district boundaries.  
   → Essential for spatial joins and mapping emissions, heating demand, and retrofit scenarios by district.
<!--
9. **3D Building Models – Geoportal Madrid**  
   https://geoportal.madrid.es/IDEAM_WBGEOPORTAL/dataset.iam?id=ece2d15a-d16f-46e8-aaec-9576771b9997
   High-resolution 3D geometry grouped by district.  
   → Use to visualize top 20% emission districts in 3D and overlay thematic data like retrofit cost or emissions gap closure.
-->
10. **Heating Technology Specs – Spain (IDAE, Eurostat, JRC, REE)**  
    `data/tech_specs/heating_technologies.csv`  
    Contains real-world cost, efficiency, and emissions data for four key heating technologies in Spain: air-source heat pumps, district heating, gas boilers, and biomass boilers.  
    → Used for scenario modeling, cost-benefit analysis, and emissions gap closure simulations.  
    Sources include:
    - [IDAE Air-Source Heat Pump Methodology Spain](https://www.idae.es/sites/default/files/estudios_informes_y_estadisticas/Metodologia_IDAE_reporte_ahorros_art-8_DEE_Bombas_de_calor.pdf)
    - [Euroheat District Heating Market Outlook 2025](https://www.euroheat.org/data-insights/outlooks/dhc-market-outlook-2025)
    - [Eurostat Energy Balances – Gas Boilers Spain](https://ec.europa.eu/eurostat/web/energy/data/energy-balances)
    - [REE National Statistical Series- Biomass Boilers Spain](https://www.ree.es/en/datos/publications/national-statistical-series)
---
