# Perfect Nations: live data

This repository holds the live data that the Perfect Nations blueprints on perfectnations.org read each time a visitor opens a page.

- `data/<nation>.json`: each nation blueprint (barbados, kenya, ...). Kept current by its Nation Steward in the Nations Newswire Stewards rotation; Barbados (Nia Carrington) at least once a day.
- `data/state-of-nations.json`: the State of Nations page (the wire of instruments and the Solutions, called dispatches until 7 November 2026). Kept current at 8 am, 12 noon and 8 pm New York time by the Correspondent, Steward of the Wire.
- `data/solutions-by-nation.json`: Solutions for every nation on the State of Nations page, built from the nation files by `tools/build_state_of_nations.py --data` (see The State of Nations page).
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
| `dispatches` | Shown on the blueprint as Solutions (from page v10.0), newest first, together with the State of Nations Solutions about the nation (see The national blueprint pages). Each has `no`, `date` (YYYY-MM-DD), `label` (for example "2 Nov 2026"), `author` (`preeti`, or `nia` on Barbados and `steward` on every other nation), `title` and `summary`. Either a `url` to a published post, or `body` (a list of paragraphs) and `sources` (a list of `label` and `url`), which the page opens in place. |
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

- **Built, never edited by hand.** `python3 tools/build_blueprints.py` joins `pages/nations-menu.html`, `pages/home-rule.html` (the gold line) and `pages/blueprints-atlas.html` (the page itself: style, markup and script). It draws the golden map from the world outlines in `pages/home-hero.html`, so the homepage planet and the map share one source.
- **A new blueprint needs no new build.** On every visit the page reads `pages/manifest.json`: a blueprint merged there (its `pn-bp-<slug>` key) turns gold on the map, joins the tiles, the counts, the region tabs and the atlas at once. If it is not yet in `data/blueprints.json`, the page reads `data/<slug>.json` for its tile.
- **`data/blueprints.json`** is the live index of open blueprints: for each, `slug`, `name`, `region`, `url`, `steward` (from `steward.name`) and `figure` (the first sourced monetary figure of the hero, else its first figure: `value`, `label`, `money`). It mirrors the nation files and adds no fact of its own. Rebuild it with `python3 tools/build_blueprints.py --index`; it is data, so it may go straight to main.
- **Page changes** (design, words, a rebuilt fallback) go through a pull request "For approval: Blueprints page vX.Y, ...", with the `pn-blueprints` version raised in the manifest.

## The 50 States page (from 10 November 2026)

perfectnations.org/50-states/ is one file, `pages/us-states.html` (root `pn-us`): the section for the 50 states of the United States, where state blueprints will open. It is in the header (Where we work, after Blueprints of Nations), in the footer and in the header search (each state by name).

- **Built, never edited by hand.** `python3 tools/build_us_states.py` builds the page from `data/us-states.json` (the figures), `tools/us/template.html`, `tools/us/style.css` and `tools/us/script.js` (the design and words), the gold line in `pages/home-rule.html` and the cup, laurels and stars of the logo kit. The map is drawn at build time from `tools/us/states-albers-10m.json` (us-atlas 3, ISC licence: Census Bureau cartographic boundaries, Albers USA with Alaska and Hawaii inset), so the page loads no map file and no library.
- **`data/us-states.json`**: for each state `slug`, `name`, `abbr`, `fips`, `region` (Census region), `population` (Census Bureau, Vintage 2025, 1 July 2025), `gdp_musd` (BEA, current-dollar GDP 2025, millions) and `poverty` (ACS 2025 1-year, table B17001: `below`, `moe`, `universe`, `share`); the United States totals; the three sources. Rebuilt with `python3 tools/build_us_states.py --data` from the official downloads in `data/us/raw/` (see its README); it adds no figure of its own.
- **A state blueprint needs no new build of this page.** On every visit the page reads `pages/manifest.json`: a key `pn-us-<slug>` (for example `pn-us-texas`) with a perfectnations.org `url` turns that state bright gold on the map and in the list, and its card and row link to that url. The header search does the same.
- **Addresses:** `/50-states/?state=<slug>` (or `#<slug>`) opens the page with that state's card on the map. "Ask for it" goes to `/contact/?about=blueprint&country=<State>`.
- **Checks and previews:** `python3 tools/check_page.py pages/us-states.html`, then `python3 tools/preview_page.py pages/us-states.html --out <folder> --fonts <folder holding node_modules/@fontsource>`.
- **Every change** goes through a pull request "For approval: The 50 States vX.Y, ...", with `pn-us` raised in the manifest. A yearly refresh of the figures (new Census and BEA releases) is a page change: download, `--data`, build, pull request.

