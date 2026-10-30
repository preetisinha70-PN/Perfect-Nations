# Perfect Nations: live data

This repository holds the live data that the Perfect Nations blueprints on perfectnations.org read each time a visitor opens a page.

- `data/barbados.json`: the Barbados blueprint. Kept current every morning by Nia Carrington, Nation Steward of Barbados.

Each page reads its file from
`https://raw.githubusercontent.com/preetisinha70-PN/perfect-nations/main/data/<nation>.json`
and, if that fails, from the jsDelivr mirror. If neither can be read, the page shows the version last pasted into WordPress.

## The Barbados file

| Field | What it drives on the page |
|---|---|
| `updated` | The Nation Steward card: "Last updated D Month YYYY" (YYYY-MM-DD) |
| `coverage.score` | The centre of the wheel, the heading and the first of the three numbers |
| `coverage.gap`, `coverage.gap_text` | The Gap card |
| `coverage.perfect_capita` | The Perfect Capita card ("To set" until it is costed with Barbados) |
| `guarantees` | Exactly seven, in this order: Food, Water, Shelter, Energy, Education, Health, Livelihoods. `value` is 0 to 100 and fills the wheel; `display`, `note`, `source` and `url` fill the tiles. The lowest value is marked as the guarantee that sets Coverage. |
| `newswire` | The Barbados Newswire, newest first, at most eight items. `highlight` is an optional part of the title shown in gold. Every `url` must start with https://. |

Rules: every figure must have a primary source; no contractions; plain ASCII where possible. A file that breaks these rules (wrong nation, not seven guarantees, a value outside 0 to 100) is ignored by the page, which then keeps its pasted version.
