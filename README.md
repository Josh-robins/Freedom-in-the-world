# Freedom in the World — Data Analysis & Visualization

An educational data-science project analyzing the **Freedom in the World** dataset (Freedom House, published through World Bank Data360) between **2013 and 2026**.

**Guiding question:** *What does the Freedom in the World data reveal about the evolution, distribution and differences in political rights and civil liberties across economies between 2013 and 2026?*

The project is a complete, reproducible pipeline: dataset profiling → metadata and data dictionary → cleaning and reshaping → global trends → country analysis → regional analysis → indicator analysis → geographic visualization → an interactive Streamlit dashboard.

## Data source

- **Dataset ID:** `FH_FIW`
- **Producer:** Freedom House (https://freedomhouse.org/report/freedom-world)
- **Publisher:** World Bank Data360
- **Coverage:** 2013–2026, 197 economies, 40 indicators (per Data360 presentation)
- **Version:** 2026-08-01

The Freedom in the World survey assesses political rights and civil liberties using numerical ratings. Scores are based on implementation of rights in practice, not merely legal guarantees. **Higher scores always mean more freedom** (except the 1–7 ratings, which are inverted).

## Dataset structure

| File | Contents |
|---|---|
| `data/raw/FH_FIW_WIDEF.csv` | Wide-format export, 7880 rows (the complete 197 × 40 grid). Each row = one economy × one indicator series; ~38 metadata columns (`REF_AREA`, `INDICATOR`, `UNIT_MEASURE`, `*_LABEL`, …) precede the 14 year columns `2013`–`2026`. |
| `data/raw/FH_FIW.json` | Metadata / data dictionary: `database_description.ref_country` maps `REF_AREA` codes to economy names; also citation, license, time coverage. Indicator definitions are **not** in the JSON — they live in the CSV (`INDICATOR_LABEL`, `UNIT_MEASURE_LABEL`). |
| `data/processed/freedom_in_world_long.csv` | Cleaned long-format analytical dataset, 110,320 rows (economy × indicator × year). Produced by notebook 03; consumed by all later notebooks and the dashboard. |
| `data/processed/lookup_tables/` | Economy and indicator dictionaries (from notebook 02). |

### Indicator structure

Indicator codes are prefixed `FH_FIW_`:

- Question-level codes: **0–4** scale
- Category subtotals (seven freedom categories): **0–12 or 0–16**
- `FH_FIW_PR` (political rights): **0–40** · `FH_FIW_CL` (civil liberties): **0–60** · `FH_FIW_TOTAL` (overall): **0–100**
- Ratings (`PR_RATING` / `CL_RATING`): **1–7, inverted** — 1 = most free, 7 = least free
- `FH_FIW_STATUS`: **categorical** — Free / Partly Free / Not Free

The overall score is **exactly** political rights plus civil liberties (verified in notebook 05). Scores on different scales are **not comparable without normalization** — the dashboard plots everything as % of scale.

## Project structure

```text
Freedom/
├── data/
│   ├── raw/                  # FH_FIW_WIDEF.csv, FH_FIW.json (never modified)
│   └── processed/            # freedom_in_world_long.csv, lookup_tables/
├── notebooks/                # 01_dataset_profiling.ipynb … 08_geographic_analysis.ipynb
├── src/                      # Reusable helpers (loading, cleaning, regions, visualizations)
├── dashboard/                # Streamlit app
│   ├── app.py                #   Home (metrics + status map)
│   ├── pages/                #   Map Explorer, Country Explorer, Global Trends,
│   │                         #   Regional Analysis, Indicator Explorer
│   └── components/charts.py  #   Shared chart rendering, themes, helpers
├── .streamlit/config.toml    # Dark-theme configuration
├── outputs/                  # figures/, tables/, reports/
├── docs/
└── requirements.txt
```

## Setup

Requires Python 3.11+ (developed on 3.14).

```bash
# 1. Create the virtual environment
python -m venv .venv

# 2. Activate it
#    Windows (PowerShell):  .venv\Scripts\Activate.ps1
#    Windows (cmd):         .venv\Scripts\activate.bat
#    macOS/Linux:           source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

> **OneDrive note:** this project lives under an OneDrive-synced folder. Exclude `.venv` from OneDrive sync (Settings → Account → Choose folders → exclude `Freedom/.venv`) to avoid syncing thousands of small files and recurring file-lock issues.

## Usage

### Notebooks (the analysis pipeline)

Start Jupyter, open `notebooks/`, and run 01 → 08 in order:

```bash
jupyter notebook
```

The notebooks are the documented analysis: profiling (01), metadata & data dictionary (02), cleaning & reshaping (03), global trends (04), country analysis (05), regional analysis (06), indicator analysis (07), geographic analysis (08). The long dataset created in notebook 03 feeds everything after it.

### Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard consumes only the processed long dataset, never the raw CSV. **Design:** a black dark theme with amber accents; charts in bordered cards; **all maps share a publication navy style** (`#0E2A45`) with thin country borders, Natural Earth projection, no axes, no zoom (the only chart action is PNG download), and a "Designed by Josh" footer.

**Pages:**

| Page | What it offers |
|---|---|
| **Home** | 8 key metrics, then the headline **FREEDOM IN THE WORLD** status map (Free `#00A767` / Partly Free `#D5A616` / Not Free `#9260A8`), then global trend and status-mix charts |
| **Map Explorer** | Publication-style status map (world/Africa, year selector, dynamic title) plus level and change maps for every major indicator — all as % of scale with a "Not free → Free" colorbar; **Download Map (PNG)** button exports at 2800×1800 |
| **Country Explorer** | Trends, indicator profiles and comparisons for any economy |
| **Global Trends** | Mean trends, distributions, year-over-year movement |
| **Regional Analysis** | UN M49 main regions and Africa sub-regions, with the region × category heatmap |
| **Indicator Explorer** | The summary indicators and seven categories, one at a time, with trends, extremes and a map |

Regional groupings (EAC, P5+G7, UN M49) are documented external classifications approved for this project — never invented.

## Cleaning methodology

- The raw files in `data/raw/` are **never modified**; all cleaning output goes to `data/processed/`.
- The wide CSV is melted into long format; year values are converted to integers and scores to numeric (the categorical status stays as text).
- **Missing values are never imputed** — missing data stays missing unless a documented analytical reason says otherwise.
- Cleaning decisions are documented in notebook 03.

## Scope & limitations

- **No machine learning** (no clustering, PCA, classification, forecasting, neural networks) in the current version.
- **No external datasets** (GDP, education, conflict, etc.) — analysis stays entirely within the Freedom in the World data.
- **No causal claims** — the project distinguishes observation (scores changed) from interpretation (per the FiW system) and does not attempt external explanation.
- Indicator and economy definitions are taken from the source metadata only; nothing is invented.
- Regional classification is only used where documented and approved.

## License & citation

Freedom House content may be used for non-commercial purposes with proper citation.

> Freedom House. (Year). Freedom in the World Year. Retrieved from https://freedomhouse.org/report/freedom-world#Data

## Reproducibility

Installations use minimum-version constraints (`requirements.txt`). For an exact, reproducible environment, freeze the installed versions after setup:

```bash
pip freeze > requirements.lock.txt
```

Reinstalling from `requirements.lock.txt` reproduces the environment byte-for-byte.