## The Capital Architecture page (from 7 November 2026)

perfectnations.org/capital-architecture/ is one file, `pages/capital-architecture.html` (root `pn-arch`, page 8549), kept by the Capital Architecture Steward.

- **Built, never edited by hand.** `python3 tools/build_capital.py` builds the page from `data/capital-architecture.json` (the words and figures), `tools/capital/style.css` and `tools/capital/script.js` (the design), the gold line in `pages/home-rule.html` and the laurels of the logo in `pages/home-logo-kit.html`. Previews: `python3 tools/preview_capital.py`.
- **`data/capital-architecture.json`**: `hero`; `five` (the five instruments we lead with, also read by the homepage and About: `name`, `headline`, `where`, `year`, `figure`, `label`, `source`, `url`, `nation`, `image`, `alt`); `index.families` (six families, each with `name`, `short`, `line` and `items`: `name`, `headline` (one line, at most about ten words), `how` (one sentence), `where`, `year`, `figure` (shown in gold, sourced money or a sourced result only), `label`, `source`, `url` (the primary source, https), `nation` (the slug of an open blueprint, or empty)); `record`; `close`.
- **The record is live.** `record` counts every line of `capital.register` across the open blueprints (counts, never sums) and lists each nation with its count and first register line. The build recounts it; `python3 tools/build_capital.py --record` refreshes only the record, which is data and may go straight to main. The page reads it on every visit.
- **Page changes** (an instrument added or reworded, a new landmark, design) go through a pull request "For approval: Capital Architecture vX.Y, ...", with the `pn-arch` version raised in the manifest.

## The Art of Nations page (from 7 November 2026)

perfectnations.org/art-of-nations/ (page 16839; the old address /perfect-nations-gallery/ leads to it) is one file, `pages/art-of-nations.html` (root `pn-art`), kept by the Art of Nations Steward. Its Elementor widget already contains `pn-art`, so the plugin serves the file in its place; nothing is pasted. The old two-part widget (v3.0, roots `pn-art` and `pn-gal`) is archived at `archive/elementor/gallery-16839-before-one-file-2026-11-07.json`.

- **Built, never edited by hand.** `python3 tools/build_art.py` reads `art/catalogue.json` (the paintings and books: words, nation colours, images, enquiry links) and `art/art-of-nations.template.html` (style, markup, script) and writes the page. The build refuses straight apostrophes, contractions, image URLs outside the Media Library, copies wider than 768 px in `images`, and any non-ASCII character.
- **A new painting** is one new entry in `paintings` (newest last): the hero, the wall, the count ("5 of 195 nations painted"), the 195 dots and the viewer all follow.
- **The artist.** Every work names its artist (`artist`, today Preeti Sinha on every work): on the card, in the hero caption and in the viewer.
- **Origins** (`origins`) are the artist’s founding works, shown whole before the nation portraits and not counted among the 195. The first is *Botanical Origins* by Preeti Sinha (acrylic on canvas, 12 × 16 in, 2026, not for sale), the garden painting the series grew from (Media Library 17752). A work whose `status` is "Not for sale" or "Sold" shows that status and no Enquire.
- **Images** are the copies WordPress makes (300, 600 and 768 px under `images`; `zoom` is the copy the viewer opens). Check each one exists in the Media Library first.
- **Ready for a shop.** Put the store address in `shop` and a `buy_url` (and `price`, if wanted) on a work: it shows Buy beside Enquire. Without a `buy_url` a work stays by enquiry.
- **Checks and previews:** `python3 tools/check_page.py pages/art-of-nations.html art/art-of-nations.template.html`, then `python3 tools/preview_art.py` (laptop 1440 x 900, phone 390 x 844; screenshots in /tmp/pn-preview).
- **Every change** goes through a pull request "For approval: Art of Nations vX.Y, ...", with `pn-art` raised in the manifest.

## The About page (from 7 November 2026)

