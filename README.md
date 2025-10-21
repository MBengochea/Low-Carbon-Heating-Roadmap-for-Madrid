# Low-Carbon Heating Roadmap for Madrid

General Objective:
```
Design a data-driven roadmap to accelerate the adoption of low-carbon heating systems in Madrid, optimizing environmental impact, cost-efficiency, and urban integration using reproducible analytics and operational methodologies. Using only Madrid’s open data and public APIs.
```
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
6. **Ingest data**:
   
python data_ingest/fetch_footfall.py

python data_ingest/fetch_climate.py

7. **Run models**:
   
python models/architecture_scoring.py

python models/portfolio_selection.py

8. **Launch dashboard**:
    
streamlit run dashboards/streamlit_app.py

---
## Key Deliverables

- Quantitative Figures of Merit for seven system architectures  
- Tradespace charts (cost vs performance vs risk)  
- Optimized €500 M five-year investment roadmap  
- Streamlit dashboard for real-time pilot insights  
- Executive summary & stakeholder slide deck
---
## Data Sources

- Madrid Open Data: climate, footfall, energy  
- [Add additional public APIs here]
---
## License

All rights reserved. No license granted.
