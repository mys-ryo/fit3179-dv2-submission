"""Small data files for the simple charts. Every number comes from the files in data/raw/.

  data/frogid_records_by_year.csv        FrogID records per year (ALA, dr14760) + whether the year is complete
  data/frogid_records_by_month_state.csv    FrogID records per month and state, and the share of the state's records
  data/tsx_frog_index.csv        Threatened Frog Index 2025 (TSX, CC BY 4.0) with the index as a percentage
  data/dcceew_status_waffle.csv         one row per EPBC-listed amphibian taxon (53) with a grid position and a legend label that includes the count
  data/ala_threatened_species_records.csv  threatened frogs with the most records in ALA (with a `zero` column for the lollipop stick)
  data/frogid_species_rank.csv   the 10 most recorded FrogID species: records per year (2018-2023) and share of that year's records
  data/frogid_state_share.csv    each state's share of all FrogID records in 2018 and 2023 (slope chart)
  data/frogid_state_share_labels.csv  labels for the slope chart, spread out so that they do not overlap
  data/frogid_species_by_month.csv  records per month for the 4 most recorded species (streamgraph)
  data/frogid_calling_seasons.csv    months in which each of the 10 most recorded species calls more than expected (Gantt-style chart)
  data/dcceew_status_by_state.csv  one row per state and status (long format, with status_rank), for the stacked bar
"""
import csv, json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
raw = root / "data" / "raw"   # one folder per provider (see data/raw/README_sources.md)
out = root / "data"


