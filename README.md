Low-Carbon Heating Roadmap for Madrid
Quantitative roadmap & technology portfolio for decarbonizing Madrid’s heating systems

Table of Contents
Repo Structure

Quick Start

Key Deliverables

Data Sources

License

Repo Structure
text
project
│   README.md                 # overview & instructions
│   requirements.txt          # dependency list
│
├── data_ingest               # fetch & stage raw data
│   ├ fetch_footfall.py
│   └ fetch_climate.py
│
├── calculations              # analysis notebooks
│   ├ figures_of_merit.ipynb
│   └ trade_space_analysis.ipynb
│
├── models                    # scoring & portfolio scripts
│   ├ architecture_scoring.py
│   └ portfolio_selection.py
│
├── dashboards                # Streamlit app
│   └ streamlit_app.py
│
└── reports                   # stakeholder deliverables
    ├ executive_summary.pdf
    └ presentation_slides.pptx
´´´
Quick Start
bash
git clone https://github.com/your-username/madrid-heating-decarbonization.git
cd madrid-heating-decarbonization

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python data_ingest/fetch_footfall.py
python data_ingest/fetch_climate.py

python models/architecture_scoring.py
python models/portfolio_selection.py

streamlit run dashboards/streamlit_app.py
Key Deliverables
Quantitative Figures of Merit for seven system architectures

Tradespace charts (cost vs performance vs risk)

Optimized €500 M five-year investment roadmap

Streamlit dashboard for real-time pilot insights

Executive summary & stakeholder slide deck

Data Sources
Madrid Open Data: climate, footfall, energy

[Add additional public APIs here]

License
All rights reserved. No license granted.
