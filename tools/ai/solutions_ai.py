#!/usr/bin/env python3
"""Now possible with AI: one line for each Solution Perfect Nations designs (Preeti Sinha, President and CEO, 24 Nov 2026).

    "I would like to bring SI back into Perfect Nations ... I believe SI can make the solutions to development
     challenges possible which were not feasible before."

The decision of 24 Nov 2026: innovative financing for development (FfD) is always named first and finances the
Solution; AI makes it possible and proves it. On the site the Solutions say "AI" (what exists today) and the vision
says "super intelligence" (where it is heading). Each line below says what AI makes possible for that Solution:
no figures, no results claimed, no contractions, never "pay".

    python3 tools/ai/solutions_ai.py          write the "ai" field of every designed Solution in
                                              data/state-of-nations.json (placed after "advises")
    python3 tools/ai/solutions_ai.py --check  list designed Solutions without a line (exit 1 if any)

A new Solution gets its line here, in the same pull request that proposes it.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FILE = ROOT / 'data' / 'state-of-nations.json'
MAX = 200

AI = {
    1: 'AI scores farms along the railway from satellite images and mobile-money records, so banks can lend to growers with no credit history.',
    2: 'AI confirms each switch from the stove’s own data and the mobile-money repayments, so every carbon credit is verified household by household.',
    3: 'AI screens Batswana firms for the fund and counts the jobs each investment creates, so every diamond dividend can be followed to work.',
    4: 'AI maps every hill village from satellite images and verifies each connection from meter data, so grants are released on proof, not paperwork.',
    5: 'AI maps informal homes from satellite images and values the land each new transit line lifts, so a city knows what each bond can finance.',
    6: 'AI runs short reading checks by phone in every school of the cocoa regions, so the fund can release money on learning, school by school.',
    7: 'AI tracks reading levels school by school and flags the schools falling behind, so each tranche follows proven learning that outcome funders can see.',
    8: 'AI follows the savings of the conversion into every province and tracks reading results, so the conversion can be audited year after year.',
    9: 'AI scores national reading assessments quickly and consistently, so a coupon can be tied to learning and checked by every investor.',
    10: 'AI reads meter and water-quality data home by home, so each connection is verified before its funds are released.',
    11: 'AI reads smart-meter data to confirm that each kitchen cooks with electricity, so carbon credits and bill finance rest on measured use.',
    12: 'AI tracks cyclones and reads satellite images of reefs and coasts, so cover triggers on measured damage and islanders recover their income faster.',
    13: 'AI maps the homes without a toilet from satellite and survey data, so the bond reaches the poorest homes first and reports every toilet built.',
    14: 'AI maps the households without safe water on every island and finds the leaks in each network, so the proceeds go where water reaches homes.',
    15: 'AI forecasts the storm and reads the damage farm by farm from satellite images, so parametric cover reaches a farmer’s mobile wallet within days.',
    16: 'AI measures reading levels in every school, refugee schools included, so partners release money only on verified learning.',
    17: 'AI tracks reading in every school, the most remote mountain schools included, so the royalties reward learning that is measured, not assumed.',
    18: 'AI reads satellite images of the forest to measure the charcoal cutting each project prevents, so carbon credits can be verified and sold.',
    19: 'AI scores customers from their instalment records, so solar companies can prove their loan books and borrow in kwacha.',
    20: 'AI finds the leaks and unbilled connections in each municipal network, so utilities can show investors the savings that will repay them.',
    21: 'AI runs each treatment plant on its own solar power and forecasts farm demand for treated water, so the sales that service the bond can be planned.',
    22: 'AI maps the households still cooking with charcoal and verifies each switch, so lenders can finance clean kitchens now against revenue that comes later.',
    23: 'AI matches trainees to the hydrogen, solar and wind jobs as they open and tracks who stays employed, so investors are rewarded for lasting jobs.',
    24: 'AI forecasts harvests and prices and checks the grain in each warehouse by sensor, so warehouse receipts become collateral banks can trust.',
    25: 'AI finds the children out of school, village by village, and tracks reading results, so each tranche follows children back into class.',
    26: 'AI tutors on a phone reach the children furthest behind on every island and track their reading, so bondholders see what their savings finance.',
    27: 'AI reads satellite images to prove the forest still stands and tracks reading in each community school, so carbon revenue rewards both.',
    28: 'AI reads meter and water-quality data from every connection, so the return of the bond rises only with safe water verified.',
    29: 'AI verifies each household connection through mobile-money and meter data, so grants reach homes even where officials cannot travel.',
    30: 'AI scores reading for meaning in every participating school, so the outcome funder can see the result before the return is set.',
    31: 'AI checks the oil revenue account against every connection it finances and publishes both, so partners can match each verified connection.',
    32: 'AI measures the power each roof produces and saves, so the bonds can be serviced from verified savings, roof by roof.',
    33: 'AI plans the last-mile lines from satellite maps of every settlement and reads meter data, so lenders see each connection and cooker earn its return.',
    34: 'AI reads each cooker’s meter data to verify clean cooking, so carbon credits can be issued for every household that switches.',
    35: 'AI reads satellite images of fields and damage across the regions at war, so cover and credit can be priced where no inspector can go.',
    36: 'AI counts the homes connected to each sewer from network and meter data, so returns tied to homes connected can be reported to the market.',
    37: 'AI tracks reading in every school and flags the schools falling behind, so each kwacha of the windfall rewards measured learning.',
    38: 'AI maps the homes without safe sanitation in every town and district, so the bond reaches the worst served first and reports each toilet built.',
    39: 'AI tutors and reading checks on a phone reach children in community and home schools, so learning can be measured even where classrooms are closed to girls.',
    40: 'AI ties each token to one household’s verified switch, read from the cooker’s own data, so every buyer can see the kitchen they financed.',
    41: 'AI maps every street still without a sewer from satellite and utility data, so the return of the bond rises with each connection verified.',
    42: 'AI measures the power each school roof produces and the reading progress of its pupils, so savings and results are verified school by school.',
    43: 'AI tracks reading in every school through short checks by phone, so funds reach schools as children read and citizens can follow their bond.',
    44: 'AI tracks every farm and fishery the savings reach and forecasts each harvest and catch, so the swap shows the island growing more of what it eats.',
    45: 'AI plans each line and village connection from satellite maps of settlements, so lenders finance the lowest-cost route to every home.',
    46: 'AI forecasts solar output and demand in each city, so the reserve can be sized to the bills it stands behind.',
    47: 'AI audits every medicine purchase against prices and deliveries, so creditors can see each converted dollar reach a pharmacy shelf.',
    48: 'AI reads satellite data to find and measure every flare, so investors know how much gas each site can turn into power.',
    49: 'AI maps where the need for power is greatest and tracks each system installed, so the fund can publish what every contribution delivers.',
    50: 'AI maps the markets, clinics and homes without power from satellite images, so the bond finances the mini-grids that reach the most people first.',
    51: 'AI maps the counties where families go short of fresh food, down to the neighbourhood, so each state fund places grocers and cold chains where they matter most.',
    53: 'AI matches the small firms that hire with the workers who need better jobs and counts the jobs each guarantee creates, so savers see the work they finance.',
}



def problems(no, text):
    out = []
    if len(text) > MAX:
        out.append('longer than %d characters (%d)' % (MAX, len(text)))
    if not text.startswith('AI '):
        out.append('does not begin with "AI "')
    if re.search(r'\d', text):
        out.append('carries a figure')
    if re.search(r'\b(pay|pays|paid|paying)\b', text, re.I):
        out.append('says "pay": write "finance"')
    if re.search(r"n['’]t\b|\b(it|that|there|they|we|you)['’](s|re|ve|ll|d)\b", text, re.I):
        out.append('has a contraction')
    if "'" in text or '"' in text:
        out.append('has a straight quotation mark')
    if re.search(r'super ?intelligence|\bSI\b', text, re.I):
        out.append('a Solution says AI, not super intelligence')
    return ['Solution No. %02d: %s' % (no, p) for p in out]


def main():
    son = json.loads(FILE.read_text(encoding='utf-8'))
    designs = [d for d in son['dispatches'] if d.get('kind') == 'design']
    bad = []
    for no, text in AI.items():
        bad += problems(no, text)
    missing = [d['no'] for d in designs if d['no'] not in AI]
    if '--check' in sys.argv:
        for b in bad:
            print(b)
        for n in missing:
            print('Solution No. %02d has no "Now possible with AI" line' % n)
        sys.exit(1 if bad or missing else 0)
    if bad:
        print('\n'.join(bad))
        sys.exit(1)
    changed = 0
    for i, d in enumerate(son['dispatches']):
        if d.get('kind') != 'design' or d['no'] not in AI or d.get('ai') == AI[d['no']]:
            continue
        nd = {}
        for k, v in d.items():
            if k == 'ai':
                continue
            nd[k] = v
            if k == 'advises':
                nd['ai'] = AI[d['no']]
        if 'ai' not in nd:
            nd['ai'] = AI[d['no']]
        son['dispatches'][i] = nd
        changed += 1
    FILE.write_text(json.dumps(son, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('%d Solutions given their line; %d without one: %s' % (changed, len(missing), missing))


if __name__ == '__main__':
    main()
