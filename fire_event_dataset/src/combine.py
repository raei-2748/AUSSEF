"""One workbook for the mentor: key declared events first, then the full fire dataset.

Reads out/nsw_key_bushfire_events.xlsx and out/nsw_fire_events_2015_2025.xlsx (build those first) and writes
out/nsw_bushfires_2015_2025_combined.xlsx. URL columns are made clickable.
Run: uv run --no-sync --with openpyxl python -m src.combine
"""
import pandas as pd

from src.common import OUT

KEY = OUT / "nsw_key_bushfire_events.xlsx"
FULL = OUT / "nsw_fire_events_2015_2025.xlsx"
DEST = OUT / "nsw_bushfires_2015_2025_combined.xlsx"

# (new sheet name, source workbook, sheet, what it is)
SHEETS = [
    ("key_events", KEY, "events", "125 declared NSW bushfire disasters: summary, key facts, sources"),
    ("key_event_council", KEY, "event_council", "Each declared event × council: fire features, council context, Y columns"),
    ("key_facts", KEY, "facts", "Every reported fact with source, date, verbatim quote and link check"),
    ("key_dictionary", KEY, "dictionary", "Column meanings for the three key_ sheets"),
    ("key_sources", KEY, "sources", "Every document behind the key_ sheets"),
    ("all_fires", FULL, "fires", "All NSW bushfires 2015–2025, one row per fire × council, Bowen's template columns first"),
    ("lga_year", FULL, "lga_year", "Council × year economy and finance panel, 2014–2025"),
    ("all_fires_dictionary", FULL, "dictionary", "Column meanings, units, sources and coverage for all_fires"),
    ("lga_year_dictionary", FULL, "lga_year_dictionary", "Column sources for lga_year"),
    ("download_links", FULL, "download_links", "Exact download link for every input dataset"),
    ("data_sources", FULL, "sources", "Every input file: local path, SHA-256, access time, licence"),
]
URL_COLS = {"source_url", "declaration_source_url", "download_url", "url", "source", "house_loss_url"}


def main():
    guide = pd.DataFrame(
        [(n, w) for n, _, _, w in SHEETS],
        columns=["sheet", "what it holds"])
    notes = pd.DataFrame({"sheet": ["", "Notes"], "what it holds": ["", ""]})
    rules = pd.DataFrame({"sheet": ["", "", "", "", ""], "what it holds": [
        "Blank means no data; 0 means the source was checked and the value is zero.",
        "Y, Y_class, DL, IL, FP, SL and split are left blank on purpose, to be designed in class.",
        "Every number traces to a source (see the dictionaries, key_sources, download_links); links were checked.",
        "Facts: a value is kept only if the number appears in its quote; hedged figures ('more than 700 ha') are blanked.",
        "_excess columns = change in the council minus the median change in councils without a fire of 100 ha or more.",
    ]})
    guide = pd.concat([guide, notes, rules], ignore_index=True)
    with pd.ExcelWriter(DEST, engine="openpyxl") as w:
        guide.to_excel(w, sheet_name="README", index=False)
        for name, book, sheet, _ in SHEETS:
            d = pd.read_excel(book, sheet_name=sheet)
            d.to_excel(w, sheet_name=name, index=False)
            ws = w.sheets[name]
            for j, col in enumerate(d.columns, start=1):
                if col not in URL_COLS:
                    continue
                for i, u in enumerate(d[col], start=2):
                    if isinstance(u, str) and u.startswith("http") and "{" not in u and " " not in u:
                        ws.cell(row=i, column=j).hyperlink = u
                        ws.cell(row=i, column=j).style = "Hyperlink"
        w.sheets["README"].column_dimensions["A"].width = 24
        w.sheets["README"].column_dimensions["B"].width = 110
    return DEST


if __name__ == "__main__":
    print(main())
