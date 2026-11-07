# Perfect Nations: live data

This repository holds the live data that the Perfect Nations blueprints on perfectnations.org read each time a visitor opens a page.

- `data/<nation>.json`: each nation blueprint (barbados, kenya, ...). Kept current by its Nation Steward in the Nations Newswire Stewards rotation; Barbados (Nia Carrington) at least once a day.
- `data/state-of-nations.json`: the State of Nations page (the wire of instruments and the dispatches). Kept current at 8 am and 8 pm New York time by the Correspondent, Steward of the Wire.
- `archive/`: older Newswire items and dispatches, moved out of the nation files and never deleted (see The archive).
- `figures/perfect-capita.json`: the live figures on the Perfect Capita page (perfectnations.org/perfect-capita/). Kept by the Perfect Capita Steward (see The Perfect Capita page). It is not a nation file, which is why it sits outside `data/`.

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
| `newswire` | The Barbados Newswire, newest first. The file keeps the newest eight, which the page shows; older items move to `archive/newswire/barbados.json` and open under All news. `highlight` is an optional part of the title shown in gold. Every `url` must start with https://. |

Every nation file, Barbados included since 6 November 2026, carries `checked`: the date and time (YYYY-MM-DDTHH:MMZ, UTC) the rotation last checked it. The rotation uses it to choose which nations to check next; it does not show on the page.

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
- Check any page file with `python3 tools/check_page.py pages/<file>.html` (ASCII, CSS, scripts, tags, ids, copy).

## The Blueprints page (from 6 November 2026)

perfectnations.org/blueprints/ is one file, `pages/blueprints.html` (root `pn-blueprints`), kept by the Blueprints Steward.

- **Built, never edited by hand.** `python3 tools/build_blueprints.py` joins `pages/nations-menu.html`, `pages/home-seams.html` and `pages/blueprints-atlas.html` (the page itself: style, markup and script). It draws the golden map from the world outlines in `pages/home-hero.html`, so the homepage planet and the map share one source.
- **A new blueprint needs no new build.** On every visit the page reads `pages/manifest.json`: a blueprint merged there (its `pn-bp-<slug>` key) turns gold on the map, joins the tiles, the counts, the region tabs and the atlas at once. If it is not yet in `data/blueprints.json`, the page reads `data/<slug>.json` for its tile.
- **`data/blueprints.json`** is the live index of open blueprints: for each, `slug`, `name`, `region`, `url`, `steward` (from `steward.name`) and `figure` (the first sourced monetary figure of the hero, else its first figure: `value`, `label`, `money`). It mirrors the nation files and adds no fact of its own. Rebuild it with `python3 tools/build_blueprints.py --index`; it is data, so it may go straight to main.
- **Page changes** (design, words, a rebuilt fallback) go through a pull request "For approval: Blueprints page vX.Y, ...", with the `pn-blueprints` version raised in the manifest.

## The Art of Nations page (from 7 November 2026)

perfectnations.org/perfect-nations-gallery/ (page 16839) is one file, `pages/art-of-nations.html` (root `pn-art`), kept by the Art of Nations Steward. Its Elementor widget already contains `pn-art`, so the plugin serves the file in its place; nothing is pasted. The old two-part widget (v3.0, roots `pn-art` and `pn-gal`) is archived at `archive/elementor/gallery-16839-before-one-file-2026-11-07.json`.

- **Built, never edited by hand.** `python3 tools/build_art.py` reads `art/catalogue.json` (the paintings and books: words, nation colours, images, enquiry links) and `art/art-of-nations.template.html` (style, markup, script) and writes the page. The build refuses straight apostrophes, contractions, image URLs outside the Media Library, copies wider than 768 px in `images`, and any non-ASCII character.
- **A new painting** is one new entry in `paintings` (newest last): the hero, the wall, the count ("5 of 195 nations painted"), the 195 dots and the viewer all follow.
- **Images** are the copies WordPress makes (300, 600 and 768 px under `images`; `zoom` is the copy the viewer opens). Check each one exists in the Media Library first.
- **Ready for a shop.** Put the store address in `shop` and a `buy_url` (and `price`, if wanted) on a work: it shows Buy beside Enquire. Without a `buy_url` a work stays by enquiry.
- **Checks and previews:** `python3 tools/check_page.py pages/art-of-nations.html art/art-of-nations.template.html`, then `python3 tools/preview_art.py` (laptop 1440 x 900, phone 390 x 844; screenshots in /tmp/pn-preview).
- **Every change** goes through a pull request "For approval: Art of Nations vX.Y, ...", with `pn-art` raised in the manifest.

## Nations

Each live blueprint reads its own file: `data/<nation>.json` (barbados, kenya, ...). A Steward edits only the file for its own nation.

