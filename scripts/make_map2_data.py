"""Build data/frogid_records_by_area.csv for the proportional symbol map (chart 08).

Input (data/raw/ala_frogid_dr14760/): ala_frogid_grid_point-0.1.json
  FrogID records (ALA data resource dr14760) counted in 0.1 degree cells; each label is "lat,lon" of the cell's south-west corner.

The 0.1 degree cells are added up into 3 x 3 degree areas (degrees, not kilometres).
Areas with fewer than 1,000 records are left out (about 1% of the records).
Each circle is placed at the record-weighted mean of its cells, rather than the centre of
the 3-degree area, which could place a circle in the sea.
"""
import csv, json, math
from pathlib import Path

STEP = 3.0  # width and height of each area in degrees
MIN_RECORDS = 1000  # minimum records needed to show an area's circle

root = Path(__file__).resolve().parent.parent
grid = json.load(open(root / "data" / "raw" / "ala_frogid_dr14760" / "ala_frogid_grid_point-0.1.json"))

areas = {}
for x in grid:
    lat, lon = (float(v) for v in x["label"].split(","))
    # Give all 0.1-degree cells in the same 3-degree area one shared key.
    # Rounding before floor avoids floating-point errors at area boundaries.
    key = (math.floor(round(lat / STEP, 6)) * STEP, math.floor(round(lon / STEP, 6)) * STEP)
    a = areas.setdefault(key, [0, 0.0, 0.0])  # records, sum(records * lat), sum(records * lon)
    a[0] += x["count"]
    # Weight each cell's centre by its records to locate the area's circle.
    a[1] += x["count"] * (lat + 0.05)  # + 0.05 = centre of the 0.1 degree cell
    a[2] += x["count"] * (lon + 0.05)

# Divide weighted position totals by the record count; omit areas below the threshold.
rows = [{"longitude": round(slon / n, 3), "latitude": round(slat / n, 3), "records": n}
        for _, (n, slat, slon) in sorted(areas.items()) if n >= MIN_RECORDS]

dest = root / "data" / "frogid_records_by_area.csv"
with open(dest, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(len(rows), "circles; records shown", sum(r["records"] for r in rows), "of", sum(a[0] for a in areas.values()))