perfectnations.org/about/ is one file, `pages/about.html` (root `pn-about`), kept by the About Steward.

- **Edited by hand, except the GENERATED blocks.** `python3 tools/build_about.py` refreshes them: the homepage parts with the gold line's style (`pages/home-rule.html`), the counts of Stewards, and the Nation Stewards roll, one card per open blueprint in `data/blueprints.json`, with the Steward's name from `data/<slug>.json` and the 150 px portrait the nation's own blueprint shows. Run it whenever a blueprint is added; the roll and the counts follow.
- **The bands, in order (v11.4):** the logo, "Perfect Nations is a new-age sovereign advisory firm, and its clients are nations", the Vision and the Mission (Earthrise); What we do; 01 Assets; 02 Capital; 03 Solutions; the Founder's Vision (all homepage parts); the President and CEO (ivory); the record (Lagoon); the gold line; the Council of Stewards (Earthrise); the gold line; the close, the homepage's own (`pages/home-pledge.html`): the ReDesign Studio and its three ways to begin. A change to a homepage part reaches About when `tools/build_about.py` is run.
- **Checks and previews:** `python3 tools/check_page.py pages/about.html`, then `python3 tools/preview_page.py pages/about.html --out <folder> --fonts <node_modules/@fontsource>`.
- **Every change** goes through a pull request "For approval: About vX.Y, ...", with `pn-about` raised in the manifest.

## The Contact page (from 7 November 2026)

perfectnations.org/contact/ (page 12711) is one file, `pages/contact.html` (root `pn-contact`), kept by the Contact Steward. Its Elementor Custom HTML widget (v5.1) already contains `pn-contact`, so the plugin serves the file in its place; the paste stays as the fallback.

- **Edited by hand**, except two blocks that `python3 tools/build_contact.py` writes: the gold line's style (from `pages/home-rule.html`; the line sits under the letterhead), and a JSON block with the open blueprints (from `pages/manifest.json`), the paintings and books (from `art/catalogue.json`) and, since v6.2 (10 Nov 2026), every published Solution (the "design" entries of `data/state-of-nations.json`) for "Discuss a Solution". Run the build whenever a blueprint or a Solution is published, or a painting or book is added.
- **Every button on the site lands here with its intent**: `?about=studio` or `briefing` (The Nation Briefing), `lab` (The Blueprint Lab), `commission` or `sovereign` (The Sovereign Mandate), `original-<nation>` (a painting), `perfect-<nation>-book` (a book), `solution-<number>` or `?solution=<number>` (Discuss a Solution, that Solution), `gallery`, `speaking`; `?topic=nominate-self`, `guest`, `nominate`, `story`, `enterprise`, `codesigner`; `?nation=<slug>` (an open blueprint opens "Share a vision or story", any other nation "Ask for a blueprint"); `?country=<Name>`.
- **Sending** opens the visitor's own email to contact@perfectnations.org, with Gmail, Outlook and Copy as fallbacks. Nothing is stored on the site.
- **Checks and previews:** `python3 tools/check_page.py pages/contact.html`, then `python3 tools/preview_page.py pages/contact.html --out <folder> --fonts <folder holding node_modules/@fontsource>`.
- **Every change** goes through a pull request "For approval: Contact vX.Y, ...", with `pn-contact` raised in the manifest.

## The State of Nations page (from 7 November 2026; v8.0 from 9 November 2026)

perfectnations.org/state-of-nations/ (page 15051) is one file, `pages/state-of-nations.html` (root `pn-son`), kept by the State of Nations Steward. The page's one Elementor Custom HTML widget already contains `pn-son`, so the plugin serves the file in its place.

The page is about the Solutions Perfect Nations designs: one for each open blueprint nation, to end extreme poverty and secure the seven basic standards of living, with innovative finance first and super intelligence second. Bands: the hero (Earthrise); the Solutions (ivory), with a search by nation and filters by standard; the gold line; the Deal Notes, the wire and the close (Earthrise Depth).