- Each nation has its own Nation Steward (named in `steward.name`), which reviews its whole blueprint once a week in the Nation Stewards rotation: the hero figures, the register, the record in figures, the Sovereign Assets, the enterprises, the seven standards and the Dispatches. Everything it changes is in the data file and is published automatically after the Auditor; changes to the design or the page code still go through a pull request.
- The Nations Newswire Stewards rotation runs three times a day and keeps every nation's Newswire current, the five nations checked longest ago at each run, with Barbados at least once a day. It also writes the landmark dispatches. A new nation file joins both rotations automatically.
- `checked` records the last Newswire check and `reviewed` the last weekly review (both YYYY-MM-DDTHH:MMZ, UTC). When the Newswire Stewards report a landmark instrument for a nation, they set its `reviewed` to "" so that its Nation Steward reviews the whole page at the next run.
- `stewards/<nation>.md`: each Nation Steward's notes, public like the rest of this repository: the primary source of every figure on the page that has no link of its own (the hero and asset figures), the watch items and the open gaps.
- No limit on the number of Newswire items or dispatches (Steward-General, 6 November 2026). A Newswire item names an instrument, approval, debt operation or investment, with an issuer and terms, verified on the article page, one item per announcement. A dispatch is written only for a landmark: an instrument approved, priced, signed or closed, or a watched item resolved.
- The Correspondent (8 am and 8 pm) also adds every instrument it verifies for a nation to that nation's `newswire`, and sets that file's `updated`. It never edits `barbados.json` and changes nothing else in a nation file.
- Dispatches share one numbered series across every file in `data/` and `archive/` and every open pull request.

## The whole blueprint page (from 6 November 2026)

Every nation file also drives the rest of its page. Each part is optional: when it is missing or malformed, the page shows its own code instead. Every `url` is https (an enterprise may also use `mailto:`), and URLs may not contain quotes, brackets or spaces. `money: true` shows the value in gold; use it only for sourced monetary values.

| Field | What it drives on the page |
|---|---|
| `hero.lead` | The sentence under the nation's name |
| `hero.stats` | The three figures in the hero: `value` and `label`. A stat labelled "Instruments and investments on record" always shows the number of register lines |
| `capital.heading` | The heading of the Capital Architecture section |
| `capital.record` | The record in figures: `value`, `money`, `text`, `source` (the link text, for example "IMF, 2024") and `url` |
| `capital.register` | The register, in the order shown; the page shows the first eight and a Show all button for the rest, and builds the filters and counts. Each line: `cat` (govt, humanitarian, multi, regional, bilat, private or impact), `status` (the label shown, for example "Active", "Approved", "Pipeline"), `tone` (the badge style: active, completed, pipeline, advocacy, annual, appeal or granted), `name`, `detail` (the small line under the name), `amount`, `money`, `note`, `text`, `by` (a list of the institutions) and `url` (the primary source) |
| `assets.heading`, `assets.items` | The Sovereign Assets cards: `name`, `figure`, `money`, `label` (the small line under the figure), `text`, `alt` (a description of the picture), `images` (one or more https picture URLs, the first that loads is shown) and `tint` (two colours, for example ["#E07A3A", "#6A2410"], behind the picture) |
| `enterprises.heading`, `enterprises.items` | The enterprise cards: `standard` (one of the seven, or "In preparation"), `name`, `text`, `source` (the link text) and `url` |

## The archive

Nothing published is deleted. When a list grows past what its page shows, the oldest entries move, unchanged, to the top of an archive file (a JSON list, newest first), created when first needed:

- `archive/newswire/<nation>.json`: Newswire items beyond the newest eight. Each blueprint (from 6 November 2026) reads it when its Newswire is full and shows an All news button that opens the full list in place.
- `archive/dispatches/<nation>.json`: dispatches beyond the newest six. Their numbers still count in the shared series.

Entries keep the fields they had in the nation file. A URL already in a nation file or its archive is never added again.

## The Sovereign Assets file (from 6 November 2026)

`data/sovereign-assets.json` drives the Sovereign Assets page (perfectnations.org/sovereign-assets/, root id `pn-sov`, page v6.0 and later). Kept by the Sovereign Assets Steward (skill `steward-sovereign-assets`).

| Field | What it drives on the page |
|---|---|
| `ledger` | The three figures in the hero (assets recorded, nations, asset classes) and the count in the full ledger. Counted by `python3 tools/build_sovereign_assets.py --data` from every nation file's `assets.items`; never edited by hand |
| `nations` | The golden planet (one gold light per recorded asset, placed at `lat`, `lon`) and the list of nations, each linking to its blueprint. Counted with the ledger |
| `updated` | "Ledger updated D Month YYYY" in the hero; set by the build whenever the ledger changes |
| `featured` | The five assets, in order. Each: `cls` (one of the eight classes), `figure`, `unit`, `line` (the words under the figure), `name`, `nation`, `flags` (two-letter codes), `text`, `source` (the link text), `url` (the source), `link` (the blueprint), `image` (1536 px copy) and `image_small` (768 px copy) from the Media Library, and `alt` |

The page itself is built, never edited by hand: `pages/sovereign-assets-src.html` (the design) and this file make `pages/sovereign-assets.html` through `python3 tools/build_sovereign_assets.py`, which also runs the validation suite. The page reads this file on every visit, so a new nation file or a refreshed figure shows without a pull request; a change to the design goes through a pull request. If the file is missing or malformed, the page shows the figures built into it. Previews: `python3 tools/preview_sovereign_assets.py --all`.

