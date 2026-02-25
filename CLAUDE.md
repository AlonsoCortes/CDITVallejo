# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Geospatial and sociodemographic analysis of the CDIT Vallejo-i area in Mexico City, built by SECTEI CDMX. Processes 2020 Census data, DENUE 2025 economic units, and public transport networks at AGEB and block (manzana) level. Produces an interactive geovisor deployed via GitHub Pages.

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
4. `nb_analisisDENUE.ipynb` — Economic units analysis; produces `unidades_economicas_cdit_2025.geojson`
5. `nb_isodistancia_cdit.ipynb` — Isodistance network analysis from CDIT using `osmnx`

### Shared Utilities (`notebooks/utils_censo.py`)

Handles INEGI census special codes:
- `-6` ("no aplica") — treated via `tratar_no_aplica()` (replaced with 0)
- `-8` (confidential) — treated via `tratar_confidencial()` with strategies: `nan`, `zero`, `median`, `mean`, `valor_bajo`
- `tratar_censurados()` combines both treatments
- `diagnostico_censurados()` provides summary of censored values

### Geovisor (`docs/`)

Client-side interactive map deployed via GitHub Pages from the `docs/` directory. Built with Leaflet.js (mapping) + Chart.js (statistics). Reads GeoJSONs from `docs/datos/` (copies of `datos/02_finales/`).

#### Geovisor files

| File | Description |
|---|---|
| `docs/index.html` | Entry point — redirects to `index_agebs.html` |
| `docs/index_agebs.html` | **Main geovisor** — Census 2020 at AGEB level |
| `docs/index_manzanas.html` | Geovisor — Census 2020 at manzana (block) level |

#### Geovisor features (`index_agebs.html`)

- **Choropleth** of 36 census variables (6 thematic groups) with quintile classification
- **Layer panel** with individual toggles and opacity slider for the choropleth
- **Statistics panel** — descriptive stats + histogram (Chart.js) per variable
- **Point layers** (each independently togglable):
  - CDIT Vallejo-i — custom CDMX government icon
  - PILARES — `divIcon` circular red marker with "P"
  - Transporte público — Metro STC (`logo_metro_cdmx.svg`), Metrobús (`logo_metrobus_cdmx.svg`), CETRAM (red circle), Tren Suburbano (blue circle), RTP (grey circle)
  - Unidades económicas CDIT 2025 — 6 categories with individual toggles + master checkbox with indeterminate state

#### DENUE economic units categories (`categoria_cdit`)

| ID | Category | Color |
|---|---|---|
| `ue-apoyo` | Apoyo a negocios y emprendimiento | `#f59e0b` |
| `ue-diseno` | Diseño y economía creativa | `#8b5cf6` |
| `ue-educacion` | Educación y capacitación | `#3b82f6` |
| `ue-manufactura` | Manufactura tecnológica e industria avanzada | `#ef4444` |
| `ue-servicios` | Servicios profesionales, científicos y técnicos | `#14b8a6` |
| `ue-tecnologia` | Tecnología, informática y telecomunicaciones | `#6366f1` |

#### GeoJSON data files (`docs/datos/`)

| File | Description |
|---|---|
| `agebs_censo_pct_zecditvallejo.geojson` | Census 2020 variables at AGEB level |
| `manzanas_censo_pct_zecditvallejo.geojson` | Census 2020 variables at manzana level |
| `unidades_economicas_cdit_2025.geojson` | DENUE 2025 economic units (2,200 features) |
| `estaciones_transporte_publico.geojson` | Public transport stations (Metro, Metrobús, RTP, CETRAM, Tren Suburbano) |
| `pilares.geojson` | PILARES community centres |
| `ubicacion_ceditvallejo.geojson` | CDIT Vallejo-i location |
| `logo_metro_cdmx.svg` | Metro CDMX official logo (used as map marker) |
| `logo_metrobus_cdmx.svg` | Metrobús CDMX official logo (used as map marker) |

## Key Conventions

- GeoPackage files (`.gpkg`) are git-ignored; GeoJSON is used for version-controlled outputs
- Census variables follow the pattern: raw count (`pob_total`) + percentage version (`pct_*`)
- Data files use snake_case with geographic context suffixes (e.g., `_zecditvallejo`)
- When modifying the geovisor, final GeoJSONs must be copied to both `datos/02_finales/` and `docs/datos/`
- Transport stations use `SISTEMA` field to distinguish provider: `'STC Metro'`, `'Metrobús'`, `'Red de Transporte de Pasajeros'`
