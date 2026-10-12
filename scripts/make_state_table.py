"""Build data/ala_listed_share_by_state.csv for the choropleth map (chart 03).

For each state: how many frog species were recorded in the Atlas of Living Australia (ALA), and how many of them are on the
national threatened list. Both numbers come from the same records, so the listed species are always part of the recorded ones.

Inputs (data/raw/):
  derived_from_ala_by_agent/ala_amphibia_species_by_state.json   ALA records of Amphibia (all contributors) per state: species -> number of records
                                                                 (made from ALA facet queries; see data/raw/README_sources.md)
  dcceew_threatened_species_lists/dcceew_species_20260828.csv          DCCEEW Threatened Species State Lists (Class = Amphibia)

Output columns:
  species_recorded         frog species with enough records in the state (the denominator)
  listed_species_recorded  the ones among them that are on the national list (the numerator)
  share_pct                100 * listed_species_recorded / species_recorded; this decides the colour on the map

Note: "listed" means on the national list and recorded in the state. It is not the state's own list, and the list says nothing
about how many records a species has. The map counts species, not records (chart 06 counts records).

Rules:
  - A species counts as recorded in a state if it has at least MIN_RECORDS records there (a single record may be a mistake).
  - A species counts as listed if it is on the national list and not extinct. The list uses older scientific names for some
    frogs, so the current name and the genus + species are also matched.
  - Litoria verreauxii is not counted: only its alpine subspecies is listed, and the ALA records are for the whole species.
"""
import csv, json
from pathlib import Path

MIN_RECORDS = 5   # fewer records than this: the species does not count as recorded in the state

root = Path(__file__).resolve().parent.parent
raw = root / "data" / "raw"

# {state: {species name: number of ALA records}}
by_state = json.load(open(raw / "derived_from_ala_by_agent" / "ala_amphibia_species_by_state.json"))
# Only the amphibian rows are needed (53 of the 2,222 rows in the file).
with open(raw / "dcceew_threatened_species_lists" / "dcceew_species_20260828.csv", encoding="utf-8-sig") as f:
    rows = [r for r in csv.DictReader(f) if r["Class"] == "Amphibia"]

# Step 1: the set of listed species names. Only names that really appear in the ALA data are kept, so that a name the
# ALA does not use cannot end up in the count.
recorded_anywhere = set().union(*[set(v) for v in by_state.values()])
listed = set()
for r in rows:
    if r["Threatened status"] == "Extinct":   # extinct frogs are not recorded any more
        continue
    species = (r["Genus"] + " " + r["Species"]).strip()
    if species == "Litoria verreauxii":
        continue
    # The list gives the name in two columns (the name used when listed, and the current name). Keep the first two words of
    # each (genus + species, without a subspecies), so that they can be compared with the ALA names.
    names = {" ".join(r[k].split()[:2]) for k in ("Scientific Name", "Current Scientific Name") if r[k].strip() not in ("", "-")}
    names.add(species)
    listed |= names & recorded_anywhere

# Step 2: for each state, count the recorded species, and how many of them are listed.
out = []
for state, species_records in by_state.items():
    recorded = [s for s, n in species_records.items() if n >= MIN_RECORDS]
    listed_here = [s for s in recorded if s in listed]
    out.append({"name": state, "species_recorded": len(recorded), "listed_species_recorded": len(listed_here),
                "share_pct": round(100 * len(listed_here) / len(recorded), 1)})

dest = root / "data" / "ala_listed_share_by_state.csv"
with open(dest, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)
for r in out:
    print(r)
print("wrote", dest)
