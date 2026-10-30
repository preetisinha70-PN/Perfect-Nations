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
| `dispatches` | The Dispatches under the Letter, newest first, at most three shown. Each has `no`, `date` (YYYY-MM-DD), `label` (for example "2 Nov 2026"), `author` (`preeti`, or `nia` on Barbados and `steward` on every other nation), `title` and `summary`. Either a `url` to a published post, or `body` (a list of paragraphs) and `sources` (a list of `label` and `url`), which the page opens in place. |
| `newswire` | The Barbados Newswire, newest first, at most eight items. `highlight` is an optional part of the title shown in gold. Every `url` must start with https://. |

Rules: every figure must have a primary source; no contractions; plain ASCII where possible. A file that breaks these rules (wrong nation, not seven guarantees, a value outside 0 to 100) is ignored by the page, which then keeps its pasted version.

## Who may publish a dispatch

- `author: "nia"`: written by Nia Carrington, Nation Steward of Barbados, audited, and committed straight to main.
- `author: "steward"`: written by the Nation Steward of that nation (for example Wanjiru Mwangi for Kenya), audited, and committed straight to main.
- `author: "preeti"`: signed by Preeti Sinha, President and CEO. Proposed only as a pull request; it goes live when she merges it. Never committed to main directly.

## Nations

Each live blueprint reads its own file: `data/<nation>.json` (barbados, kenya, ...). A Steward edits only the file for its own nation.
