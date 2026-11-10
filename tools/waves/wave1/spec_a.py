def R(cat, status, name, detail, amount, text, by, url, note='', tone='active', money=True):
    d = {'cat': cat, 'status': status, 'tone': tone, 'name': name, 'detail': detail, 'amount': amount, 'money': money and bool(amount),
         'text': text, 'by': by, 'url': url}
    if note:
        d['note'] = note
    return d


def C(value, text, source, url, money=True):
    return {'value': value, 'money': money, 'text': text, 'source': source, 'url': url}


def W(date, title, url, source, highlight=''):
    return {'date': date, 'title': title, 'highlight': highlight, 'url': url, 'source': source}


WDI = 'World Bank, World Development Indicators (API, last updated 8 October 2026), accessed 10 November 2026: population 2025, ages 0 to 14 2025, land area and agricultural and forest land 2024, renewable fresh water per person 2022, natural resource rents 2021, renewable electricity output 2021, electricity access and clean cooking 2024.'
STD = 'The seven standards: FAO food insecurity, WHO/UNICEF JMP water and sanitation, UN-Habitat urban slums, World Bank clean cooking, learning poverty and lower-secondary completion, and poverty headcounts (all via the World Bank); WHO UHC service coverage index, 2023.'

IMF_DZA_1 = 'https://www.imf.org/en/news/articles/2026/07/06/pr26236-algeria-imf-staff-completes-2026-article-iv-mission'
IMF_DZA_2 = 'https://www.imf.org/en/news/articles/2026/09/21/pr26290-algeria-imf-concludes-2026-aiv-consultation'
ZAW_DZA = 'https://www.zawya.com/en/projects/oil-and-gas/algeria-approves-54bln-illizi-south-hydrocarbon-project-x93mprrf'
FA_DZA = 'https://www.financialafrik.com/en/2026/05/06/algeria-sonatrach-signs-a-contract-of-over-one-billion-usd-with-pttep-and-an-export-agreement-to-egypt/'

IMF_BEN = 'https://www.imf.org/en/news/articles/2026/02/25/pr-26063-benin-imf-completes-the-7th-rev-of-ext-fund-and-ecf-and-4th-rev-of-rsf'
WB_BEN_CPF = 'https://www.worldbank.org/en/news/press-release/2026/06/16/a-new-country-partnership-framework-and-320-million-for-benin'
WB_BEN_W = 'https://www.worldbank.org/en/news/press-release/2026/01/16/benin-10000-women-entrepreneurs-receive-business-development-support'
WB_BEN_GAS = 'https://www.worldbank.org/en/news/press-release/2026/07/20/gas-market-development-lower-energy-costs-create-jobs-unlock-private-investment'
WB_WACA = 'https://www.worldbank.org/en/news/press-release/2026/03/18/safeguarding-coasts-driving-jobs-waca-to-protect-530-000-people-and-catalyze-13-000-blue-economy-jobs'
WB_COSO = 'https://www.worldbank.org/en/news/press-release/2026/06/25/world-bank-scales-up-support-to-boost-jobs-and-resilience-in-northern-gulf-of-guinea'

IMF_BFA = 'https://www.imf.org/en/news/articles/2026/02/19/pr-26054-burkina-faso-imf-completes-4th-rev-under-ecf-and-approves-under-the-rsf'
IMF_BFA_CR = 'https://www.imf.org/-/media/files/publications/cr/2026/english/1bfaea2026002.pdf'
ECO_BFA = 'https://www.ecofinagency.com/news/1902-53078-imf-completes-fourth-review-of-burkina-fasos-extended-credit-facility-and-approves-124-3-million-climate-resilience-program'
WB_BFA_AG = 'https://www.worldbank.org/en/news/press-release/2026/03/10/burkina-faso-a-new-project-to-accelerate-the-transformation-of-the-agricultural-sector'
WB_BFA_SP = 'https://www.worldbank.org/en/news/press-release/2026/07/15/burkina-faso-new-world-bank-financing-to-expand-economic-opportunities-and-strengthen-social-protection-systems'

