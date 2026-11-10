# Official downloads behind the 50 States page

Pulled on 10 November 2026 (16:52 UTC, `pulled-at.txt`) by a temporary GitHub Actions run, because the
Census Bureau and BEA sites cannot be reached from the build workspace. `python3 tools/build_us_states.py --data`
reads only these files and writes `data/us-states.json`.

| File | Source | Used for |
|---|---|---|
| `NST-EST2025-ALLDATA.csv` | U.S. Census Bureau, Vintage 2025 population estimates, https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv | `POPESTIMATE2025` (1 July 2025) and `REGION` (the four Census regions) |
| `SAGDP1__ALL_AREAS_1997_2025.csv` | U.S. Bureau of Economic Analysis, SAGDP (last updated 30 September 2026), https://apps.bea.gov/regional/zip/SAGDP.zip | LineCode 3, current-dollar GDP (millions of current dollars), 2025 |
| `acsdt1y2025-b17001-states.dat` | U.S. Census Bureau, ACS 2025 1-year table-based summary file, https://www2.census.gov/programs-surveys/acs/summary_file/2025/table-based-SF/data/1YRData/acsdt1y2025-b17001.dat (the nation and state rows, first five columns) | B17001_E001 (population for whom poverty status is determined) and B17001_E002 (income in the past 12 months below poverty level), with E002's margin of error |
| `shells-B17001.txt` | The table shells of the same release | The labels of B17001_001 and B17001_002 |
| `var-2025-*.json` | api.census.gov variable labels | Reference only (the Census API now needs a key, so the figures come from the file server) |