## The Capital Wire file (homepage ticker)

`data/ticker.json` drives the Capital Wire, the moving deal tape under the homepage hero (Section 01b v2.0 and later, root id `pn-tick`). It is a short extract of the wire, about 5 KB, so the homepage never downloads the full State of Nations file. Kept by the Correspondent: rebuilt on every run that changes the wire, and on the first run of each day so items older than 14 days leave the tape. If the file is missing or malformed, the tape shows the deals built into the widget.

```
{
 "page": "ticker",                      // must be exactly this
 "updated": "YYYY-MM-DD",               // the run that last changed the wire
 "edition": "8 am",                     // "8 am" or "8 pm" (New York)
 "count": { "deals": 64, "nations": 44 },  // wire entries in state-of-nations.json; distinct names in their nations lists
 "items": [ ... ]                       // 8 to 12, in the order shown
}
```

**Item**

| field | rule |
|---|---|
| `date`, `type`, `title`, `source`, `url` | copied unchanged from the item's entry in `data/state-of-nations.json`; the url must be on the wire |
| `nation` | the label shown, from the wire entry's `where` |
| `slug` | the nation's slug on the homepage planet (lowercase, hyphens, no "The": `bahamas`, `cote-divoire`, `dr-congo`, `united-states`); "" for a regional item. A slug the planet does not know simply hides "Find on the planet" |
| `figure` | the headline amount as the source states it, compact: `US$5.2bn`, `EUR 4.5bn`, `US$175m`, `FCFA 143bn`, `MAD 1bn`. Never converted, never estimated; an item without a sourced amount does not go on the tape |
| `line` | what it is, 2 to 7 words, sentence case, no figure, no contractions ("External bond", "IDB guarantee turns debt savings into health") |
| `signal` | one of `Record`, `First`, `Oversubscribed`, `Innovative`, or "" (see below) |

**Signals**: `Record` only when the source calls it a record (largest, lowest cost, record demand); `First` only when the source calls it a first (first issue, first in a currency, first of its kind); `Oversubscribed` only when the source reports demand or proceeds above the amount offered or targeted; `Innovative` for debt swaps, guarantees and credit enhancement, catastrophe bonds and parametric cover, forest and nature funds, results-based and outcome finance, carbon and Article 6, and tokenisation.

**Order**: wire items from the last 14 days (30 if fewer than eight qualify): first those with a signal, in the order Record, First, Oversubscribed, Innovative; then the rest, largest amount first (rank by the US dollar size the source gives or implies; the figure shown stays in the source's currency); newest first on ties. At most 12.

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

## The Perfect Capita page

The page is one file, `pages/perfect-capita.html` (root `pn-pcap`), served by the Live Pages plugin. It is kept by the **Perfect Capita Steward**, which owns the page and nothing else.

- **Page code** goes through a pull request. Edit `src/perfect-capita.html`, never the built file, then run `python3 tools/build_perfect_capita.py`: it adds the painted seams (shared with the homepage, `pages/home-seams.html`), writes `pages/perfect-capita.html` and runs the validation suite (`tools/check_page.py`). Raise the version in the source banner and in `pages/manifest.json`, render previews with `python3 tools/preview_page.py pages/perfect-capita.html`, and open "For approval: Perfect Capita vX.Y, [what changed]".
- **Figures** live in `figures/perfect-capita.json`. The page reads it on every visit (raw.githubusercontent.com, then jsDelivr) and fills every element marked `data-pc="path"` with the text at that path, and every `data-pc-href` link with an https url. After the Auditor the Steward commits this file straight to main, like a nation file. If the file is unreadable, is for another page, or breaks the rules below, the page keeps the figures written into it.

| Field | What it drives on the page |
|---|---|
| `page` | Must be `"perfect-capita"` |
| `updated`, `checked` | The last change (YYYY-MM-DD) and the last check (YYYY-MM-DDTHH:MMZ, UTC); not shown |
| `world` | The world today: exactly seven, in the order Food, Water, Shelter, Energy, Education, Health, Livelihood. Each: `standard`, `value` (for example "2.1"), `unit` ("bn", "m", " in 10"), `text` (one line, starting with the people it counts), `source` (the link text: publisher, year, and the data year) and `url` (the primary source) |
| `nations` | It has been done: exactly five, in the order Thailand, Vietnam, Singapore, Brazil, Rwanda (to change a nation, change the page by pull request). Each: `nation`, `standard`, `figure`, `what`, `source`, `url` |
| `first` | The first nation priced (Barbados), copied from `data/barbados.json` `coverage` and the Measurer's floor: `perfect_capita`, `price`, `coverage`, `set_by`, `gap` and `lead` (two sentences). Never changed here before the Measurer changes them |

Every text is plain, without contractions, under 400 characters; every url https with no quotes, brackets or spaces. The seven world figures overlap and are never added together.
