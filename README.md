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
| `coverage.perfect_capita` | The Perfect Capita card: the yearly cost per person, for example "$6,204" ("To set" until it is costed with the nation) |
| `coverage.price`, `coverage.price_note` | Optional. The price of Perfect [Nation]: Perfect Capita times population, for example "$1.75bn", and one sentence on how it was set (page v11.8 and later) |
| `guarantees` | The seven basic living standards. The field keeps its name so older pages still read it. Exactly seven, in this order: Food, Water, Shelter, Energy, Education, Health, Livelihoods (the name stays "Livelihoods"; pages show "Livelihood"). `value` is 0 to 100 and fills the wheel; `display`, `note`, `source` and `url` fill the tiles. The lowest value is marked as the standard that sets Coverage. |
| `dispatches` | The Dispatches under the Letter, newest first, at most three shown. Each has `no`, `date` (YYYY-MM-DD), `label` (for example "2 Nov 2026"), `author` (`preeti`, or `nia` on Barbados and `steward` on every other nation), `title` and `summary`. Either a `url` to a published post, or `body` (a list of paragraphs) and `sources` (a list of `label` and `url`), which the page opens in place. |
| `newswire` | The Barbados Newswire, newest first, at most eight items. `highlight` is an optional part of the title shown in gold. Every `url` must start with https://. |

Every nation file except Barbados also carries `checked`: the date and time (YYYY-MM-DDTHH:MMZ, UTC) the Nation Stewards rotation last checked it. The rotation uses it to choose which nations to check next; it does not show on the page.

## Words we use (Steward-General, 1 November 2026)

- **The seven basic living standards**, in running text "the seven standards": food, water, shelter, energy, education, health and livelihood.
- **Perfect Capita**: the yearly cost, per person, of lifting everyone above the Living Line in all seven basic living standards.
- **The price of Perfect [Nation]**: Perfect Capita times population, the national bill ("The price of Perfect Barbados: $1.75 billion a year"). It is also the denominator of the Perfect Nations Ratio.
- **Coverage** shows how close a nation is, out of 100, set by its weakest standard. **The Gap** counts who is still below.
- **The Living Line** names the threshold only: "The poverty line measures income. The Living Line measures a life: food, water, shelter, energy, education, health and livelihood." Use it on the Perfect Capita page and in Coverage explanations (for example a `gap_text`); keep it out of headlines and most dispatches.
- Never "Human Guarantees". "Guarantee" is a verb only in the mission line ("Every nation can guarantee seven basic living standards to every citizen."), because on the wire a guarantee is a financial instrument.
- Field names in these files (`guarantees`, `Livelihoods`) are unchanged, so nothing breaks.

Rules: every figure must have a primary source; no contractions; plain ASCII where possible. A file that breaks these rules (wrong nation, not seven standards, a value outside 0 to 100) is ignored by the page, which then keeps its pasted version.

## Who may publish a dispatch

- `author: "nia"`: written by Nia Carrington, Nation Steward of Barbados, audited, and committed straight to main.
- `author: "steward"`: written by the Nation Steward of that nation (for example Wanjiru Mwangi for Kenya), audited, and committed straight to main.
- `author: "preeti"`: signed by Preeti Sinha, President and CEO. Proposed only as a pull request; it goes live when she merges it. Never committed to main directly.

## Pages (the code of each page)

`pages/` holds the full code of each page that is served live, and `pages/manifest.json` lists them by the id of their root element (for example `pn-bp-barbados`). The **Perfect Nations Live Pages** WordPress plugin reads the manifest and serves each file in place of the Custom HTML widget pasted in Elementor, so a page changes without copying and pasting. The plugin keeps each file for ten minutes and keeps the last good copy if GitHub cannot be reached; with nothing fetched, the pasted code shows.

- Merging into main publishes a page within about ten minutes (or at once with Settings > Perfect Nations Live > Refresh now).
- Every change to `pages/` goes through a pull request titled "For approval: [page] vX.Y, [what changed]"; the Steward-General approves by merging. Stewards never commit to `pages/` on main.
- Each file must keep its root id, stay plain ASCII, keep its CSS scoped to its root id, and pass `node --check` on every script block.
- To add a page: put its file in `pages/`, add its root id to the manifest, and paste the same code once into the page's Custom HTML widget (the paste is the fallback).

## Nations

Each live blueprint reads its own file: `data/<nation>.json` (barbados, kenya, ...). A Steward edits only the file for its own nation.

- Barbados is kept by its own daily run (Nia Carrington, 7:36 am New York).
- Every other nation file is kept by the Nation Stewards rotation, which runs three times a day and checks the five nations checked longest ago. A new nation file joins the rotation automatically. The seven standards are checked once a month per nation; the Newswire at every visit.
- The Correspondent (8 am, 12 noon and 8 pm) also adds every instrument it verifies for a nation to that nation's `newswire`, and sets that file's `updated`. It never edits `barbados.json` (Nia keeps the Barbados Newswire) and changes nothing else in a nation file.
- Dispatches share one numbered series across every file in `data/` and every open pull request.

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