- **Built, never edited by hand.** Edit `src/state-of-nations.html` (style, markup, script), then run `python3 tools/build_state_of_nations.py`. It fills the slots from `data/state-of-nations.json`, `data/solutions-by-nation.json` and the gold line in `pages/home-rule.html`, and refuses any non-ASCII character. Check with `python3 tools/check_page.py pages/state-of-nations.html`; previews with `python3 tools/preview_page.py pages/state-of-nations.html`.
- **A Solution opens on the page** (link `/state-of-nations/#solution-NN`): the idea, The challenge with its source, What Perfect Nations advises, How it works (01 Assets, 02 Capital, 03 Solutions), the deal that proves it, the first move, where the nation stands on the seven standards (from `data/solutions-by-nation.json`) and the instrument already at work. A Deal Note opens at `#deal-NN`; old `#dispatch-NN` links open the Deal Note of that number.
- **The playbook** (for each of the seven standards: the instrument, the deal that proved it and what Perfect Nations advises) lives in `PLAYBOOK` in the build script and is published in `data/solutions-by-nation.json`; a blueprint shows it only for a nation without a designed Solution. Five proofs are read from `data/capital-architecture.json` by instrument id; Food and Health carry their own primary source. Changing it is a page change.
- **`data/solutions-by-nation.json`** mirrors the nation files and adds no fact: for each open blueprint, the standard furthest from reach (`coverage.set_by`), the gap and its sentence with the source of that standard, the seven standards as published on the blueprint, the instrument already at work on that standard, the nation's designed Solution (`solutions`, `design`: no, title, idea, advice, url). Rebuild it with `python3 tools/build_state_of_nations.py --data`; it is data, so it may go straight to main. The Correspondent rebuilds it after every watch.
- **It updates itself.** On every visit the page reads both files; a Solution, Deal Note or wire item merged into `data/state-of-nations.json` shows at once. If a file cannot be read, the copy built into the page shows.
- **Page changes** go through a pull request "For approval: State of Nations vX.Y, ...", with `pn-son` raised in the manifest.

## Nations

Each live blueprint reads its own file: `data/<nation>.json` (barbados, kenya, ...). A Steward edits only the file for its own nation.

- Each nation has its own Nation Steward (named in `steward.name`), which reviews its whole blueprint once a week in the Nation Stewards rotation: the hero figures, the register, the record in figures, the Sovereign Assets, the enterprises, the seven standards and the Dispatches. Everything it changes is in the data file and is published automatically after the Auditor; changes to the design or the page code still go through a pull request.
- The Nations Newswire Stewards rotation runs three times a day and keeps every nation's Newswire current, the five nations checked longest ago at each run, with Barbados at least once a day. It also writes the landmark dispatches. A new nation file joins both rotations automatically.
- `checked` records the last Newswire check and `reviewed` the last weekly review (both YYYY-MM-DDTHH:MMZ, UTC). When the Newswire Stewards report a landmark instrument for a nation, they set its `reviewed` to "" so that its Nation Steward reviews the whole page at the next run.
- `stewards/<nation>.md`: each Nation Steward's notes, public like the rest of this repository: the primary source of every figure on the page that has no link of its own (the hero and asset figures), the watch items and the open gaps.
- No limit on the number of Newswire items or dispatches (Steward-General, 6 November 2026). A Newswire item names an instrument, approval, debt operation or investment, with an issuer and terms, verified on the article page, one item per announcement. A dispatch is written only for a landmark: an instrument approved, priced, signed or closed, or a watched item resolved.
- The Correspondent (8 am and 8 pm) also adds every instrument it verifies for a nation to that nation's `newswire`, and sets that file's `updated`. It never edits `barbados.json` and changes nothing else in a nation file.
- Deal Notes (the `dispatches` in a nation file and `deals` in `data/state-of-nations.json`) share one numbered series across every file in `data/` and `archive/` and every open pull request. The Solutions Perfect Nations designs (`dispatches` in `data/state-of-nations.json`, kind "design") have their own series.

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

## The national blueprint pages (from 7 November 2026)

Every blueprint (perfectnations.org/blueprints/<nation>/, root `pn-bp-<slug>`) is built from one design, so a change is made once and reaches all 44. Page v10.0.

