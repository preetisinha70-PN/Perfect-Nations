# Perfect Nations: live data

This repository holds the live data that the Perfect Nations blueprints on perfectnations.org read each time a visitor opens a page.

- `data/barbados.json`: the Barbados blueprint. Kept current every morning by Nia Carrington, Nation Steward of Barbados.
- `data/state-of-nations.json`: the State of Nations page (the wire of instruments and the dispatches). Kept current at 8 am, 12 noon and 8 pm New York time by the Correspondent, Steward of the Wire.

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

## The State of Nations file

Read on every visit by https://perfectnations.org/state-of-nations/ (page v6.1 and later). Kept by the Correspondent, Steward of the Wire. If the file is missing or malformed, the page shows the copy built into it.

Outline (the comments are notes, not part of the file):

```
{
 "page": "state-of-nations",          // must be exactly this
 "updated": "YYYY-MM-DD",
 "wire": [ ... ],                     // newest first
 "dispatches": [ ... ]                // newest first
}
```

**Wire entry**

| field | rule |
|---|---|
| `date` | YYYY-MM-DD, the date on the article page |
| `source` | publication, as on the source chip after "Via" (for example "Artemis", "Government of Slovenia") |
| `type` | instrument type in sentence case, reusing an existing one where it fits ("Eurobond", "Catastrophe bond") |
| `title` | headline exactly as published, plain text with curly apostrophes, no HTML |
| `url` | canonical https URL, nothing after a `?` |
| `by` | list of writers; empty list for a press release |
| `agency` | wire agency when the story is carried by another outlet (for example "Reuters"), else "" |
| `where` | label shown on the item: the nation, or the region for a regional item ("West Africa") |
| `nations` | list of nations counted on the page; empty for a regional item |
| `region` | one of: Africa, Americas, Asia-Pacific, Europe, Middle East |

**Dispatch entry**

| field | rule |
|---|---|
| `no` | dispatch number, unique; the next is the highest number plus one |
| `slug`, `title`, `kicker`, `date`, `standfirst` | as on the card ("Liability management · Addis Ababa") |
| `figure`, `caption` | the lead figure on the card and its caption |
| `url` | the WordPress post, when the dispatch is published as a post |
| `body` | the full text as a list of paragraphs; a line starting "## " is a section heading. With a body and no url, the dispatch opens in a reader on the page (link: /state-of-nations/#dispatch-NN) |
| `figures` | up to four [value, caption] pairs for the reader |
| `kick` | the closing line |
| `sources` | list of {"label", "url"}, every url https |

A dispatch with neither `url` nor `body` shows "In press". Wire items are committed straight to main. A new dispatch is proposed only as a pull request titled "For approval: Dispatch No. NN" and goes live when Preeti Sinha, President and CEO, merges it.
