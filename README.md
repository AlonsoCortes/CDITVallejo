# Análisis territorial CDIT Vallejo-i

Repositorio de análisis geoespacial y sociodemográfico del entorno del **Centro de Desarrollo e Innovación Tecnológica Vallejo-i** (CDIT Vallejo-i), elaborado por la Secretaría de Educación, Ciencia, Tecnología e Innovación de la Ciudad de México (**SECTEI CDMX**).

El estudio caracteriza la Zona de Equipamiento Colectivo e Industrial Tlalnepantla–Vallejo (ZEC CDIT Vallejo) a partir del Censo de Población y Vivienda 2020, el Directorio Estadístico Nacional de Unidades Económicas (DENUE 2025) y redes de transporte público, con resolución a nivel manzana.

**Geovisor:** [AlonsoCortes.github.io/CDITVallejo](https://AlonsoCortes.github.io/CDITVallejo/)

---

## Estructura del repositorio

```
CDITVallejo/
├── datos/
│   ├── 00_insumos/          # Capas base sin procesar (GeoPackage)
│   │   ├── agebs_zonaestudio.gpkg
│   │   ├── manzanas_zonaestudio.gpkg
│   │   ├── ubicacion_cditvallejo.gpkg
│   │   └── unidadeseconomicas_denue_2025.gpkg
│   ├── 01_procesos/         # Capas intermedias de procesamiento
│   │   ├── agebs_datoscenso_zecditvallejo.gpkg
│   │   ├── isodistancias_cditvallejo.geojson
│   │   ├── malla_hexagonos_cditvallejo.gpkg
│   │   ├── manzanas_datoscenso_zecditvallejo.gpkg
│   │   └── unidades_economicas_2025.gpkg
│   └── 02_finales/          # GeoJSONs listos para el geovisor
│       ├── agebs_censo_pct_zecditvallejo.geojson
│       ├── estaciones_transporte_publico.geojson
│       ├── manzanas_censo_pct_zecditvallejo.geojson
│       └── pilares.geojson
├── docs/                    # Geovisor (GitHub Pages)
│   ├── index.html
│   └── datos/               # Copia de los GeoJSONs finales
├── notebooks/
│   ├── nb_descargaDENUE.ipynb          # Descarga de DENUE via API
│   ├── nb_analisisDENUE.ipynb          # Análisis de unidades económicas
│   ├── nb_informacionCenso.ipynb       # Procesamiento de datos censales
│   ├── nb_informacionCensoAnalisis.ipynb # Cálculo de variables pct_*
│   ├── nb_isodistancia_cdit.ipynb      # Isodistancias desde el CDIT
│   ├── proyecto_qgis_CDITVallejo.qgz   # Proyecto QGIS
│   └── utils_censo.py                  # Utilidades compartidas
├── pyproject.toml
└── requirements.txt
```

---

## Datos

### Censo de Población y Vivienda 2020 — nivel manzana

Variables incluidas en `manzanas_censo_pct_zecditvallejo.geojson`:

| Grupo | Variables |
|-------|-----------|
| Población | `pob_total`, `pob_fem`, `pob_masc`, `den_pob_ha` |
| Grupos de edad | `pob_15_24`, `pob_30_49`, `pob_50_59`, `pob_60_mas`, … |
| Educación | `pob_alfabeta`, `pob_analfabeta`, `pob_sin_escolaridad`, `pob_superior`, … |
| Actividad económica | `pea`, `pob_ocupada`, `pob_desocupada`, `pob_no_pea`, … |
| Vivienda | `viv_habitadas`, `viv_elect`, `viv_agua`, `viv_drenaje`, `viv_hacinada`, … |
| Tecnología | `viv_comp`, `viv_cel`, `viv_internet`, … |

Cada variable cuenta con su versión porcentual (`pct_*`) calculada con el denominador apropiado según el universo de referencia del Censo (ver `nb_informacionCensoAnalisis.ipynb`).

### DENUE 2025

Unidades económicas dentro de la zona de estudio descargadas mediante la API del INEGI (`inegipy`). Análisis en `nb_analisisDENUE.ipynb`.

### Capas complementarias

| Archivo | Contenido |
|---------|-----------|
| `pilares.geojson` | Puntos de acceso PILARES en el área de influencia |
| `estaciones_transporte_publico.geojson` | Metro, Metrobús, Tren Suburbano y CETRAMs |
| `ubicacion_ceditvallejo.geojson` | Ubicación del CDIT Vallejo-i |

---

## Geovisor

El geovisor interactivo está disponible en **[AlonsoCortes.github.io/CDITVallejo](https://AlonsoCortes.github.io/CDITVallejo/)** y es servido desde la carpeta `docs/` vía GitHub Pages.

Permite:

- **Visualizar coropléticos** de las 36 variables censales a nivel manzana con clasificación por quintiles
- **Alternar entre capas** de puntos: CDIT Vallejo-i, PILARES y estaciones de transporte
- **Consultar estadísticos descriptivos** (mínimo, máximo, media, mediana, desviación estándar) e histograma de distribución para cualquier variable seleccionada

Construido con [Leaflet.js](https://leafletjs.com/) y [Chart.js](https://www.chartjs.org/), sin dependencias de servidor.

---

## Configuración del entorno

El proyecto usa [uv](https://docs.astral.sh/uv/) como gestor de paquetes con Python ≥ 3.10.

```bash
# Instalar dependencias
uv sync

# O con pip
pip install -r requirements.txt
```

**Dependencias principales:** `geopandas`, `osmnx`, `inegipy`, `matplotlib`, `scipy`, `ipykernel`

---

## Fuentes

- **INEGI** — Censo de Población y Vivienda 2020
- **INEGI** — DENUE 2025
- **SECTEI CDMX** — Directorio de PILARES
- **SEMOVI CDMX** — Red de transporte público
