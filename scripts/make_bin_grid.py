"""Build data/ala_threatened_share_bins.csv for the bin map (chart 06).

Inputs (data/raw/), all from ALA (api.ala.org.au, facet `point-0.1` = 0.1 degree cells):
  ala_threatened_listed/ala_threatened_grid_point-0.1.json   records of EPBC-listed amphibians (non-extinct, 44 species)
  ala_amphibia_all_contributors/ala_all_amphibia_grid_point-0.1.json records of all Amphibia in Australia

The bins are squares on the flat map, not on the lat/lon grid. The maps use the Albers equal-area
projection (parallels -18 and -36, central meridian 132), so equal squares on the map are equal
areas on the ground: every bin covers the same amount of land (BIN_KM x BIN_KM). A lat/lon grid
would give smaller bins in the south.

Each 0.1 degree cell is placed in a bin by its centre. share_threatened = threatened records /
all amphibian records in the bin (a fraction of a total, so it does not just copy where people
record frogs). Bins with fewer than MIN_TOTAL amphibian records are dropped (share too noisy).
The output has the lat/lon of two opposite corners of each square, which is what Vega-Lite's
`rect` mark needs (longitude/latitude and longitude2/latitude2).
"""
import csv, json, math
from pathlib import Path

BIN_KM = 100
MIN_TOTAL = 50
PARALLELS = (-18.0, -36.0)
CENTRAL_MERIDIAN = 132.0
R = 6371.0  # earth radius in km

root = Path(__file__).resolve().parent.parent
raw = root / "data" / "raw"

# Albers equal-area conic (same formulas as d3-geo's conicEqualArea, with the origin at the equator)
# Set up the constants used to convert longitude/latitude to distances in kilometres.
y0, y1 = (math.radians(p) for p in PARALLELS)
n = (math.sin(y0) + math.sin(y1)) / 2
c = 1 + math.sin(y0) * (2 * n - math.sin(y0))
r0 = math.sqrt(c) / n


def forward(lon, lat):
    # Put a geographic point on the flat, equal-area map before assigning a square.
    lam = math.radians(lon - CENTRAL_MERIDIAN) * n
    r = math.sqrt(c - 2 * n * math.sin(math.radians(lat))) / n
    return R * r * math.sin(lam), R * (r0 - r * math.cos(lam))


def inverse(x, y):
    # Convert a square's map coordinates back to longitude/latitude for Vega-Lite.
    x, y = x / R, y / R
    r0y = r0 - y
    lam = math.atan2(x, abs(r0y)) * (1 if r0y > 0 else -1)
    lat = math.asin((c - (x * x + r0y * r0y) * n * n) / (2 * n))
    return CENTRAL_MERIDIAN + math.degrees(lam / n), math.degrees(lat)


def load(name):
    # Add each small ALA cell's count to its containing 100 km square.
    bins = {}
    for item in json.load(open(raw / name)):
        lat, lon = (float(v) for v in item["label"].split(","))
        x, y = forward(lon + 0.05, lat + 0.05)  # centre of the 0.1 degree cell
        # Floor division gives the same (column, row) key to points in one square.
        key = (math.floor(x / BIN_KM), math.floor(y / BIN_KM))
        bins[key] = bins.get(key, 0) + item["count"]
    return bins


threatened = load("ala_threatened_listed/ala_threatened_grid_point-0.1.json")
total = load("ala_amphibia_all_contributors/ala_all_amphibia_grid_point-0.1.json")

rows = []
for (i, j), n_all in sorted(total.items()):
    # Small totals make the percentage unstable, so omit these squares.
    if n_all < MIN_TOTAL:
        continue
    n_thr = threatened.get((i, j), 0)
    # Vega-Lite's rect mark needs two opposite corners of each square.
    lon_a, lat_a = inverse(i * BIN_KM, j * BIN_KM)
    lon_b, lat_b = inverse((i + 1) * BIN_KM, (j + 1) * BIN_KM)
    rows.append({
        "longitude": round(lon_a, 4), "latitude": round(lat_a, 4),
        "longitude2": round(lon_b, 4), "latitude2": round(lat_b, 4),
        "all_records": n_all, "threatened_records": n_thr,
        # This is a share of ALA records, not a share of individual frogs.
        "share_threatened": round(100 * n_thr / n_all, 1),
    })

dest = root / "data" / "ala_threatened_share_bins.csv"
with open(dest, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print(len(rows), "bins of", BIN_KM, "km x", BIN_KM, "km; wrote", dest)
