"""Cuba: the seven standards re-measured on 12 November 2026 (the delivery test).

The Steward-General asked for the Cuba figures to be revisited: the first edition (10 November 2026)
read only World Bank indicators of connection and access, which counted every Cuban as having
electricity and 96 per cent as cooking with clean fuels while the grid serves about a third of demand.

The delivery test: where the nation's own agencies publish how much of a service actually reaches
people, the standard takes the lower of the strict measure and that delivered share.
Run: python3 tools/measures/cuba_2026_11_12.py   (prints the figures written to data/cuba.json)
"""

P = 9434593                      # ONEI, population with effective residence, 31 Dec 2025 (Prensa Latina, 21 Jul 2026)
P_WB = 10937203                  # World Bank WDI, 2025 (the first edition used this figure)

# Water: basic water (WHO/UNICEF JMP, 2024) and people with piped supply cut, dawn of 3 Nov 2026 (INRH, Cubadebate, 4 Nov 2026)
water_basic = 95.15
water_cut = 2681770
water_reaching = (1 - water_cut / P) * 100

# Energy: clean cooking (WHO via World Bank, 2024) and the evening peak, 10 Nov 2026 (Union Electrica, Granma)
clean_cooking = 96.0
peak_available_mw, peak_demand_mw, peak_cut_mw = 970, 2900, 1960
grid_served = peak_available_mw / peak_demand_mw * 100

# Health: WHO UHC service coverage index (2023) and the basic medicines list available (President of Cuba, 8 Aug 2026)
uhc = 86.0
medicines_available = 30.0

c = {
    'Food': None,                                  # no FAO FIES survey for Cuba
    'Water': min(water_basic, water_reaching),
    'Shelter': 45.88,                              # safely managed sanitation, JMP 2024 (unchanged)
    'Energy': min(clean_cooking, grid_served),
    'Education': 89.2,                             # lower-secondary completion, UIS 2024 (unchanged)
    'Health': min(uhc, medicines_available),
    'Livelihoods': None,                           # no poverty survey for Cuba
}

if __name__ == '__main__':
    print('Population of record: %s (ONEI); World Bank shows %s, %.1f%% higher' % (format(P, ','), format(P_WB, ','), (P_WB / P - 1) * 100))
    print('Water reaching homes: 1 - %s / %s = %.1f%% (basic water %.1f%%)' % (format(water_cut, ','), format(P, ','), water_reaching, water_basic))
    print('Grid at the evening peak: %d / %d MW = %.1f%% (cut %d MW = %.1f%%)' % (peak_available_mw, peak_demand_mw, grid_served, peak_cut_mw, peak_cut_mw / peak_demand_mw * 100))
    print('Health: lower of UHC %.0f and medicines available %.0f%%' % (uhc, medicines_available))
    for k, v in c.items():
        print('  %-11s %s' % (k, 'Not measured' if v is None else '%.1f' % v))
    scored = {k: v for k, v in c.items() if v is not None}
    bind = min(scored, key=scored.get)
    print('Furthest from reach: %s at %.1f; the gap: %.0f%%' % (bind, scored[bind], 100 - scored[bind]))
    print('Breadth of the five measured: %.1f' % (sum(scored.values()) / len(scored)))
