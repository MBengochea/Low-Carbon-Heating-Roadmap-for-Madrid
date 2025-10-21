# Low-Carbon Heating Roadmap for Madrid

General Objective:
---
Design a data-driven roadmap to accelerate the adoption of low-carbon heating systems in Madrid, optimizing environmental impact, cost-efficiency, and urban integration using reproducible analytics and operational methodologies. Using only Madrid’s open data and public APIs.

Specific Objectives:
1. Diagnose emissions hotspots Quantify residential heating emissions across Madrid using public datasets, and apply Pareto analysis to identify the top 20% zones responsible for 80% of emissions. Prioritize areas based on emissions intensity and socio-economic vulnerability.

2. Simulate low-carbon adoption Model rollout scenarios for heat pumps and district heating using predictive analytics and stochastic optimization, inspired by Toyota Production System and Six Sigma principles.

3. Visualize impact and tradeoffs Build an interactive dashboard (Streamlit + Tableau) to map emissions hotspots, simulate technology adoption, and present cost-benefit outcomes in € and % emissions gap closed by 2030 — for policymakers and citizens.

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
project
│   README.md           # overview & instructions
│   requirements.txt    # dependency list
│
├── data_ingest         # fetch & stage raw data
│   ├ fetch_footfall.py
│   └ fetch_climate.py
│
├── calculations        # analysis notebooks
│   ├ figures_of_merit.ipynb
│   └ trade_space_analysis.ipynb
│
├── models              # scoring & portfolio scripts
│   ├ architecture_scoring.py
│   └ portfolio_selection.py
│
├── dashboards          # Streamlit app
│   └ streamlit_app.py
│
└── reports             # stakeholder deliverables
    ├ executive_summary.pdf
    └ presentation_slides.pptx
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
## Data Sources
  1_gei:
    title: Inventario Gases de Efecto Invernadero
    source: https://datos.comunidad.madrid/api/3/action/package_show?id=atm_inventario_gei
    format: CSV
    path: data/raw/gei.csv

  2_pst:
    title: Emisión de contaminantes atmosféricos por sectores: PST
    source: https://datos.comunidad.madrid/api/3/action/package_show?id=1911600
    format: CSV
    path: data/raw/pst.csv

  3_ceee:
    title: Registro de Certificados de Eficiencia Energética
    source: https://datos.comunidad.madrid/api/3/action/package_show?id=registro_certificados_eficiencia_energetica
    format: CSV
    path: data/raw/ceee.csv

  4_gas:
    title: Consumo final de gas natural por sectores
    source: https://datos.comunidad.madrid/api/3/action/package_show?id=950a60f0-498c-48db-84f4-734990d3e253
    format: CSV
    path: data/raw/gas.csv

  5_air_quality:
    title: Calidad del Aire en Tiempo Real
    source: https://ciudadesabiertas.madrid.es/dynamicAPI/API/query/calair_tiemporeal.json?pageSize=5000
    format: JSON
    path: data/raw/air_quality.json

  6_zbe:
    title: Cámaras ZBE + Zona Interior M30
    source: https://datos.madrid.es/egob/catalogo/300234-0-zbe-interior-m30.zip
    format: ZIP (CSV + SHP)
    path: data/spatial/zbe_zone.zip

  7_zbedep:
    title: ZBEDEP Centro
    source: https://datos.madrid.es/egob/catalogo/300234-0-zbedep-centro.zip
    format: ZIP (CSV + SHP)
    path: data/spatial/zbedep_zone.zip

  8_districts:
    title: Distritos Madrid
    source: https://geoportal.madrid.es/IDEAM_WBGEOPORTAL/descargas/IDEAM/Cartografia/Unidad_Administrativa/Distritos/Distritos_Madrid.zip
    format: ZIP (SHP)
    path: data/spatial/distritos_madrid.zip

---