IMF_CPV = 'https://www.imf.org/en/news/articles/2026/02/07/pr26036-cabo-verde-imf-concl-2025-aiv-consultation-7th-rev-under-ecf-and-3rd-rev-under-rsf'
CA_CPV_WB = 'https://www.channelafrica.co.za/channelafrica/?p=39588'
CA_CPV_IMF = 'https://www.channelafrica.co.za/channelafrica/?p=23437'

FA_CMR_DEBT = 'https://www.financialafrik.com/en/?p=493963'
IMF_CMR_PFA = 'https://www.imf.org/en/news/articles/2026/10/01/pr26314-imf-staff-concludes-assesment-cameroon'
IMF_CMR_8 = 'https://www.imf.org/en/News/Articles/2025/07/24/pr-25265-cameroon-imf-concludes-8th-rev-under-ecf-and-eff-and-3rd-rev-under-rsf'
IMF_CMR_7 = 'https://www.imf.org/en/News/Articles/2025/03/12/pr-2559-cameroon-imf-concludes-7th-rev-of-ecf-eff-2nd-review-of-rsf'
CAP_CMR = 'https://www.capmad.com/post/imf-yaounde-opens-talks-on-a-new-20262029-program-after-the-end-of-the-fececf-arrangement'
FA_CMR_GR = 'https://www.financialafrik.com/en/2026/08/02/by-june-30-2026-cameroon-experiences-a-growth-of-3-7-with-the-imf-in-sight-for-2027/'

IMF_CAF = 'https://www.imf.org/en/news/articles/2025/06/04/pr-25179-car-imf-completes-3rd-4th-rev-under-ecf-arrang-and-approves-us-58-mil-disburse'
IMF_CAF_CR = 'https://www.imf.org/en/publications/cr/issues/2025/06/23/central-african-republic-third-and-fourth-review-under-the-extended-credit-facility-567911'
FA_CAF = 'https://www.financialafrik.com/en/?p=490143'

IMF_TCD = 'https://www.imf.org/en/news/articles/2025/07/25/pr25269-chad-imf-executive-board-approves-a-new-48-month-ecf-arrangement'
IMF_TCD_SLA = 'https://www.imf.org/en/news/articles/2025/12/19/prr-25437-chad-imf-staff-reaches-agreement-with-chadian-authorities-on-the-1st-rev-under-ecf'
AFX_TCD = 'https://www.eabusinesstimes.com/afreximbank-extends-eur110-million-facility-to-chad-in-largest-ever-financing-support-to-the-country/'
RT_TCD = 'https://www.riotimesonline.com/chad-economy-explained-2026/'