def write(name, rows):
    with open(out / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(name, len(rows), "rows")


# 1) records per year. FrogID started on 10 Nov 2017 and the 7.0 dataset ends on 9 Nov 2024,
#    so 2017 and 2024 are partial years.
years = {int(x["label"]): x["count"] for x in json.load(open(raw / "ala_frogid_dr14760" / "ala_facet_year.json"))[0]["fieldResult"]}
write("frogid_records_by_year.csv", [{"year": y, "records": n, "complete_year": "no" if y in (2017, 2024) else "yes"}
                              for y, n in sorted(years.items())])

# 2) month x state
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
ms = json.load(open(raw / "derived_from_ala_by_agent" / "frogid_month_by_state.json"))
rows = []
for state, by_month in ms.items():
    # Each percentage uses this state's total across all months, so states of different sizes can be compared.
    total = sum(by_month.values())
    for i, m in enumerate(months, 1):
        rows.append({"state": state, "month": m, "month_number": i, "records": by_month[m],
                     "share_of_state_pct": round(100 * by_month[m] / total, 1)})
write("frogid_records_by_month_state.csv", rows)

# 3) Threatened Frog Index (1985 = 1.0)
# Express the index relative to its 1985 baseline: 1.0 becomes 100%.
with open(raw / "tsx_threatened_frog_index" / "tsx-frog-trend-2025.csv") as f:
    rows = [{"year": int(r["year"]), "index_pct": round(100 * float(r["value"]), 1),
             "low_pct": round(100 * float(r["low"]), 1), "high_pct": round(100 * float(r["high"]), 1)}
            for r in csv.DictReader(f)]
write("tsx_frog_index.csv", rows)

# 4) waffle: one square per listed taxon, ordered by how serious the status is
with open(raw / "dcceew_threatened_species_lists" / "dcceew_species_20260828.csv", encoding="utf-8-sig") as f:
    listed_types = [r for r in csv.DictReader(f) if r["Class"] == "Amphibia"]
order = ["Critically Endangered", "Endangered", "Vulnerable", "Extinct"]
listed_types.sort(key=lambda r: (order.index(r["Threatened status"]), r["Scientific Name"]))
COLS = 10
counts = {s: sum(1 for r in listed_types if r["Threatened status"] == s) for s in order}
# One CSV row becomes one square; column and row place it in a 10-column grid.
write("dcceew_status_waffle.csv", [{"scientific_name": r["Scientific Name"], "status": r["Threatened status"],
                             "status_label": f'{r["Threatened status"]} ({counts[r["Threatened status"]]})',
                             "column": i % COLS, "row": i // COLS} for i, r in enumerate(listed_types)])

# 5) threatened frogs with the most ALA records (all datasets, not only FrogID).
#    ALA counts are per species, so the Litoria verreauxii subspecies (alpina) is left out:
#    the species total also contains the common, non-listed subspecies.
ala = {x["label"]: x["count"] for x in json.load(open(raw / "ala_amphibia_all_contributors" / "ala_amphibia_species_all.json"))[0]["fieldResult"]}
best = {}
for r in listed_types:
    sp = (r["Genus"] + " " + r["Species"]).strip()
    if r["Threatened status"] == "Extinct" or sp == "Litoria verreauxii" or sp not in ala:
        continue
    common = r["Common Name"].split(",")[0].strip()
    best[sp] = {"common_name": common, "scientific_name": sp, "status": r["Threatened status"], "records": ala[sp]}
top = sorted(best.values(), key=lambda r: -r["records"])[:10]
for r in top:
    r["zero"] = 0
write("ala_threatened_species_records.csv", top)
for r in top: print("  ", r)

# 6) stacked bar (#04): number of listed frog types in each state, by status (DCCEEW). Long format, so Vega-Lite needs no fold
#    transform. status_rank is the stacking order. A frog type that lives in several states is counted in each of them.
status_order = ["Critically Endangered", "Endangered", "Vulnerable", "Extinct"]
state_columns = {"New South Wales": "NSW", "Queensland": "QLD", "Victoria": "VIC", "Australian Capital Territory": "ACT",
                 "Western Australia": "WA", "Tasmania": "TAS", "South Australia": "SA", "Northern Territory": "NT"}
rows = []
for state, col in state_columns.items():
    for i, s in enumerate(status_order):
        n = sum(1 for r in listed_types if r[col].strip() == "Yes" and r["Threatened status"] == s)
        rows.append({"name": state, "status": s, "types": n, "status_rank": i})
write("dcceew_status_by_state.csv", rows)

# 7) bump chart (#13): the 10 species with the most FrogID records in 2018-2023. Only complete years are used
#    (2017 and 2024 are partial). Common names come from ALA (raw/derived_from_ala_by_agent/frogid_top10_common_names.json).
by_year = json.load(open(raw / "derived_from_ala_by_agent" / "frogid_species_by_year_2018_2023.json"))
common = json.load(open(raw / "derived_from_ala_by_agent" / "frogid_top10_common_names.json"))
totals = {}
for y, d in by_year.items():
    for sp_, n in d.items():
        totals[sp_] = totals.get(sp_, 0) + n
top10 = [k for k, _ in sorted(totals.items(), key=lambda x: -x[1])[:10]]
rows = []
for y in sorted(by_year, key=int):
    all_year = sum(by_year[y].values())
    for sp_ in top10:
        n = by_year[y].get(sp_, 0)
        name = common[sp_][0]
        group = ("Always ranked 1st" if name == "Common Eastern Froglet"
                 else "Last until 2022, 6th in 2023" if name == "Verreaux's Frog" else "Other eight species")
        rows.append({"year": int(y), "species": name, "scientific_name": sp_, "records": n,
                     "share_pct": round(100 * n / all_year, 1), "group": group})
write("frogid_species_rank.csv", rows)

def slope_group(state):
    return "Largest change in share" if state in ("Victoria", "Western Australia", "Northern Territory") else "Other states"


# 8) slope chart (#09): each state's share of all FrogID records, 2018 vs 2023 (both complete years).
#    South Australia, Tasmania and the ACT each have only 1-3% of the records, so their lines lie close
#    together. The tutor advised to show them separately (not combined), so all 8 states are drawn;
#    the labels are spread apart by MIN_GAP (set combine to True to combine the three again).
SMALL = ("South Australia", "Tasmania", "Australian Capital Territory")
SMALL_NAME = "SA, TAS and ACT together"
st = json.load(open(raw / "derived_from_ala_by_agent" / "frogid_state_by_year_2018_2023.json"))


def slope_files(combine, rows_name, labels_name):
    rows, labels = [], []
    for y in ("2018", "2023"):
        counts = {}
        for state, n in st[y].items():
            key = SMALL_NAME if (combine and state in SMALL) else state
            counts[key] = counts.get(key, 0) + n
        total = sum(counts.values())
        for state, n in counts.items():
            rows.append({"state": state, "group": slope_group(state), "year": int(y), "records": n,
                         "share_pct": round(100 * n / total, 1)})
        # Keep the true percentage for the line, but move nearby text labels apart visually.
        # spread the labels: at least MIN_GAP apart (in percentage points) so that they do not overlap,
        # moving each label as little as possible (neighbours that are too close are pushed apart by half each)
        MIN_GAP = 3.3
        items = sorted(((s, 100 * n / total) for s, n in counts.items()), key=lambda x: x[1])
        pos = [v for _, v in items]
        for _ in range(500):
            for i in range(len(pos) - 1):
                gap = pos[i + 1] - pos[i]
                if gap < MIN_GAP:
                    shift = (MIN_GAP - gap) / 2
                    pos[i] -= shift; pos[i + 1] += shift
        for i, (s, v) in enumerate(items):
            labels.append({"state": s, "group": slope_group(s), "year": int(y), "label_y": round(pos[i], 2),
                           "share_pct": round(v, 1), "label": f"{s} {v:.1f}%"})
    write(rows_name, rows)
    write(labels_name, labels)


slope_files(False, "frogid_state_share.csv", "frogid_state_share_labels.csv")

# 9) streamgraph (#12): records per month for the 4 most recorded FrogID species (all years together)
by_month = json.load(open(raw / "derived_from_ala_by_agent" / "frogid_top5_species_by_month.json"))
rows = []
for sp_, months_ in list(by_month.items())[:4]:  # the four most recorded species (the file is sorted by records)
    for i, m in enumerate(months, 1):
        rows.append({"species": common[sp_][0], "month": m, "month_number": i, "records": months_.get(m, 0)})
write("frogid_species_by_month.csv", rows)

# 10) Gantt-style chart (#11): when does each species call more than expected?
#     FrogID records follow when people go outside (Nov has 22% of all records), so raw counts would give almost
#     every species the same warm-season bar. Instead each species' share of records in a month is divided by the
#     share of ALL records in that month. An index above 1 means "recorded more in this month than the
#     recording effort alone would give". A season is a run of months with an index above 1; a season that
#     wraps over the new year is split into two bars.
sp_month = json.load(open(raw / "derived_from_ala_by_agent" / "frogid_top10_species_by_month.json"))
all_month = {x["label"]: x["count"] for x in json.load(open(raw / "ala_frogid_dr14760" / "ala_facet_month.json"))[0]["fieldResult"]}
all_total = sum(all_month.values())
bars = []
for sp_, by_m in sp_month.items():
    n = sum(by_m.values())
    # Compare a species' monthly share with the same month's share of all FrogID records.
    # Above 1 means relatively more records for that species, not a count of individual frogs.
    idx = [(by_m.get(m, 0) / n) / (all_month[m] / all_total) for m in months]
    runs, start = [], None
    for i, v in enumerate(idx + [0]):
        if v > 1 and start is None:
            start = i
        if v <= 1 and start is not None:
            runs.append((start, i)); start = None
    peak = max(range(12), key=lambda i: idx[i])
    for a, b in runs:
        bars.append({"species": common[sp_][0], "start_month": a + 1, "end_month": b + 1,
                     "peak_month": peak + 1, "peak_index": round(idx[peak], 1),
                     "months": f"{months[a]}–{months[b - 1]}" if b - a > 1 else months[a]})
bars.sort(key=lambda r: ((r["peak_month"] - 4) % 12, r["species"], r["start_month"]))  # winter callers first
for r in bars: print("  ", r)
write("frogid_calling_seasons.csv", bars)