- **Built, never edited by hand.** `python3 tools/build_nations.py` (all open blueprints, or name some) writes `pages/blueprint-<slug>.html` from `tools/nation/style.css`, `tools/nation/script.js`, `tools/nation/globe.js`, the nation's page words in `tools/nation/<slug>.json` (the Letter, the portrait, the people of the nation, the mandate moves, how Perfect Capita is measured, the sources, the Nation Steward photo, the outline), today's `data/<slug>.json`, and, when present, `data/solutions-by-nation.json` and `data/state-of-nations.json`. `tools/nation/media.json` lists the smaller copies that exist in the Media Library for each picture (used for srcset). Add `--manifest` to raise every built `pn-bp-<slug>` in the manifest.
- **Bands:** the hero (Earthrise: the nation, three figures, the globe); the ReDesign Studio and its three mandates (ivory), straight under the hero; the Letter, Solutions and Writings (Lagoon); a gold line; the Sovereign Assets (Earthrise); Perfect Capita (ivory); Capital Architecture and the Newswire (Lagoon); a gold line; Enterprises and Voices (Earthrise); the close and the sources (Earthrise Depth). On phones the mandates, the Solutions and the assets are swipe rails; the page never scrolls sideways.
- **The globe** is drawn by the page itself (`tools/nation/globe.js`, WebGL, about 9 KB): NASA Blue Marble from the Media Library (`pn-globe-earth-day`, 1536 px on laptops, 1024 px on phones, preloaded) with the nation painted in gold from its outline. No globe.gl or three.js. It pauses off screen, survives a graphics reset, and draws a still Earth without WebGL.
- **Solutions** (the Dispatches before 7 November 2026): near the band the page reads `data/solutions-by-nation.json` (the Solution for the nation: its challenge, the deal and what Perfect Nations advises, the field `advises`; since 9 November 2026 a Solution no longer shows how FfD and SI solve it) and `data/state-of-nations.json` (every Solution whose `nation` is this nation, or whose number the nation lists), with the nation file's `dispatches` added; newest first, three on laptops with Show all.
- **Live data** as before: `data/<slug>.json` on load (hero, the seven standards, register, record, assets, enterprises, Newswire). A standard whose `value` is null shows as not scored instead of stopping the update.
- **Checks and previews:** `python3 tools/check_page.py pages/blueprint-*.html`, then `python3 tools/preview_nations.py kenya barbados --libs <folder with globe.gl and three-globe> --fonts <@fontsource folder>` (laptop and phone shots, height, where the ReDesign Studio starts, whether the globe drew, requests and bytes).
- **Every page change** goes through a pull request "For approval: 44 blueprints vX.Y, ...". The Nation Stewards keep changing only `data/<slug>.json`.
- **A new blueprint:** write `tools/nation/<slug>.json` (copy one and change every line), check its pictures in the Media Library and add them to `tools/nation/media.json`, make sure `data/<slug>.json` exists, run the build, add `pn-bp-<slug>` to the manifest.

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
| `nations` | The golden planet (one gold light per recorded asset, placed at `lat`, `lon`; a tap or click opens the nation's card with its lead asset, `top`, the first card of its blueprint) and the list of nations, each linking to its blueprint. Counted with the ledger |
| `updated`, `stamp` | "Updated D Month YYYY" in the hero: the day the ledger or the five assets last changed (`stamp` is a short fingerprint of what the last build saw); set by the build |
| `featured` | The five assets, in order. Each: `cls` (one of the eight classes), `figure`, `unit`, `line` (the words under the figure), `name`, `nation`, `flags` (two-letter codes), `text`, `source` (the link text), `url` (the source), `link` (the nation's five assets on its blueprint, `.../#bp-assets`), `image` (the 1536 px copy, or the largest copy there is, with its width in `image_w`) and `image_small` (768 px copy) from the Media Library, and `alt`. Each should be one of the five assets on the nation's blueprint, in step with its Nation Steward |

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
 "dispatches": [ ... ],               // the Solutions Perfect Nations designs, highest number first
 "deals": [ ... ]                     // the Deal Notes, newest first
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

**Solution entry** (`dispatches`; the list keeps its name so the homepage and the blueprints keep reading it). From 9 November 2026 each entry is a Solution that Perfect Nations designs, `kind` "design", one for each open blueprint nation.

| field | rule |
|---|---|
| `no` | Solution number, unique among the Solutions; the next is the highest number plus one |
| `kind` | "design" |
| `slug`, `nation`, `blueprint` | the nation exactly as its blueprint names it ("Côte d’Ivoire") and the blueprint url |
| `title`, `kicker`, `date` | the name of the Solution (at most 60 characters), "Perfect Nations Solution", the date it was designed |
| `standfirst` | the idea in one line (at most 160 characters) |
| `standards` | the standards it moves, in the order Food, Water, Shelter, Energy, Education, Health, Livelihood; it always includes the nation's standard furthest from reach |
| `challenge` | the challenge in one or two sentences (at most 360 characters), with the nation's own sourced figure |
| `advises` | What Perfect Nations advises, two sentences (at most 520 characters): the finance move first; the second begins "With super intelligence," and says what it makes possible. No new figures, no results claimed, and the word "Finance" in place of "pay" |
| `how` | three lines: 01 Assets (what the nation owns that carries it), 02 Capital (the instrument), 03 Solutions (what changes for citizens) |
| `proof` | the deal that proves it: name, where, year, figure, label, source, url, from `data/capital-architecture.json` or the nation's own record; `own` true for an instrument Perfect Nations designed (Standard Tokens, pending compliance review) |
| `first` | the first move, one sentence |
| `figure`, `caption`, `gap_seen` | the card figure (at most 18 characters, with a digit), its caption (at most 120), and the nation's gap when the Solution was written (a changed gap means the challenge needs a fresh look) |
| `sources` | list of {"label", "url"}, every url https: the source of the challenge, then the proof |

**Deal Note entry** (`deals`): a landmark market deal read by Perfect Nations (these were the Solutions before 9 November 2026, and keep their numbers). Fields as before: `no`, `kind` "deal", `slug`, `title`, `kicker`, `date`, `nation`, `standards`, `standfirst`, `challenge`, `advises`, `figure`, `caption`, `url` (the WordPress post) or `body` (paragraphs; a line starting "## " is a heading), `figures`, `kick`, `sources`. A Deal Note opens at `/state-of-nations/#deal-NN`. A new Deal Note takes the next number in `deals`, never a number in `dispatches`.

Wire items are committed straight to main. A new Solution or Deal Note is proposed only as a pull request titled "For approval: Solution No. NN" or "For approval: Deal Note No. NN" and goes live when Preeti Sinha, President and CEO, merges it.

## The Perfect Capita page

The page is one file, `pages/perfect-capita.html` (root `pn-pcap`), served by the Live Pages plugin. It is kept by the **Perfect Capita Steward**, which owns the page and nothing else.

- **Page code** goes through a pull request. Edit `src/perfect-capita.html`, never the built file, then run `python3 tools/build_perfect_capita.py`: it adds the gold line's style (shared with the homepage, `pages/home-rule.html`), writes `pages/perfect-capita.html` and runs the validation suite (`tools/check_page.py`). Raise the version in the source banner and in `pages/manifest.json`, render previews with `python3 tools/preview_page.py pages/perfect-capita.html`, and open "For approval: Perfect Capita vX.Y, [what changed]".
- **Figures** live in `figures/perfect-capita.json`. The page reads it on every visit (raw.githubusercontent.com, then jsDelivr) and fills every element marked `data-pc="path"` with the text at that path, and every `data-pc-href` link with an https url. After the Auditor the Steward commits this file straight to main, like a nation file. If the file is unreadable, is for another page, or breaks the rules below, the page keeps the figures written into it.

| Field | What it drives on the page |
|---|---|
| `page` | Must be `"perfect-capita"` |
| `updated`, `checked` | The last change (YYYY-MM-DD) and the last check (YYYY-MM-DDTHH:MMZ, UTC); not shown |
| `world` | The world today: exactly seven, in the order Food, Water, Shelter, Energy, Education, Health, Livelihood. Each: `standard`, `value` (for example "2.1"), `unit` ("bn", "m", " in 10"), `text` (one line, starting with the people it counts), `source` (the link text: publisher, year, and the data year) and `url` (the primary source) |
| `nations` | It has been done: exactly five, in the order Thailand, Vietnam, Singapore, Brazil, Rwanda (to change a nation, change the page by pull request). Each: `nation`, `standard`, `figure`, `what`, `source`, `url` |
| `first` | The first nation priced (Barbados), copied from `data/barbados.json` `coverage` and the Measurer's floor: `perfect_capita`, `price`, `coverage`, `set_by`, `gap` and `lead` (two sentences). Never changed here before the Measurer changes them |

Every text is plain, without contractions, under 400 characters; every url https with no quotes, brackets or spaces. The seven world figures overlap and are never added together.