NATIONS = [
    {
        'slug': 'algeria', 'name': 'Algeria', 'iso3': 'DZA', 'iso2': 'DZ', 'ne': 'Algeria', 'demonym': 'Algerians', 'of_people': 'Algerians',
        'steward': 'Amina Benali',
        'lead': 'Africa’s largest nation by land, home to 47.4 million, where every household has electricity and public debt reached 52.1% of GDP in 2025, financed almost entirely at home.',
        'stats': [{'value': '$51.0bn', 'label': 'Gross official reserves, 2025'}, {'value': '52.1%', 'label': 'Public debt, share of GDP, 2025'},
                  {'value': '0.8%', 'label': 'Gross external debt, share of GDP, 2025'}],
        'cap_heading': 'A nation that borrows at home and sells energy abroad.',
        'record': [C('52.1%', 'Public debt, share of GDP, 2025, driven by large financing needs', 'IMF, 2026', IMF_DZA_1, False),
                   C('$51.0bn', 'Gross official reserves, 2025; projected at $46.5 billion in 2026', 'IMF, 2026', IMF_DZA_2),
                   C('$5.4bn', 'Illizi South development agreement between Sonatrach and Midad Energy, ratified by presidential decree', 'Zawya, 2025', ZAW_DZA),
                   C('0.8%', 'Gross external debt, share of GDP, 2025', 'IMF, 2026', IMF_DZA_2, False)],
        'register': [R('private', 'Signed', 'Illizi South hydrocarbon development', 'Sonatrach and Midad Energy · Ratified by presidential decree', '$5.4bn',
                       'A development agreement for the Illizi South block between the state energy company and Saudi Arabia’s Midad Energy.', ['Sonatrach', 'Midad Energy'], ZAW_DZA),
                     R('private', 'Signed', 'Hassi Bir Rekaiz field', 'Sonatrach and PTTEP · Signed May 2026', '$1bn+',
                       'A contract worth more than US$1 billion with Thailand’s PTTEP to develop the Hassi Bir Rekaiz field.', ['Sonatrach', 'PTTEP'], FA_DZA)],
        'newswire': [W('2026-09-21', 'IMF Executive Board Concludes 2026 Article IV Consultation with Algeria', IMF_DZA_2, 'IMF'),
                     W('2026-07-06', 'IMF Staff Completes 2026 Article IV Mission to Algeria', IMF_DZA_1, 'IMF'),
                     W('2026-05-06', 'Algeria: Sonatrach signs a contract of over one billion USD with PTTEP and an export agreement to Egypt', FA_DZA, 'Financial Afrik', 'one billion USD')],
        'assets': [dict(name='The Reserves', figure='$51.0bn', money=True, label='Gross official reserves, 2025', text='A national cushion few nations hold, enough to anchor long-term finance at home.', src='IMF, 2026 Article IV (PR 26/290)'),
                   'land', 'ground', dict(name='The Grid', figure='100%', money=False, label='Of citizens with electricity, 2024', text='Every household connected, and every kitchen cooking with clean fuels: a base for industry beyond hydrocarbons.', src='World Bank, access to electricity and clean cooking, 2024'),
                   'people'],
        'land_text': 'Africa’s largest territory: desert sun, gas fields and a Mediterranean coast.',
        'ground_text': 'Oil and gas rents carry the budget; the task is to turn them into assets that outlast them.',
        'letter': 'You are Africa’s largest nation by land, and every one of your households has electricity. Your gas still carries the budget, and your debt is held almost entirely at home. Use these years of energy income to build the assets that will carry the next fifty.',
        'quote': 'Gas built the grid. Let the grid, the land and the people now finance the next fifty years.',
        'sources': [WDI, STD, 'IMF, IMF Staff Completes 2026 Article IV Mission to Algeria, 6 July 2026; IMF Executive Board Concludes 2026 Article IV Consultation with Algeria, PR 26/290, 21 September 2026.',
                    'Zawya: Algeria approves $5.4bln Illizi South hydrocarbon project. Financial Afrik, 6 May 2026: Sonatrach and PTTEP.'],
        'gaps': ['Gas reserves and export volumes: no primary page read yet (Sonatrach or the Ministry of Energy and Mines).', 'Learning outcomes date from 2007.'],
    },
    {
        'slug': 'benin', 'name': 'Benin', 'iso3': 'BEN', 'iso2': 'BJ', 'ne': 'Benin', 'demonym': 'Beninese', 'of_people': 'Beninese',
        'steward': 'Rachida Dossou',
        'lead': 'A nation of 14.8 million that held its deficit within the regional ceiling a year early, and in June 2026 drew $320 million from the World Bank for a dam and for nutrition.',
        'stats': [{'value': '$320M', 'label': 'World Bank financing approved, June 2026'}, {'value': '2.9%', 'label': 'Fiscal deficit, share of GDP, 2025 estimate'},
                  {'value': '60.5%', 'label': 'Central government debt, share of GDP, 2024'}],
        'cap_heading': 'Fiscal discipline, then dams, food and coast.',
        'record': [C('$320M', 'Two IDA operations with a new Country Partnership Framework: the Dogo-Bis dam and the Alafia nutrition programme', 'World Bank, 2026', WB_BEN_CPF),
                   C('60.5%', 'Central government debt, share of GDP, end-2024, after reclassifying loans held by public enterprises; moderate risk of debt distress', 'IMF, 2026', IMF_BEN, False),
                   C('$118M', 'Disbursed on completion of the final reviews of the IMF programme, February 2026', 'IMF, 2026', IMF_BEN),
                   C('$100M', 'IDA financing for women entrepreneurs, January 2026', 'World Bank, 2026', WB_BEN_W)],
        'register': [R('multi', 'Approved', 'Dogo-Bis Multipurpose Dam, Phase 1', 'IDA · Approved 16 June 2026', '$150M', 'Phase 1 of a dam programme with an overall envelope of $580 million.', ['World Bank'], WB_BEN_CPF, note='Overall envelope $580 million'),
                     R('multi', 'Approved', 'Alafia 1, Feeding Benin for the Future', 'IDA and GFF · Approved 16 June 2026', '$170M', 'Nutrition, health and early childhood services for women and children: $150 million from IDA and $20 million from the Global Financing Facility.', ['World Bank', 'Global Financing Facility'], WB_BEN_CPF),
                     R('multi', 'Approved', 'Women entrepreneurs (WEDAF)', 'IDA · Approved 15 January 2026', '$100M', 'Access to finance and growth for women entrepreneurs in the formal and informal sectors.', ['World Bank'], WB_BEN_W),
                     R('regional', 'Approved', 'West Africa gas market development', 'IDA · Approved 29 June 2026 · With Côte d’Ivoire and Togo', '$45M', 'Benin’s share of a $140 million regional project to build national gas markets and shared supply.', ['World Bank'], WB_BEN_GAS),
                     R('regional', 'Approved', 'West Africa Coastal Areas (WACA+), Phase 1', 'IDA, PROBLUE and private capital · Approved 17 March 2026 · With Mauritania', '$240M', 'Coastal protection and blue economy jobs at the Bouche du Roy estuary and the mouth of the Mono river.', ['World Bank'], WB_WACA, note='Total for Benin and Mauritania')],
        'newswire': [W('2026-07-20', 'Benin: 320 million USD from the World Bank for energy and nutrition', 'https://www.capmad.com/post/benin-320-million-usd-from-the-world-bank-for-energy-and-nutrition', 'Capmad', '320 million USD'),
                     W('2026-06-27', 'World Bank Adds $163M for Northern Gulf of Guinea Project', 'https://dabafinance.com/en/news/world-bank-adds-funding-gulf-of-guinea-project', 'Daba Finance', '$163M'),
                     W('2026-02-25', 'Benin: IMF Executive Board Completes the Seventh Reviews of Extended Fund and Extended Credit Facilities, and Fourth Review of the Resilience and Sustainability Facility', IMF_BEN, 'IMF')],
        'assets': ['farmland', 'forest', dict(name='The Coast', figure='$240M', money=True, label='Committed to the coast with Mauritania, 2026', text='An Atlantic shoreline and a port economy, now protected and financed as a blue economy.', src='World Bank, WACA+ press release, 17 March 2026'),
                   'water', 'people'],
        'farm_text': 'Farmland that already feeds the sub-region and grows its cotton.',
        'letter': 'You brought your deficit within the regional ceiling a year before it was due, and your partners have answered with dams, nutrition and coastal protection. Four in ten of you are under fifteen. The task is to turn a reputation for discipline into capital priced for it.',
        'quote': 'You kept your word on the budget. Now let the markets price it, and let the price fund your children.',
        'sources': [WDI, STD, 'World Bank press releases, 15 January, 17 March, 16 June and 29 June 2026, as linked.', 'IMF, PR 26/063, 25 February 2026: seventh reviews of the EFF and ECF and fourth review of the RSF.'],
        'gaps': ['Cotton output and exports: no primary page read yet.', 'Safely managed sanitation is measured; safely managed water is measured.'],
    },
    {
        'slug': 'burkina-faso', 'name': 'Burkina Faso', 'iso3': 'BFA', 'iso2': 'BF', 'ne': 'Burkina Faso', 'demonym': 'Burkinabè', 'of_people': 'Burkinabè',
        'steward': 'Aminata Ouédraogo',
        'lead': 'A nation of 24.1 million whose gold lifted growth to 5.3% in 2025, and which secured $215.9 million in 2026 to transform its farms.',
        'stats': [{'value': '$215.9M', 'label': 'Agricultural transformation financing, March 2026'}, {'value': '5.3%', 'label': 'Growth, 2025'},
                  {'value': '52.1%', 'label': 'Total public debt, share of GDP, 2025 projection'}],
        'cap_heading': 'Gold income, and capital for the farms.',
        'record': [C('$215.9M', 'Burkina Faso Agricultural Transformation Project, approved 10 March 2026', 'World Bank, 2026', WB_BFA_AG),
                   C('$120M', 'Economic opportunities and social protection, approved 15 June 2026: $100 million IDA credit and a $20 million grant', 'World Bank, 2026', WB_BFA_SP),
                   C('$302M', 'Extended Credit Facility, 48 months, approved September 2023, augmented June 2026', 'IMF, 2026', IMF_BFA_CR),
                   C('52.1%', 'Total public debt, share of GDP, projected for 2025, down from 57.2% in 2024', 'Ecofin Agency, 2026', ECO_BFA, False)],
        'register': [R('multi', 'Approved', 'Agricultural Transformation Project', 'IDA · Approved 10 March 2026', '$215.9M', 'Productivity, storage, agro-processing and access to finance in four high-potential regions, with women and youth included.', ['World Bank'], WB_BFA_AG),
                     R('multi', 'Approved', 'Economic Opportunities for Resilience', 'IDA and Sahel Adaptive Social Protection Program · Approved 15 June 2026', '$120M', 'Economic opportunities for vulnerable households and a stronger social protection system, over five years.', ['World Bank'], WB_BFA_SP),
                     R('multi', 'Active', 'Extended Credit Facility and Resilience and Sustainability Facility', 'IMF · ECF approved September 2023 · RSF approved February 2026', '', 'Fifth ECF review, augmentation and first RSF review completed 26 June 2026.', ['IMF'], IMF_BFA_CR)],
        'newswire': [W('2026-03-18', 'Burkina Faso: World Bank Grants $216 Million to Boost Agriculture', 'https://www.capmad.com/post/burkina-faso-world-bank-grants-216-million-to-boost-agriculture', 'Capmad', '$216 Million'),
                     W('2026-02-19', 'IMF Completes Fourth Review of Burkina Faso’s Extended Credit Facility and Approves $124.3 Million Climate Resilience Program', ECO_BFA, 'Ecofin Agency', '$124.3 Million')],
        'assets': [dict(name='The Gold', figure='43.2%', money=False, label='Rise in gold exports, 2025', text='Gold carried the current account into surplus in 2025; the task is to bank the windfall into lasting assets.', src='Ecofin Agency, 19 February 2026, citing the IMF'),
                   'farmland', 'ground', 'forest', 'people'],
        'farm_text': 'Six tenths of the land in agriculture: the base for food at home and income abroad.',
        'letter': 'Your gold lifted growth in 2025 and turned your current account to surplus. Most of you live from the land, and four in ten are under fifteen. The task is to bank the gold into farms, schools and power that last beyond the price of gold.',
        'quote': 'Gold is a season. Farms, schools and power are a century. Let the season pay for the century.',
        'sources': [WDI, STD, 'IMF, PR 26/054, 19 February 2026; IMF Country Report 26/207 (2026 Article IV, fifth ECF review), June 2026. Ecofin Agency, 19 February 2026.', 'World Bank press releases, 10 March and 15 June 2026.'],
        'gaps': ['The gold export rise is read in Ecofin Agency, citing the IMF; the IMF staff report figure is to be confirmed.'],
    },
    {
        'slug': 'cabo-verde', 'name': 'Cabo Verde', 'iso3': 'CPV', 'iso2': 'CV', 'ne': None, 'small': True, 'latlng': (15.12, -23.6),
        'demonym': 'Cabo Verdeans', 'of_people': 'Cabo Verdeans', 'steward': 'Djamila Tavares',
        'lead': 'An island nation of 527,000 whose record tourism lifted growth to 6.3% in 2025, while public debt fell to 100.7% of GDP.',
        'stats': [{'value': '100.7%', 'label': 'Public debt, share of GDP, 2025'}, {'value': '6.3%', 'label': 'Growth, 2025'},
                  {'value': '$71.3M', 'label': 'IMF Extended Credit Facility, total access'}],
        'cap_heading': 'Debt falling, tourism rising.',
        'record': [C('100.7%', 'Public debt, share of GDP, 2025, still falling; debt service takes 34.2% of government revenue', 'World Bank via Channel Africa, 2026', CA_CPV_WB, False),
                   C('$71.3M', 'IMF Extended Credit Facility, access of 220% of quota; Resilience and Sustainability Facility $32.4 million', 'Channel Africa, 2026', CA_CPV_IMF),
                   C('5.2%', 'Growth estimated for 2025 by the IMF; 7.2% in 2024', 'IMF, 2026', IMF_CPV, False)],
        'register': [R('multi', 'Active', 'Extended Credit Facility', 'IMF · Seventh review completed 6 February 2026', '$71.3M', 'Stronger public finances, debt sustainability and reform of public enterprises.', ['IMF'], IMF_CPV),
                     R('multi', 'Active', 'Resilience and Sustainability Facility', 'IMF · Third review completed 6 February 2026', '$32.4M', 'Climate resilience reforms for an island nation.', ['IMF'], IMF_CPV)],
        'newswire': [W('2026-02-06', 'IMF Executive Board Concludes the 2025 Article IV Consultation, Seventh Review under the Extended Credit Facility Arrangement, and Third Review under the Resilience and Sustainability Facility Arrangement with Cabo Verde', IMF_CPV, 'IMF')],
        'assets': [dict(name='The Visitors', figure='6.3%', money=False, label='Growth in 2025, led by record tourism', text='Record arrivals already earn; the islands can price that demand into lasting infrastructure.', src='World Bank, Cabo Verde Economic Update, via Channel Africa'),
                   'grid', 'farmland', 'forest', 'people'],
        'grid_text': 'Wind and sun already supply part of the grid of a nation with no fuel of its own.',
        'letter': 'You are ten islands with no oil and no gold, and your debt has fallen as a share of your economy every year since the pandemic. Your visitors and your diaspora already invest in you. Let the next decade price the sun, the wind and the sea as the assets they are.',
        'quote': 'Islands without oil can still be rich in sun, wind and sea. Count them, and let them pay.',
        'sources': [WDI, STD, 'IMF, PR 26/036, 6 February 2026.', 'Channel Africa, IMF reviews and World Bank economic update, 2026, as linked.'],
        'gaps': ['Public debt is read in Channel Africa, citing the World Bank; the World Bank report itself is to be linked.', 'No outline at map scale: shown with the gold marker.', 'Learning outcomes not measured; lower-secondary completion used.'],
    },
    {
        'slug': 'cameroon', 'name': 'Cameroon', 'iso3': 'CMR', 'iso2': 'CM', 'ne': 'Cameroon', 'demonym': 'Cameroonians', 'of_people': 'Cameroonians',
        'steward': 'Esther Mbarga',
        'lead': 'A nation of 29.9 million with forest over four tenths of its land and two thirds of its power from renewable sources, now negotiating a new programme with the IMF.',
        'stats': [{'value': 'XAF 15.6tn', 'label': 'Public debt stock, end June 2026'}, {'value': '44.3%', 'label': 'Public-sector debt, share of GDP, March 2026'},
                  {'value': '65.8%', 'label': 'Electricity from renewable sources, 2021'}],
        'cap_heading': 'Forest, rivers and a debt to refinance.',
        'record': [C('XAF 15.6tn', 'Public debt stock at end June 2026, about $27 billion, monthly report of the Autonomous Amortization Fund', 'Financial Afrik, 2026', FA_CMR_DEBT),
                   C('44.3%', 'Public-sector debt, share of GDP, 31 March 2026, Ministry of Finance', 'Capmad, 2026', CAP_CMR, False),
                   C('$689.5M', 'IMF Extended Credit Facility and Extended Fund Facility, approved July 2021', 'IMF, 2025', IMF_CMR_7),
                   C('XAF 626bn', 'The PAD power plant public-private partnership, about $1.08 billion', 'Financial Afrik, 2026', FA_CMR_DEBT)],
        'register': [R('multi', 'Completed', 'Extended Credit Facility and Extended Fund Facility', 'IMF · Approved July 2021', '$689.5M', 'Three-year arrangements; the eighth reviews were completed in July 2025.', ['IMF'], IMF_CMR_7),
                     R('multi', 'Active', 'Resilience and Sustainability Facility', 'IMF · Third review completed 24 July 2025', '$71M', 'The third review made about $71 million available for Cameroon’s climate agenda.', ['IMF'], IMF_CMR_8),
                     R('private', 'Active', 'Kribi refinery', 'Public-private partnership', 'XAF 540bn', 'A refinery partnership of about $882 million, carried in the public debt report.', ['Government of Cameroon'], FA_CMR_DEBT)],
        'newswire': [W('2026-10-01', 'IMF Staff Concludes Post-Financing Assessment Discussions with Cameroon', IMF_CMR_PFA, 'IMF'),
                     W('2026-08-02', 'By June 30, 2026, Cameroon experiences a growth of 3.7% with the IMF in sight for 2027', FA_CMR_GR, 'Financial Afrik', '3.7%')],
        'assets': ['forest', 'grid', 'water', 'farmland', 'people'],
        'forest_text': 'Part of the Congo Basin, the second lung of the planet: carbon and timber that can earn as they stand.',
        'grid_text': 'Rivers already give two thirds of the power; every new connection can be clean.',
        'letter': 'You hold part of the Congo Basin forest, rivers that already light two thirds of your grid, and a young nation of nearly thirty million. Your debt is sustainable but costly. Let the forest and the rivers carry cheaper capital than the market now offers you.',
        'quote': 'Your forest stores the world’s carbon. Let the world pay for it in cheaper capital.',
        'sources': [WDI, STD, 'IMF, PR 25/59 (March 2025), PR 25/265 (24 July 2025) and PR 26/314 (1 October 2026).', 'Financial Afrik, CAA monthly public debt report to end June 2026; Capmad, Ministry of Finance figure to 31 March 2026.'],
        'gaps': ['Public debt figures are read in Financial Afrik and Capmad, citing the CAA and the Ministry of Finance; the CAA report itself is to be linked.'],
    },
    {
        'slug': 'central-african-republic', 'name': 'Central African Republic', 'iso3': 'CAF', 'iso2': 'CF', 'ne': 'Central African Republic',
        'demonym': 'Central Africans', 'of_people': 'Central Africans', 'gov': 'the Central African Republic', 'steward': 'Grâce Yakité',
        'lead': 'A nation of 5.5 million with forest over seven tenths of its land and nearly all its power from water, rebuilding its public finances with the IMF.',
        'stats': [{'value': '72.5%', 'label': 'Of the land under forest, 2024'}, {'value': '96.5%', 'label': 'Electricity from renewable sources, 2021'},
                  {'value': '$197M', 'label': 'IMF Extended Credit Facility, approved 2023'}],
        'cap_heading': 'Forest and water, waiting for capital.',
        'record': [C('$197M', 'IMF Extended Credit Facility, approved April 2023; $58 million disbursed in June 2025', 'IMF, 2025', IMF_CAF),
                   C('57.4%', 'Public sector debt, share of GDP, projected for 2025, from 60.7% in 2024', 'IMF, 2025', IMF_CAF_CR, False),
                   C('9.1%', 'Domestic revenue, share of GDP, 2024', 'IMF, 2025', IMF_CAF_CR, False)],
        'register': [R('multi', 'Active', 'Extended Credit Facility', 'IMF · Approved April 2023 · Extension requested April 2026', '$197M', 'Third and fourth reviews completed 4 June 2025, with $58 million disbursed.', ['IMF'], IMF_CAF)],
        'newswire': [W('2026-04-17', 'Central African Republic asks the IMF for more time to complete its programme', FA_CAF, 'Financial Afrik')],
        'assets': ['forest', 'grid', 'water', 'ground', 'people'],
        'forest_text': 'One of Africa’s great forests: carbon, timber and biodiversity that can earn while they stand.',
        'grid_text': 'Almost all the power that flows comes from water; the task is to bring it to the four in five still without it.',
        'letter': 'You hold forest over seven tenths of your land, rivers that give almost all your power, and more fresh water per person than most nations on earth. Almost half of you are children. The task is to turn what stands and flows into services that reach every one of them.',
        'quote': 'What stands and what flows can feed and teach every child. Let the forest and the rivers pay.',
        'sources': [WDI, STD, 'IMF, PR 25/179, 4 June 2025; IMF Country Report 25/140.', 'Financial Afrik: request for more time, 17 April 2026.'],
        'gaps': ['Food insecurity figure dates from 2022.', 'Learning outcomes not measured; lower-secondary completion (2016) used.', 'The Newswire title is a summary of the Financial Afrik article; to be replaced by its exact title at the weekly review.'],
    },
    {
        'slug': 'chad', 'name': 'Chad', 'iso3': 'TCD', 'iso2': 'TD', 'ne': 'Chad', 'demonym': 'Chadians', 'of_people': 'Chadians',
        'steward': 'Achta Mahamat',
        'lead': 'A nation of 21 million where oil supplied 51.8% of government revenue in 2024 and rain-fed farming about 40% of GDP, now under a new four-year IMF programme.',
        'stats': [{'value': '$625M', 'label': 'IMF Extended Credit Facility, July 2025'}, {'value': '€110M', 'label': 'Afreximbank facility, its largest for Chad'},
                  {'value': '13.4%', 'label': 'Of citizens with electricity, 2024'}],
        'cap_heading': 'Oil income, a new IMF programme, and a nation without power.',
        'record': [C('$625M', 'IMF Extended Credit Facility, 48 months, approved 25 July 2025; access of SDR 455.65 million', 'IMF, 2025', IMF_TCD),
                   C('€110M', 'Afreximbank financing in local currency, the bank’s largest for Chad', 'EA Business Times, 2026', AFX_TCD),
                   C('51.8%', 'Share of government revenue from oil, 2024 (World Bank)', 'Rio Times, 2026', RT_TCD, False)],
        'register': [R('multi', 'Active', 'Extended Credit Facility', 'IMF · Approved 25 July 2025 · 48 months', '$625M', 'Staff-level agreement on the first review reached in December 2025.', ['IMF'], IMF_TCD),
                     R('regional', 'Signed', 'Afreximbank local-currency facility', 'Afreximbank', '€110M', 'Financing for the national development agenda, the largest the bank has extended to Chad.', ['Afreximbank'], AFX_TCD)],
        'newswire': [W('2025-12-19', 'IMF Staff Reaches Agreement with Chadian Authorities on the First Review under the ECF', IMF_TCD_SLA, 'IMF')],
        'assets': [dict(name='The Oil', figure='65.3%', money=False, label='Of exports from oil, 2024', text='Oil already earns most of what Chad sells abroad; the task is to turn it into power and schools at home.', src='World Bank figures via Rio Times, 2026'),
                   'farmland', 'land', 'water', 'people'],
        'farm_text': 'Rain-fed farms and herds that carry four in ten of every dollar the nation earns.',
        'letter': 'Oil carries your budget and your exports, yet one in eight of you has electricity. Your farms and herds carry most families. Almost half of you are children. Let the oil buy the power, the water and the schools that will outlast it.',
        'quote': 'Oil can light a nation once. Let it pay for the grid that lights it for good.',
        'sources': [WDI, STD, 'IMF, PR 25/269, 25 July 2025; PR 25/437, 19 December 2025.', 'EA Business Times: Afreximbank EUR 110 million facility. Rio Times, World Bank figures on oil, 2026.'],
        'gaps': ['Oil shares of revenue and exports are read in Rio Times, citing the World Bank; the World Bank Macro Poverty Outlook is to be linked.', 'Public debt in % of GDP: IMF table read; latest figure to confirm.'],
    },
]
