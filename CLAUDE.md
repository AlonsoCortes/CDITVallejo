# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Geospatial and sociodemographic analysis of the CDIT Vallejo-i area in Mexico City, built by SECTEI CDMX. Processes 2020 Census data, DENUE 2025 economic units, and public transport networks at block (manzana) level. Produces an interactive geovisor deployed via GitHub Pages.

**Language:** Project documentation, variable names, and comments are in Spanish.

## Setup

```bash
uv sync                          # Install dependencies (preferred)
pip install -r requirements.txt  # Alternative
```

Requires Python >= 3.10 (pinned to 3.10 in `.python-version`). Uses `uv` as package manager.

## Architecture

### Data Pipeline (3 stages in `datos/`)

1. **`00_insumos/`** — Raw GeoPackage layers (`.gpkg`, git-ignored)
2. **`01_procesos/`** — Intermediate processing outputs
3. **`02_finales/`** — Final GeoJSONs consumed by the geovisor

### Processing Notebooks (`notebooks/`)

Executed in this order for the full pipeline:

1. `nb_descargaDENUE.ipynb` — Downloads economic units from INEGI API via `inegipy`
2. `nb_informacionCenso.ipynb` — Imports and cleans census data at block level
3. `nb_informacionCensoAnalisis.ipynb` — Calculates percentage variables (`pct_*`) with appropriate denominators
4. `nb_analisisDENUE.ipynb` — Economic units analysis
5. `nb_isodistancia_cdit.ipynb` — Isodistance network analysis from CDIT using `osmnx`

### Shared Utilities (`notebooks/utils_censo.py`)

Handles INEGI census special codes:
- `-6` ("no aplica") — treated via `tratar_no_aplica()` (replaced with 0)
- `-8` (confidential) — treated via `tratar_confidencial()` with strategies: `nan`, `zero`, `median`, `mean`, `valor_bajo`
- `tratar_censurados()` combines both treatments
- `diagnostico_censurados()` provides summary of censored values

### Geovisor (`docs/`)

Client-side interactive map at `docs/index.html`, deployed via GitHub Pages from the `docs/` directory. Built with Leaflet.js (mapping) + Chart.js (statistics). Reads GeoJSONs from `docs/datos/` (copies of `datos/02_finales/`).

Features: choropleth maps of 36 census variables with quintile classification, layer toggling (transport, PILARES, CDIT), descriptive statistics with histograms.

## Key Conventions

- GeoPackage files (`.gpkg`) are git-ignored; GeoJSON is used for version-controlled outputs
- Census variables follow the pattern: raw count (`pob_total`) + percentage version (`pct_pob_total`)
- Data files use snake_case with geographic context suffixes (e.g., `_zecditvallejo`)
- When modifying the geovisor, final GeoJSONs must be copied to both `datos/02_finales/` and `docs/datos/`
