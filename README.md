# Are Australia's Frogs Disappearing?

A one-page data story for FIT3179 Data Visualisation 2 (Monash University, Semester 2, 2026).
It combines FrogID sightings, the national threatened species list and the Threatened Frog Index.
Author: Ryoma Kano. Date: 25 October 2026.

## Folders

| Folder | Content |
|---|---|
| `index.html` | The page (text, layout). |
| `css/styles.css` | The style of the page. |
| `js/main.js` | Draws each chart into its `<div>`. |
| `js/*.vg.json` | One Vega-Lite specification per chart (readable JSON, not minified). |
| `data/` | The small data files that the charts read (CSV and one TopoJSON map). |
| `scripts/` | Python scripts for preparing the chart data, plus an optional local test server. |

## File names

- Chart specifications: `js/NN_topic_idiom.vg.json`. NN is the number of the chart (the order on the page is in the table below; the rank chart, 13, is in section 4).
- Data files: `data/source_content.csv`. The start of the name is the source: `frogid_` (FrogID), `dcceew_` (threatened species list), `ala_` (Atlas of Living Australia), `tsx_` (Threatened Frog Index).
- All names are lower case, with underscores and no spaces.

## Charts

13 charts: three maps (choropleth, proportional symbol map, bin map), heat map, waffle chart, lollipop chart, bump chart, slope chart, streamgraph, Gantt chart, stacked bar chart, and two line charts.

| Page section | Chart | Specification |
|---|---|---|
| 1 | Threatened Frog Index (line) | `js/01_tsx_index_line.vg.json` |
| 1 | Threatened frog types by status (waffle) | `js/02_status_waffle.vg.json` |
| 2 | Share of recorded frog species that are on the threatened list, by state (choropleth map) | `js/03_state_share_choropleth.vg.json` |
| 2 | Listed frog types by state and status (stacked bar) | `js/04_status_by_state_stacked_bar.vg.json` |
| 3 | Listed frogs with the most records (lollipop) | `js/05_threatened_records_lollipop.vg.json` |
| 3 | Threatened share of frog records (bin map) | `js/06_threatened_share_bin_map.vg.json` |
| 4 | FrogID records per year (line) | `js/07_records_per_year_line.vg.json` |
| 4 | FrogID records by area (proportional symbol map) | `js/08_records_by_area_symbol_map.vg.json` |
| 4 | Share of FrogID records by state, 2018 and 2023 (slope) | `js/09_state_share_slope.vg.json` |
| 4 | Rank of the 10 most recorded species (bump) | `js/13_species_rank_bump.vg.json` |
| 5 | Records by month and state (heat map) | `js/10_month_state_heat_map.vg.json` |
| 5 | Months with more records than usual (Gantt) | `js/11_calling_season_gantt.vg.json` |
| 5 | Records by month for four species (streamgraph) | `js/12_species_month_streamgraph.vg.json` |

## Data sources

Data were downloaded on 5 October 2026.

- **FrogID**, Australian Museum (dataset 7.0, November 2017 to November 2024, via the Atlas of Living Australia, data resource dr14760): frog records by state, year, month, species and area. Rowley, J. J. L. & Callaghan, C. T. (2020). Licence CC BY-NC 4.0.
  https://www.frogid.net.au/science/map-and-data/
- **Atlas of Living Australia**: records of all frogs (all contributors), for the bin map, the share of listed frogs and the most recorded listed frogs. Licence varies by contributor.
  https://www.ala.org.au/
- **Department of Climate Change, Energy, the Environment and Water**: Threatened Species State Lists, 28 August 2026 (status of 53 listed frog types, states where they occur). Licence CC BY 3.0 AU.
  https://data.gov.au/data/dataset/threatened-species-state-lists
- **Threatened Species Index (TSX)**, TERN and The University of Queensland: Threatened Frog Index 2025 (decline of threatened frogs, 1985 to 2022). Licence CC BY 4.0.
  https://tsx.org.au/visualising-the-index/the-threatened-frog-index-2025/
- **Natural Earth**: Admin 1 states and provinces, for the state borders (public domain).
  https://www.naturalearthdata.com/

## How the data files were made

The raw downloads are not in this repository (they are large). They were summed up with the scripts in `scripts/`:

| Script | Makes |
|---|---|
| `make_state_table.py` | `data/ala_listed_share_by_state.csv` (frog species recorded per state, and how many are on the threatened list) |
| `make_bin_grid.py` | `data/ala_threatened_share_bins.csv` (100 km x 100 km squares for the bin map) |
| `make_map2_data.py` | `data/frogid_records_by_area.csv` (circles for the proportional symbol map) |
| `make_chart_data.py` | All other small files in `data/` |

The scripts are published so that every number in `data/` can be traced back. They read the raw downloads from `data/raw/`, which is not part of this repository, so they cannot be run without downloading those files again (see the sources above and the data snapshot below). Each script starts with a short description of its input files and the rules it applies (for example, the minimum number of records). Run a script from the project root with `python3 scripts/<name>.py` (Python 3, standard library only).

The state borders were cut out of the Natural Earth file with mapshaper.org and saved as TopoJSON (`data/australia_states.topojson`).

### Data snapshot and how the Atlas of Living Australia (ALA) data were collected

- **The data are a snapshot of 5 October 2026** (DCCEEW list of 28 August 2026, Threatened Frog Index 2025, FrogID dataset 7.0). They were not refreshed afterwards. ALA is updated all the time, so a new download would show slightly more records.
- The ALA numbers were collected from the ALA occurrence API (`https://api.ala.org.au/occurrences/occurrences/facets`) with these filters:
  - FrogID: `fq=data_resource_uid:dr14760`, together with `facets=year`, `month`, `stateProvince`, `species` or the 0.1 degree grid `point-0.1`; for the tables by state, month or species, one more `fq` such as `stateProvince:"<state>"`, `year:<year>` or `species:"<name>"` was added.
  - All Australian frogs (all contributors): `fq=class:Amphibia` and `fq=country:Australia`, with `facets=species`, `stateProvince` or `point-0.1`.
  - Listed (threatened) frogs: `fq=species:("<name>" OR ...)` with the scientific names of the non-extinct amphibians of the DCCEEW list (without *Litoria verreauxii*), and `fq=country:Australia`, with `facets=point-0.1`.
- The data were collected with the help of an AI assistant (see "Use of AI"). The queries were run again on 7 October 2026 with AI assistance, and the results were compared with the saved files: the FrogID numbers used for the charts were identical; the numbers for all contributors differed slightly (mostly higher, by less than 0.1% in total), probably because ALA changed after the download.

## Use of AI

The author built the charts from the unit's Vega-Lite templates. Claude helped write and edit parts of the code, reviewed it, gave advice on how to process the data, and helped proofread and format the English text. The author chose the topic, story, charts and design, did the final checks and decided the content of the text.

## Local development

Open the project root folder (`fit3179-dv2`) in VS Code. Right-click `index.html` and choose **Open with Live Server**, then use the local URL shown by Live Server. The page loads chart specifications from `js/` and their data from `data/`; previewing a `.vg.json` file on its own will not display the full page.

As an alternative to Live Server, `scripts/dev_server.py` serves the project folder on `http://127.0.0.1:8765` and tells the browser not to cache files, so edits to `.vg.json` and `.csv` files show up after a reload. Run `python3 scripts/dev_server.py` from the project root and open that address. It is only a helper for testing; the published page does not use it.
