"""Wave 1 of the full blueprints (Africa, 20 nations), researched 25 November 2026.

Brief: claude/full-blueprints-151.md (Project doc). What this adds to each data/<slug>.json:
  REGISTER   new lines for Capital already committed (capital.register), each dated and sourced
  RECORD     new lines for the record (capital.record), to reach five
  ENTERPRISES new cards for Already working in <Nation> (enterprises.items)
  PATCH      amounts filled in on lines that were already on the page (matched by the start of the name)
  GAPS       what could not be sourced, or rests on a secondary source, for stewards/<slug>.md (Open gaps)
Applied by tools/waves/full1/apply.py. Research notes: tools/waves/full1/notes.md.

World Bank lines cite the project page (projects.worldbank.org/.../project-detail/<ID>); their dates and amounts
are the Board approval date and the current commitment in the World Bank projects API (search.worldbank.org/api/v3),
read 25 November 2026. Pipeline projects (future Board dates) are left out.
"""

WBP = 'https://projects.worldbank.org/en/projects-operations/project-detail/'
WB = 'World Bank'


def R(cat, status, name, detail, amount, text, by, url, note='', tone='active'):
    m = bool(amount) and amount[0] in '$€£¥' or amount[:3] in ('XOF', 'XAF', 'SDR', 'DZD', 'Rs ', 'Rs2', 'Rs1') or amount.startswith('Rs')
    return {'cat': cat, 'status': status, 'tone': tone, 'name': name, 'detail': detail, 'amount': amount,
            'money': bool(amount) and m, 'note': note, 'text': text, 'by': list(by), 'url': url}


def W(pid, name, date, amount, text, status='Approved', cat='multi', extra=''):
    d = 'World Bank · Approved %s' % date + (' · ' + extra if extra else '')
    return R(cat, status, name, d, amount, text, [WB], WBP + pid)


def C(value, text, source, url, money=True):
    return {'value': value, 'money': money, 'text': text, 'source': source, 'url': url}


def E(standard, name, text, source, url):
    return {'standard': standard, 'name': name, 'text': text, 'source': source, 'url': url}


BOAD150 = 'https://admin.boad.org/wp-content/uploads/2026/03/COMPRESS-CA-150-1.pdf'
ISDB_BAKU = 'https://www.isdb.org/news/isdb-signs-development-financing-agreements-with-member-countries-during-the-2026-isdb-group-annual-meetings-in-baku'
FO = 'https://financesone.worldbank.org/countries/'

REGISTER, RECORD, ENTERPRISES, PATCH, GAPS, HEADING = {}, {}, {}, {}, {}, {}

# ------------------------------------------------------------------ Algeria
REGISTER['algeria'] = [
    R('regional', 'Approved', 'Shoreline Power and Arkad facility for Hassi Bir Rekaiz, Phase 2a',
      'Afreximbank · Approved June 2026 · Global revolving dual-tranche facility', '$200M',
      'Finances Arkad’s 44% share of the US$980 million engineering, procurement and construction contract for the Hassi Bir Rekaiz field, one of the largest upstream contracts in Algeria, and brings African contractors into the work.',
      ['Afreximbank', 'Shoreline Power Company', 'Arkad'],
      'https://www.zawya.com/en/press-release/africa-press-releases/afreximbank-approves-us200-million-facility-for-shoreline-to-support-algerias-energy-development-403154'),
    R('regional', 'Signed', 'Strategic Cooperation Framework, 2025 to 2027',
      'Islamic Development Bank Group · Signed in Algiers, May 2025 · IsDB, ICD, ITFC, ICIEC and ISF', '$3bn+',
      'A three-year framework for the private sector, human capital, infrastructure and Islamic finance. The IsDB Group’s chairman put the financing at more than US$3 billion over three years, with the railways first.',
      ['Islamic Development Bank Group'],
      'https://www.isdb.org/news/the-peoples-democratic-republic-of-algeria-and-isdb-group-sign-a-cooperation-framework-2025-2027',
      note='The amount is the chairman’s figure, reported by the business press; the IsDB release gives no total'),
    R('private', 'Signed', 'Baladna Algeria powdered-milk project, second package',
      'Signed 23 April 2026, Algiers · Herd, services and cattle supply · Adrar', '$635M',
      'The second package of contracts for the integrated dairy farm and powdered-milk plant in Adrar, a US$3.5 billion project with Qatar’s Baladna that aims to cut the nation’s milk imports. It serves the food standard.',
      ['Baladna Algeria', 'National Investment Fund'],
      'https://www.aps.dz/fr/economie/agriculture-et-peche/mobq7klc-signature-du-deuxieme-lot-de-contrats-de-realisation-pour-plus-de-635-millions-de-dollars'),
    R('private', 'Signed', 'Baladna Algeria powdered-milk project, first package',
      'Signed 28 July 2025, Algiers · 14 contracts · Agricultural technology and production lines', '$500M+',
      'The first fourteen contracts of the US$3.5 billion integrated milk project in the south of the country, signed with agricultural technology and equipment suppliers.',
      ['Baladna Algeria', 'Algerian Investment Promotion Agency'],
      'https://news.radioalgerie.dz/fr/node/68540'),
    R('private', 'Signed', 'Integrated phosphate project, first phase',
      'Signed 12 August 2026, Algiers · Two engineering, procurement and construction contracts · Saipem and a Chinese contractor', '',
      'Sonatrach and the Algerian fertiliser company AFC signed the first two construction contracts of the integrated phosphate project, which turns the nation’s phosphate into fertiliser for its farms and for export.',
      ['Sonatrach', 'AFC', 'Saipem'],
      'https://www.aps.dz/fr/economie/industrieenergie-et-mines/msq6iz8d-sonatrach-et-l-afc-signent-deux-contrats-avec-des-partenaires-italien-et-chinois',
      note='APS does not state the value'),
    R('private', 'Signed', 'Zemoul El Kbar hydrocarbon contract',
      '30-year exploration and development contract · Sonatrach and Eni', '$1.35bn',
      'A thirty-year contract with Italy’s Eni to develop the Zemoul El Kbar area, financed by the partners.',
      ['Sonatrach', 'Eni'],
      'https://www.enerdata.net/publications/daily-energy-news/eni-and-sonatrach-sign-us135-bn-deal-develop-hydrocarbons-algeria.html'),
    R('private', 'Signed', 'Natural gas supply to Germany',
      'Signed 16 July 2026, Berlin · Deliveries from 1 January 2027 · Sonatrach and VNG', '',
      'A new contract that expands gas deliveries to the German market from 2027; the two companies are also partners in the SoutH2 hydrogen corridor to Europe.',
      ['Sonatrach', 'VNG'],
      'https://sonatrach.com/en/sonatrach-and-the-german-company-vng-sign-contract-for-natural-gas-supply/',
      note='Sonatrach does not state the volume or value'),
]
RECORD['algeria'] = [
    C('$3.5bn', 'Baladna Algeria, the integrated powdered-milk project in Adrar; more than US$1.1 billion of contracts signed in two packages, July 2025 and April 2026',
      'APS, 2026', 'https://www.aps.dz/fr/economie/agriculture-et-peche/mobq7klc-signature-du-deuxieme-lot-de-contrats-de-realisation-pour-plus-de-635-millions-de-dollars'),
]
ENTERPRISES['algeria'] = [
    E('Food', 'Baladna Algeria', 'A dairy farm and powdered-milk plant under construction in Adrar, built with Qatar’s Baladna to cut milk imports.',
      'APS, 2026', 'https://www.aps.dz/fr/economie/agriculture-et-peche/mobq7klc-signature-du-deuxieme-lot-de-contrats-de-realisation-pour-plus-de-635-millions-de-dollars'),
]
GAPS['algeria'] = [
    'An honest short list: Algeria borrows almost nothing abroad (gross external debt 0.8% of GDP, IMF, 2026), so the development banks lend little; its capital comes from the budget, the sovereign sukuk and Sonatrach’s partners. Twelve lines, not twenty.',
    'Secondary sources: the IsDB framework figure of more than US$3 billion (business press, May 2025); Zemoul El Kbar, US$1.35 billion (Enerdata); the Afreximbank facility (APO release on Zawya).',
    'Enterprises: four found on the public record (no water, shelter, energy or education enterprise with a source).',
]

# ------------------------------------------------------------------ Benin
REGISTER['benin'] = [
    W('P513143', 'Public Resource Management for Jobs and Growth', '30 September 2026', '$70M',
      'Raises domestic revenue and makes public spending go further, so the budget can carry more of the seven standards itself.'),
    W('P510638', 'First Accelerated Economic Transformation and Jobs operation', '27 February 2026', '$200M',
      'Budget support for rules that open sectors to private investment, and for investment in people.', extra='Development policy financing'),
    W('P511454', 'Benin Youth Inclusion Project', '25 June 2025', '$41.3M',
      'Brings under-employed young people aged 15 to 30 into work and strengthens the employment and training services that serve them.'),
    W('P180579', 'Grand Nokoué Sustainable Urban Mobility Project', '20 May 2025', '$400M',
      'Safer, faster and more accessible transport along the main corridors of Cotonou and its neighbours, where most of the nation’s jobs are.'),
    W('P181259', 'Land Tenure Management Program', '30 April 2025', '$100M',
      'Builds the national cadastre and registers more land rights, so families and farmers can borrow against what they own.'),
    W('P508182', 'Gazetted Forests Management Project 2', '30 April 2025', '$80.7M',
      'Protects and manages the classified forests that store water and carbon; a further US$7 million was approved on 14 July 2026.'),
    R('regional', 'Approved', 'Ouidah–Hillacondji road, duplication',
      'BOAD · Approved at the 150th Board session, Dakar, 25 and 26 March 2026', 'XOF 30bn',
      'Doubles the Agonkanmey–Hillacondji coastal road to the Togo border to cut travel times and accidents on the main West African corridor.',
      ['West African Development Bank (BOAD)'], BOAD150),
]
RECORD['benin'] = [
    C('$400M', 'World Bank financing for urban mobility in Grand Nokoué, approved May 2025: the largest World Bank operation approved for Benin in 2025 and 2026',
      'World Bank, 2025', WBP + 'P180579'),
]
ENTERPRISES['benin'] = [
    E('Food', 'BIOPHYTO', 'Organic fertiliser and biopesticides made in Benin, in place of chemical pesticides; a €2.75 million loan from BIO in 2025.',
      'BIO, 2025', 'https://www.bio-invest.be/en/our-impact/impact-stories/how-organic-fertilizer-cultivates-sustainable-success'),
    E('Water', 'CRIPT', 'A Cotonou company founded in 2025 that designs and installs energy and water systems for farms and homes.',
      'VC4A, 2025', 'https://vc4a.com/ventures/centre-de-recherche-dinnovation-et-de-production/?lang=en'),
    E('Energy', 'Qotto', 'Solar kits for homes, paid for in instalments; US$8 million raised to grow in Benin and beyond.',
      'TechCrunch', 'https://techcrunch.com/?p=2484140'),
    E('Energy', 'AXIAN Energy', 'Four solar plants, the first developed in Benin by an independent power producer, financed with €30 million.',
      'Tech in Africa, 2026', 'https://www.techinafrica.com/?p=42364'),
    E('Livelihood', 'Vital Finance', 'Microfinance for small businesses across Benin; a €3 million loan from BIO in January 2026.',
      'BIO, 2026', 'https://www.bio-invest.be/en/investments/biophyto'),
]
GAPS['benin'] = ['Enterprises: AXIAN Energy (Tech in Africa) and Qotto (TechCrunch) rest on the business press.']

# ------------------------------------------------------------------ Burkina Faso
REGISTER['burkina-faso'] = [
    R('regional', 'Approved', 'SONABHY energy security imports',
      'BOAD · Approved at the 150th Board session, Dakar, 25 and 26 March 2026 · About 500,000 m³ of liquid and gaseous hydrocarbons', 'XOF 45bn',
      'Finances fuel and gas imports by the national hydrocarbons company, to keep power, transport and cooking gas supplied.',
      ['West African Development Bank (BOAD)', 'SONABHY'], BOAD150),
    R('regional', 'Approved', 'Ouagadougou-Donsin international airport',
      'BOAD loan · Continuation of works', 'XOF 5.9bn',
      'A further BOAD loan, about US$10.5 million, to continue building the new international airport at Donsin, north of Ouagadougou.',
      ['West African Development Bank (BOAD)'], 'https://www.financialafrik.com/en/?p=485820'),
    R('govt', 'Issued', 'Treasury bills and bonds on the regional market (UMOA-Titres)',
      'Auction of 25 March 2026 · 364-day bills and 3, 5 and 7-year bonds · To finance the 2026 budget', 'XOF 77bn',
      'One of the largest of the year’s regional auctions: XOF 76.999 billion raised from investors across the West African monetary union.',
      ['Public Treasury of Burkina Faso', 'UMOA-Titres'], 'https://fr.allafrica.com/stories/202603260574.html'),
    R('govt', 'Issued', 'Treasury bills and bonds on the regional market (UMOA-Titres)',
      'Auction of 11 February 2026 · Weighted average yields 7.18% (bills), 7.85% (3 years), 6.81% (5 years), 7.28% (7 years)', 'XOF 66bn',
      'XOF 65.999 billion raised for the 2026 budget; the bonds fall due between January 2029 and January 2033.',
      ['Public Treasury of Burkina Faso', 'UMOA-Titres'], 'https://fr.allafrica.com/stories/202602120401.html'),
]
RECORD['burkina-faso'] = [
    C('XOF 131.5bn', 'Approved for Burkina Faso by the BOAD Board on 25 and 26 March 2026: cotton inputs, the Koudougou solar plant, fuel imports and credit lines',
      'BOAD, 2026', BOAD150),
]
GAPS['burkina-faso'] = ['Secondary sources: the Donsin airport loan (Financial Afrik) and the two UMOA-Titres auctions (Burkinabè press on allAfrica); the UMOA-Titres result notices were not opened.']

# ------------------------------------------------------------------ Cabo Verde
REGISTER['cabo-verde'] = [
    W('P514336', 'Improving Connectivity and Urban Infrastructure in Cabo Verde', '17 March 2026', '$40M',
      'Roads, urban works and connections between the islands, in two IDA financings of US$30 million and US$10 million.'),
    W('P508355', 'Creating Opportunities and Reaching Results on Employment (CORRE) Program', '23 June 2026', '$15M',
      'Paid for results: more Cabo Verdeans, women and young people above all, in training and in work.'),
    W('P509177', 'Digital Cabo Verde Project', '2 May 2025', '$20M',
      'Digital public services and connectivity for an island nation, so a citizen on any island reaches the state online.'),
    W('P508181', 'Cabo Verde Human Capital Project', '29 March 2025', '$3.75M',
      'Support for health, education and social protection services.'),
]
RECORD['cabo-verde'] = [
    C('$1.08bn', 'World Bank Group commitments to Cabo Verde across 56 projects, as of 30 September 2026', 'World Bank, 2026', FO + 'Cabo%20Verde'),
    C('€147M', 'For the ports: an EIB framework loan of €114 million (2024) and an EU investment grant of €33.3 million (December 2025), the Blue Economy Sustainable Ports Facility',
      'EIB, 2026', 'https://www.eib.org/en/press/all/2026-015-eib-global-signs-eur34-million-eu-grant-to-support-sustainable-ports-in-cabo-verde-under-global-gateway'),
]
ENTERPRISES['cabo-verde'] = [
    E('Water', 'Águas de Ponta Preta', 'A Cabo Verdean water and energy company, part of the consortium investing €6.8 million to rebuild the Palmarejo solar plant in Praia.',
      'Lusa, 2025', 'https://hrportugal.sapo.pt/consorcio-internacional-para-reabilitar-parque-solar-em-cabo-verde-conta-com-empresa-portuguesa/'),
    E('Energy', 'OMCV, Luz para as Meninas', 'The Organisation of Cape Verdean Women puts solar lighting kits in tin houses on São Vicente, so girls can study after dark.',
      'UNDP', 'https://www.undp.org/acceleratorlabs/blog/luz-para-meninas-light-girls'),
    E('Health', 'NhaBex', 'Founded in 2015: queue management for health posts, banks and town halls, so people wait less for public services.',
      'Startups, 2026', 'https://startups.com.br/negocios/inovacao/cabo-verde-investe-em-talento-para-levar-startups-ao-mercado-global/'),
    E('Livelihood', 'Sintaxy', 'A software company founded in 2014 in Cabo Verde that now works for clients in the United States, Portugal and England.',
      'Startups, 2026', 'https://startups.com.br/negocios/inovacao/cabo-verde-investe-em-talento-para-levar-startups-ao-mercado-global/'),
]
GAPS['cabo-verde'] = ['Nineteen register lines: the IFC loan to Cabo Verde Airports (approved 23 October 2025) may be the line already listed as the second sustainability-linked loan, so it is not counted twice.']

# ------------------------------------------------------------------ Cameroon
REGISTER['cameroon'] = [
    W('P515198', 'Electricity Transmission and Reform Project, additional financing', '13 June 2026', '$50M',
      'EUR 43 million more for the national grid, so the power of the new dams reaches homes and factories.'),
    W('P515832', 'Enhancing Connectivity and Resilience in the Far North', '11 June 2026', '$81M',
      'Roads and services in the Far North, the region hit hardest by conflict and climate shocks.'),
    W('P510425', 'Adaptive Safety Nets and Economic Inclusion Project', '18 August 2025', '$38.6M',
      'Cash transfers and help to earn a living for the poorest households, ready to scale up when a shock strikes.'),
    R('regional', 'Approved', 'Trade finance for AFG Bank Cameroon',
      'African Development Bank Group · Approved 21 October 2026 · Credit line of up to €30M over 3.5 years and a transaction guarantee', '€40M',
      'Helps businesses, women and young people above all, import equipment for industry, agro-industry and telecommunications.',
      ['African Development Bank Group', 'AFG Bank Cameroon'],
      'https://www.afdb.org/en/news-and-events/press-releases/cameroon-african-development-bank-group-grants-97726'),
    R('regional', 'Approved', 'Transaction guarantee for CCA-Bank',
      'African Development Bank Group · Approved 1 December 2025, Abidjan', '€25M',
      'Risk cover so Crédit Communautaire d’Afrique-Bank can finance more trade for small and medium-sized enterprises.',
      ['African Development Bank Group', 'CCA-Bank'],
      'https://www.afdb.org/en/news-and-events/press-releases/cameroon-african-development-bank-group-approves-eu25-million-trade-finance-facility-enable-credit-communautaire-dafrique-bank-expand-support-smes-89211'),
    R('regional', 'Signed', 'Skills for Employability and Entrepreneurship in the Far North (CAP2E)',
      'African Development Bank Group · Loan agreements signed 29 September 2025, Yaoundé', '€136M',
      'Skills, jobs and modern infrastructure for young people in the conflict-affected Far North.',
      ['African Development Bank Group'],
      'https://www.afdb.org/en/news-and-events/press-releases/cameroon-afdb-sign-eu136-million-loan-deal-develop-skills-and-entrepreneurship-far-north-87284'),
    R('regional', 'Signed', 'Ngaoundéré–Garoua road (PAST4)',
      'African Development Bank Group · Signed 19 March 2025, Yaoundé · 246 km of the Douala–N’Djamena corridor', '€330.48M',
      'Rebuilds and widens a key section of the corridor that carries trade from the port of Douala to Chad and the Central African Republic.',
      ['African Development Bank Group'],
      'https://www.afdb.org/en/news-and-events/press-releases/cameroon-african-development-bank-group-approves-eu330-million-loan-upgrade-ngaoundere-garoua-road-improve-connectivity-and-strengthen-regional-integration-82017'),
]

# ------------------------------------------------------------------ Central African Republic
REGISTER['central-african-republic'] = [
    W('P514772', 'Local Governance and Community Resilience Project', '20 October 2026', '$25M',
      'Local councils and communities choose and build the services they need most.'),
    W('P515854', 'Emergency Food Crisis Response Project, additional financing', '10 June 2026', '$50M',
      'A second IDA grant of US$50 million, bringing the project to US$100 million, to keep farmers producing and families fed.'),
    R('regional', 'Approved', 'Regional DARES, distributed renewable energy, phase 1',
      'World Bank · Approved 22 June 2026 · Central African Republic share · With Benin, Liberia and Sierra Leone', '$55M',
      'Solar mini-grids and home systems where the grid does not reach; part of a US$200 million first phase.',
      [WB], 'https://www.worldbank.org/en/programs/africa-regional-integration'),
    R('regional', 'Approved', 'Sustainable Congo Basin Forest Economies',
      'World Bank · Approved 31 March 2026 · Central African Republic share', '$60M',
      'Jobs from standing forest: sustainable timber, non-timber products and payments for keeping the forest whole.',
      [WB], FO + 'Central%20African%20Republic'),
    W('P508925', 'Emergency Infrastructure and Connectivity Recovery Project', '22 June 2025', '$30M',
      'Reopens roads and bridges cut by conflict and floods; a further US$10 million was approved on 11 November 2025.'),
    W('P509689', 'Health Service Delivery and System Strengthening Project (SENI-Plus)', '25 June 2025', '$21M',
      'Free essential care for mothers and children and stronger health centres.'),
    W('P508180', 'Adaptive and Productive Social Safety Nets Project', '30 April 2025', '$22M',
      'Cash and work for the poorest households, linked to help to earn a living.'),
    W('P510632', 'Human Capital and Women and Girls’ Empowerment (Maïngo) Project', '25 June 2025', '$10M',
      'Keeps girls in school and opens skills and work to young women.'),
    W('P511373', 'Inclusive and Resilient Cities Project', '22 July 2025', '$9.18M',
      'Drainage, streets and services in the poorest districts of Bangui and other towns.'),
    W('P181682', 'Public Sector Digital Governance, additional financing', '21 May 2025', '$6.4M',
      'Digital systems for the state, so revenue, payroll and services work and can be checked.'),
    R('private', 'Commissioned', 'Sakaï 2 solar field, Bimbo',
      'Global South Utilities (GSU) · Partial commissioning 12 August 2026 · 15 MW first, for up to 300,000 households', '$90M',
      'A solar field south-west of Bangui financed by an Emirati investor, now feeding the grid of the national utility, ENERCA.',
      ['Global South Utilities'], 'https://www.financialafrik.com/2026/08/14/centrafrique-un-fonds-emirati-investit-90-millions-usd-pour-une-centrale-solaire/'),
]
RECORD['central-african-republic'] = [
    C('$3.15bn', 'World Bank Group commitments to the Central African Republic across 76 projects, as of 30 September 2026', 'World Bank, 2026', FO + 'Central%20African%20Republic'),
    C('$583M', 'African Development Bank portfolio in the country: 20 projects, half of it in transport and a fifth in water and sanitation (December 2025)',
      'African Development Bank, 2025', 'https://fr.allafrica.com/stories/202512170134.html'),
]
GAPS['central-african-republic'] = [
    'Secondary source: Sakaï 2, US$90 million (Financial Afrik).',
    'Enterprises: two found on the public record; the private sector is small and few firms are reported by name.',
]

# ------------------------------------------------------------------ Chad
REGISTER['chad'] = [
    W('P180915', 'Chad Connectivity and Integration Project', '18 February 2025', '$170M',
      'Roads that link farming regions to markets and Chad to its neighbours.'),
    W('P509357', 'Sahel Resiland Chad: Building Resilience through Sustainable Natural Resource Management', '26 February 2026', '$100M',
      'Restores land, water and pasture so farmers and herders can stay and earn through droughts.'),
    W('P509253', 'N’Djamena Urban Resilience Project', '31 March 2025', '$50M',
      'Drainage and flood protection for the capital, where the river floods have displaced thousands.'),
    R('regional', 'Signed', 'Basic Education Transformation Project',
      'Islamic Development Bank · Signed 19 June 2026, Baku', '$20M',
      'Part of a multi-partner programme to give every Chadian child a basic education.',
      ['Islamic Development Bank'], ISDB_BAKU),
]
RECORD['chad'] = [
    C('$170M', 'World Bank financing for roads that connect Chad’s farming regions and its neighbours, approved 18 February 2025', 'World Bank, 2025', WBP + 'P180915'),
]
GAPS['chad'] = ['Eighteen register lines. The World Bank lists a US$135 million Energy Access Scale Up Project for 24 November 2026; its approval was not confirmed, so it is not on the page.']

# ------------------------------------------------------------------ Gabon
REGISTER['gabon'] = [
    W('P177372', 'Gabon Urban Development Project (PADIG)', '11 June 2025', '$150M',
      'Climate-resilient streets, drainage and public facilities, and less flooding, in the secondary cities.'),
    R('private', 'Signed', 'Oil-backed prefinancing with Trafigura',
      'Signed 15 April 2026 · Seven years · Repaid from oil deliveries', '$1bn',
      'About XOF 610 billion to ease the budget; the World Bank notes it rests on oil deliveries, so it depends on output and prices.',
      ['Government of Gabon', 'Trafigura'],
      'https://documents1.worldbank.org/curated/en/099102526143532234/pdf/P512960-6681a191-8a38-41c7-b257-7f2ae412862a.pdf'),
    R('govt', 'Signed', 'Food sovereignty investment conventions',
      'Signed 4 May 2026, Libreville · Five conventions · Ministers of the Economy and of Agriculture', 'XOF 775bn+',
      'Five conventions worth more than XOF 775 billion, over €1.2 billion, for farms and food processing, so that more of what Gabon eats is grown and made at home.',
      ['Government of Gabon'],
      'https://gouvernement.ga/2026/05/04/souverainete-alimentaire-signature-de-cinq-5-conventions-dun-montant-global-de-plus-de-775-milliards-de-fcfa-par-les-ministres-en-charge-de-leconomie-et-de-lagriculture/'),
    R('regional', 'Signed', 'Afreximbank loan and memorandum of understanding',
      'Signed 27 June 2025, Abuja, at the Afreximbank Annual Meetings · Loan to the Ministry of Economy and Finance', '200M',
      'A loan for economic reforms, signed with a memorandum for about US$3 billion to develop the manganese value chain, the railway and energy.',
      ['Afreximbank'],
      'https://ecomatin.net/energie-minerais-infrastructures-afreximbank-et-le-gabon-signent-deux-accords-de-financement-a-hauteur-de-4-milliards',
      note='Reported as €200 million (EcoMatin) and as US$200 million (Financial Afrik); the currency is not confirmed'),
    R('regional', 'Agreed', 'Afreximbank mobilisation agreement for priority investments',
      'Agreed 17 September 2025, Libreville', 'XOF 1,800bn',
      'An agreement to mobilise about XOF 1,800 billion, close to US$3 billion, for the investments of the national development plan.',
      ['Afreximbank'],
      'https://www.gabonreview.com/le-gabon-conclut-un-accord-de-3-milliards-de-dollars-avec-afreximbank-pour-soutenir-ses-investissements-prioritaires/'),
    R('private', 'Invested', 'Airtel Mobile Money Gabon',
      'IFC · Gross exposure as of 31 July 2026', '$27.6M',
      'IFC financing for mobile money, which brings payments and savings to people without a bank account.',
      ['IFC', 'Airtel Money'], FO + 'gabon'),
]
RECORD['gabon'] = [
    C('$1bn', 'Oil-backed prefinancing with Trafigura, April 2026, seven years', 'World Bank, 2026',
      'https://documents1.worldbank.org/curated/en/099102526143532234/pdf/P512960-6681a191-8a38-41c7-b257-7f2ae412862a.pdf'),
]
ENTERPRISES['gabon'] = [
    E('Food', 'Agri-Vert', 'A centre that processes and sells farm produce, opened in February 2026 at Bambouchine, Libreville.',
      'allAfrica, 2026', 'https://fr.allafrica.com/stories/202602220064.html'),
    E('Energy', 'Solar Box Gabon', 'A Libreville company, founded in 2016, that rents and sells solar equipment.',
      'Solar Impulse Foundation', 'https://solarimpulse.com/companies/solar-box-gabon'),
    E('Education', 'Finance Solid’', 'Financial education for vulnerable people, so families can plan, save and borrow safely.',
      'allAfrica, 2026', 'https://fr.allafrica.com/stories/202606290206.html'),
    E('Livelihood', 'Airtel Money Gabon', 'Mobile money for payments and savings, backed by IFC financing of US$27.6 million.',
      'World Bank Group, 2026', FO + 'gabon'),
]
GAPS['gabon'] = [
    'An honest short list of fifteen: the World Bank has two active operations in Gabon (projects API, 25 November 2026); most capital comes from Eurobonds, the regional market and commodity prefinance.',
    'Secondary sources: the Afreximbank loan and memorandum (EcoMatin; Financial Afrik gives the loan in dollars), the mobilisation agreement (Gabonreview). The French Treasury reported an AFD–EU financing of €203 million for the Transgabonais (May 2026) that may overlap the AFD line already listed; not added.',
]

# ------------------------------------------------------------------ The Gambia
REGISTER['gambia'] = [
    W('P510637', 'Advancing Reforms for Inclusive and Sustainable Economic Growth (ARISE), first operation', '24 November 2025', '$45M',
      'Budget support for reforms in public finance, energy and the private sector.', extra='Development policy financing'),
    W('P513113', 'The Gambia Water and Sanitation Project', '25 September 2026', '$30M',
      'Safe water and sanitation for more Gambian households.'),
    W('P512353', 'The Gambia Resilience, Inclusion, Skills, and Equity Project', '14 April 2026', '$10M',
      'Skills and safety nets for the households most exposed to shocks.'),
    R('multi', 'Approved', 'Extended Credit Facility, augmentation and extension',
      'IMF · Approved 6 July 2026 · SDR 12.44 million, 20% of quota · Six-month extension of the ECF and the RSF', '$17M',
      'More IMF financing and more time for the reform programme, as the nation absorbs higher costs.',
      ['International Monetary Fund'],
      'https://www.imf.org/en/news/articles/2026/07/06/pr26239-the-gambia-imf-exec-board-concludes-2026-aiv-consult-completes-5th-rev-ecf-2nd-rev-rsf-arr'),
]
PATCH['gambia'] = [
    ('Resilience and Sustainability Facility', {'amount': '$63.55M', 'money': True}),
    ('Regional Access Increase and Sustainable Energy', {'amount': '$50M', 'money': True,
     'note': 'The Gambia’s share of a US$160 million operation with Togo (World Bank, Finances One)'}),
]
RECORD['gambia'] = [
    C('$1.73bn', 'World Bank Group commitments to The Gambia across 68 projects, as of 31 July 2026', 'World Bank, 2026', FO + 'Gambia,%20The'),
]
ENTERPRISES['gambia'] = [
    E('Food', 'Farm Fresh', 'Fresh produce from a network of about a thousand farmers, delivered to homes and shops by a tech-enabled platform.',
      'TechCabal, 2025', 'https://techcabal.com/2025/11/05/how-gambias-farm-fresh-is-evolving-into-a-tech-enabled-food-distribution-platform/'),
    E('Water', 'Bakaf Farm', 'An onion farm in Foni that irrigates with a centre-pivot system, bought with support from the World Bank’s GIRAV project.',
      'World Bank, 2024', 'https://www.worldbank.org/en/news/feature/2024/06/14/transforming-the-gambia-s-agriculture-from-subsistence-to-market-oriented-farming'),
    E('Education', 'Songhai Initiative', 'Farm training for young Gambians at Chamen, so farming becomes a career of choice.',
      'UNDP, 2026', 'https://www.undp.org/node/575346'),
    E('Livelihood', 'Startup Incubator Gambia', 'A social enterprise building the next generation of Gambian entrepreneurs.',
      'VC4A', 'https://vc4a.com/ventures/startup-incubator-gambia'),
]

# ------------------------------------------------------------------ Guinea
REGISTER['guinea'] = [
    W('P518505', 'Guinea Electricity Access Scale Up Project, Phase 2, further financing', '29 September 2026', '$27.8M',
      'More households connected to power, adding to the US$232 million second phase approved in June 2025.'),
    R('regional', 'Approved', 'Guinea–Mali 225 kV interconnection, additional financing',
      'African Development Fund · Approved 10 December 2025, Abidjan · Loan of about $22M and grant of $3.79M', '$25.79M',
      'Completes the power line that will carry Guinea’s hydropower to Mali.',
      ['African Development Fund'],
      'https://www.afdb.org/en/news-and-events/press-releases/african-development-fund-grants-guinea-nearly-26-million-additional-funding-develop-electricity-interconnection-mali-89562'),
    R('regional', 'Approved', 'Fertiliser for 45,000 smallholders (MAFDE guarantee)',
      'African Development Bank Group · Approved 8 October 2026, Abidjan · Partial credit guarantee', '$2.2M',
      'A guarantee so suppliers can sell fertiliser on credit to 45,000 small farmers, faster and cheaper.',
      ['African Development Bank Group'],
      'https://www.afdb.org/fr/news-and-events/press-releases/guinee-banque-africaine-developpement-approuve-22-97647'),
    R('private', 'Operating', 'Simandou iron ore: mines, railway and port',
      'Operations started November 2025 · First shipment December 2025 · State of Guinea holds 15%', '$11.6bn',
      'The capital needed for the southern blocks (SimFer: Rio Tinto and Chinese partners); the northern blocks, held by WCS, are additional. The 600 km railway and port are shared, with the state holding a 15% free carried stake.',
      ['Rio Tinto', 'Chalco Iron Ore Holdings', 'Winning Consortium Simandou', 'Baowu', 'Government of Guinea'],
      'https://www.miningweekly.com/article/simandou-iron-ore-project-guinea-update-2025-12-12',
      note='SimFer’s capital requirement as reported by Mining Weekly; total investment in the project is put above US$20 billion'),
]
RECORD['guinea'] = [
    C('$200bn', 'Investment the Simandou 2040 programme expects over fifteen years; the African Development Bank pledged its support in January 2026',
      'African Development Bank, 2026',
      'https://www.afdb.org/fr/news-and-events/press-releases/guinee-la-banque-africaine-de-developpement-sengage-aux-cotes-du-pays-pour-reussir-le-programme-simandou-2040-un-projet-strategique-de-developpement-90356'),
]
GAPS['guinea'] = ['Eighteen register lines. Secondary source: the Simandou capital figure (Mining Weekly); Rio Tinto confirms the first shipment and the ownership, not the figure.']

# ------------------------------------------------------------------ Liberia
REGISTER['liberia'] = [
    W('P508345', 'Liberia Forest Economy Project (LiFE-P)', '19 November 2026', '$45.4M',
      'Community forests, forest governance and an aim of 50,000 new jobs from forests that stay standing.'),
    W('P509192', 'Southeastern Corridor Road Asset Management Project', '26 June 2025', '$23M',
      'The first financing for the road to the south-east, before the further US$18 million of March 2026.'),
    W('P510360', 'Sustainable Urban and Peri-Urban Agriculture for Women Empowerment Project', '11 September 2026', '$4.73M',
      'Market gardens and income for women around Monrovia.'),
    W('P517005', 'Liberia: Rural Economic Transformation Project', '18 June 2026', '$3.6M',
      'Support for farm value chains in rural Liberia.'),
    R('regional', 'Approved', 'Fiscal Sustainability and Mining Sector Governance Support Programme, phase 1',
      'African Development Bank Group · Approved, announced 4 June 2026 · Budget support', '$16.7M',
      'Reforms that widen the fiscal space for public services and bring more of the mining revenue to the nation.',
      ['African Development Bank Group'],
      'https://www.afdb.org/en/news-and-events/press-releases/liberia-african-development-bank-approves-167-million-strengthen-fiscal-sustainability-and-mining-governance-94159'),
    R('bilat', 'Signed', 'Private Sector Development grant',
      'European Union · Grant agreement signed in Monrovia by the Minister of Finance and the EU Ambassador', '€25M',
      'A grant to build the private sector and the jobs it creates.',
      ['European Union'],
      'https://www.mfdp.gov.lr/index.php/media-center/press-release/gol-and-eu-sign-25-million-financing-agreement-to-boost-private-sector-development'),
]
PATCH['liberia'] = [
    ('Regional Distributed Access through Renewable Energy', {'amount': '$45M', 'money': True, 'note': 'Liberia’s share of the US$200 million first phase (World Bank, Finances One)'}),
]
GAPS['liberia'] = ['Seventeen register lines; the release does not date the EU grant signing (published by the Ministry of Finance in 2025).']

# ------------------------------------------------------------------ Libya
PATCH['libya'] = [
    ('Waha concessions', {'amount': '$20bn+', 'money': True, 'note': 'Foreign-financed investment over 25 years, as stated by the Prime Minister'}),
]
RECORD['libya'] = [
    C('$20bn+', 'Foreign-financed investment in the 25-year extension of the Waha concessions with TotalEnergies and ConocoPhillips, signed 24 January 2026',
      'The National, 2026', 'https://www.thenationalnews.com/business/energy/2026/01/24/libya-to-sign-20bn-deal-with-us-and-french-companies-to-boost-oil-output'),
]
GAPS['libya'] = [
    'An honest short list: with two rival governments, the development banks lend almost nothing to Libya; the capital on record is the unified budget, oil partnerships and humanitarian appeals. Memoranda of understanding (Chevron, January 2026; the Libya Energy and Economic Summit, July 2026) are not capital and are not listed.',
    'Secondary source: the Waha figure (the Prime Minister, reported by The National; TotalEnergies’ release gives North Gialo, 100,000 barrels a day).',
]

# ------------------------------------------------------------------ Mali
REGISTER['mali'] = [
    R('regional', 'Approved', 'CMDT cotton campaign 2025–2026',
      'BOAD · Approved at the 150th Board session, Dakar, 25 and 26 March 2026 · About 433,700 tonnes of seed cotton', 'XOF 25bn',
      'Finances the collection and ginning of the cotton crop, the cash income of hundreds of thousands of farm families.',
      ['West African Development Bank (BOAD)', 'CMDT'], BOAD150),
    R('govt', 'Issued', 'Treasury bills and bonds on the regional market (UMOA-Titres)',
      'Auction of 8 July 2026 · To finance the 2026 budget', 'XOF 60.3bn',
      'XOF 60.333 billion raised from investors across the West African monetary union.',
      ['Public Treasury of Mali', 'UMOA-Titres'], 'https://fr.allafrica.com/stories/202607090266.html'),
    R('govt', 'Issued', 'Treasury bills and bonds on the regional market (UMOA-Titres)',
      'Auction of 24 June 2026 · 50 billion offered · 3-year bonds at 6.00%, 5-year at 6.20%', 'XOF 55bn',
      'The second XOF 55 billion raised in June 2026 for the budget.',
      ['Public Treasury of Mali', 'UMOA-Titres'], 'https://fr.allafrica.com/stories/202606250699.html'),
]
RECORD['mali'] = [
    C('XOF 25bn', 'BOAD financing for the 2025–2026 cotton campaign, approved March 2026: about 433,700 tonnes of seed cotton collected and ginned', 'BOAD, 2026', BOAD150),
]
GAPS['mali'] = ['Secondary sources: the two UMOA-Titres auctions (Malian press on allAfrica); the UMOA-Titres result notices were not opened.']

# ------------------------------------------------------------------ Mauritania
REGISTER['mauritania'] = [
    W('P505173', 'West Africa Regional Electricity Market Program, Phase 1: Mauritania Transmission Corridor', '24 January 2025', '$465M',
      'High-voltage lines that tie Mauritania into the West African power market, so its wind and sun can be sold to its neighbours.'),
    W('P179383', 'Development of Energy Resources and Mining Sector Support (DREAM), Phase 1', '27 March 2025', '$82.5M',
      'Prepares green hydrogen, energy storage and the mining sector to grow, with private investment to follow.'),
    W('P506443', 'Mauritania Public Spending Efficiency', '3 June 2025', '$50M',
      'Makes public spending go further in health, education and social protection; US$42 million paid for results.'),
]
RECORD['mauritania'] = [
    C('$465M', 'World Bank financing for the Mauritania transmission corridor of the West Africa electricity market, approved January 2025', 'World Bank, 2025', WBP + 'P505173'),
]
GAPS['mauritania'] = ['Nineteen register lines.']

# ------------------------------------------------------------------ Mauritius
REGISTER['mauritius'] = [
    R('govt', 'Budgeted', 'Public Sector Investment Programme, 2026–27 to 2030–31',
      'Presented with the Budget 2026–27 · Five-year capital programme', 'Rs 231bn',
      'About Rs 231 billion of public investment over five years, financed by the budget, loans and lines of credit from partners and private capital; a Government Support Agreement framework now derisks private solar with batteries.',
      ['Government of Mauritius'],
      'https://mauritiusassembly.govmu.org/mauritiusassembly/wp-content/uploads/2026/06/Public-Sector-Investment-Programme-2026-2027-to-2030-2031.pdf',
      tone='annual'),
    R('regional', 'Signed', 'Technical assistance against financial crime',
      'African Development Bank · Approved 6 January 2026 · Signed 23 February 2026 · MIC-TAF grant of UA 520,000', '$713K',
      'Strengthens the policy and capacity to fight money laundering, fraud and illicit financial flows, which protects the nation’s standing as a financial centre.',
      ['African Development Bank'], 'https://mapafrica.afdb.org/en/projects/46002-P-MU-KF0-003'),
    R('regional', 'Approved', 'Link Africa-Mauritius SME Development and Access to Finance and Markets',
      'African Development Bank · Grant · With Bank One', '$1.79M',
      'Helps Mauritian small businesses find finance and markets on the African continent.',
      ['African Development Bank', 'Bank One'],
      'https://ewsdata.rightsindevelopment.org/projects/p-mu-ha0-012-link-africa-mauritius-sme-development-and-access-t/'),
    R('bilat', 'Signed', 'Credit facility agreement with State Bank of India',
      'Signed 12 March 2025, during the visit of the Prime Minister of India · Government of Mauritius as borrower', '',
      'A credit facility for the government, signed with the visit’s other agreements.',
      ['State Bank of India', 'Government of Mauritius'],
      'https://www.narendramodi.in/list-of-outcomes-visit-of-prime-minister-narendra-modi-to-mauritius', note='The amount is not stated'),
    R('multi', 'Launched', 'Mandatory energy auditing and energy efficiency',
      'Global Environment Facility · Five years, 2026 to 2031 · Implemented by the Energy Efficiency Management Office with UNDP', '',
      'Energy audits made mandatory and efficiency financed, so the island uses less imported fuel.',
      ['Global Environment Facility', 'UNDP'],
      'https://www.undp.org/mauritius-seychelles/news/mauritius-launches-5-year-project-advance-mandatory-energy-auditing-and-energy-efficiency'),
]
PATCH['mauritius'] = [
    ('Special Economic Package: grant-cum-line', {'note': 'The Export-Import Bank of India signed an INR 4,100 crore (about US$426 million) line of credit in July 2026 (TXF)'}),
]
RECORD['mauritius'] = [
    C('Rs 231bn', 'Public Sector Investment Programme, 2026–27 to 2030–31: five years of public investment', 'Government of Mauritius, 2026',
      'https://mauritiusassembly.govmu.org/mauritiusassembly/wp-content/uploads/2026/06/Public-Sector-Investment-Programme-2026-2027-to-2030-2031.pdf'),
]
GAPS['mauritius'] = [
    'An honest short list of fifteen: Mauritius is a high-income island that borrows mainly at home; the development banks lend it little. AFD and the EU are finalising Rs 6.3 billion for the water crisis (Mauritian press, November 2026); not listed until signed.',
    'The AfDB Bank One grant rests on the Early Warning System database; the AfDB page was not opened.',
]

# ------------------------------------------------------------------ Niger
REGISTER['niger'] = [
    R('regional', 'Approved', 'Energy Sector Governance and Competitiveness Support Programme, phase 2 (PAGSEC-II)',
      'African Development Bank Group · Approved 21 October 2026, Abidjan · Budget support loan', '$144.34M',
      'XOF 80 billion for reforms that widen access to energy and help the private sector grow.',
      ['African Development Bank Group'], 'https://www.afdb.org/fr/news-and-events/press-releases/niger-groupe-banque-africaine-developpement-97728'),
    R('regional', 'Disbursed', 'Energy Sector Governance and Competitiveness Support Programme, phase 1 (PAGSEC-I)',
      'African Development Fund · Approved 26 September 2025 · Fully disbursed 17 October 2025 · UA 105 million', 'XOF 81bn',
      'The first phase of the same programme, paid in full within three weeks of approval.',
      ['African Development Fund'], 'https://www.afdb.org/fr/documents/niger-programme-dappui-gouvernance-secteur-98673'),
    R('regional', 'Approved', 'Youth Agripreneurship and Technological and Financial Innovation Programme (PIDAJ)',
      'African Development Bank Group · Approved 24 April 2026, Abidjan · All eight regions', '$180.6M',
      'Five agricultural vocational high schools, an innovation centre and finance for young farmers who turn food into a business.',
      ['African Development Bank Group'],
      'https://www.afdb.org/fr/news-and-events/press-releases/niger-un-financement-de-180-millions-de-dollars-pour-soutenir-les-jeunes-agripreneurs-92876'),
    R('regional', 'Approved', 'Drinking water and sanitation for Zinder, Mirriah and nearby villages',
      'African Development Fund · Loan · Announced 7 November 2025', '$165.5M',
      'Safe water and sanitation for more than a million people in the Zinder region.',
      ['African Development Fund'],
      'https://www.afdb.org/fr/news-and-events/press-releases/niger-la-banque-africaine-de-developpement-accorde-1655-millions-de-dollars-pour-ameliorer-lacces-leau-potable-et-lassainissement-de-plus-dun-million-de-personnes-88433'),
    R('multi', 'Approved', 'Extended Credit Facility, augmentation',
      'IMF · Eighth review completed 13 March 2026 · Augmentation equal to 60% of quota', 'SDR 79M',
      'More IMF financing to meet the nation’s balance-of-payments needs.',
      ['International Monetary Fund'], 'https://www.imf.org/-/media/files/publications/cr/2026/french/1nerfa2026001.pdf'),
    R('govt', 'Issued', 'Treasury bonds on the regional market (UMOA-Titres)',
      'Auction of 23 April 2026 · 3 and 5-year bonds · XOF 35 billion offered · Due April 2029 and April 2031', 'XOF 29.6bn',
      'XOF 29.582 billion raised from investors across the West African monetary union; every bid was accepted.',
      ['Public Treasury of Niger', 'UMOA-Titres'], 'https://www.umoatitres.org/wp-content/uploads/2026/04/Annonce-au-MTP-NE-ES-23.04.2026.pdf'),
    R('govt', 'Issued', 'Treasury bills and bonds with a buyback (UMOA-Titres)',
      'Auction of 24 February 2026 · Weighted average yield 10.07% · XOF 12 billion bought back', 'XOF 37.5bn',
      'A new issue joined to the early buyback of older debt, to spread the nation’s repayments.',
      ['Public Treasury of Niger', 'UMOA-Titres'], 'https://www.umoatitres.org/wp-content/uploads/2026/02/Annonce-au-MTP-NE-EC-24.02.2026.pdf'),
]
GAPS['niger'] = ['Nineteen register lines: every active World Bank operation of 2025 and 2026 is already listed.']

# ------------------------------------------------------------------ Sierra Leone
REGISTER['sierra-leone'] = [
    R('regional', 'Approved', 'Bumbuna-1 Hydroelectric Power Station Expansion',
      'OPEC Fund · Loan · 60 MW more renewable power for Freetown', '$45M',
      'Expands the nation’s main hydropower station to serve about 1.4 million people in the capital.',
      ['OPEC Fund for International Development'],
      'https://opecfund.org/news-events/press-releases/2026/opec-fund-approves-us-645-million-for-water-security-resilient-transport-and-economic-growth'),
    W('P506745', 'Enhancing Sierra Leone Energy Access', '27 June 2025', '$14M',
      'More homes, clinics and businesses connected to electricity.'),
    W('P510536', 'Quality Essential Health Services and Systems Support Project', '25 June 2025', '$12.58M',
      'Essential care for mothers and children and a stronger health system.'),
]
PATCH['sierra-leone'] = [
    ('Regional Distributed Access through Renewable Energy', {'amount': '$60M', 'money': True, 'note': 'Sierra Leone’s share of the US$200 million first phase (World Bank, Finances One)'}),
    ('Western Africa Regional Digital Integration Program', {'amount': '$15M', 'money': True, 'note': 'Sierra Leone’s share of the US$137 million operation (World Bank, Finances One)'}),
]
RECORD['sierra-leone'] = [
    C('$3.34bn', 'World Bank Group commitments to Sierra Leone across 103 projects, as of 31 August 2026', 'World Bank, 2026', FO + 'sierra%20leone'),
]
GAPS['sierra-leone'] = ['Eighteen register lines.']

# ------------------------------------------------------------------ Sudan
REGISTER['sudan'] = [
    R('regional', 'Approved', 'Boosting Resilience of Agri-food Systems in Sudan (BOOST)',
      'African Development Bank Group · Approved 22 April 2026 · Grant · Delivered by the World Food Programme', '$86.98M',
      'More food grown and available, and agribusiness for women and young people, in a country where war has driven hunger to record levels.',
      ['African Development Bank Group', 'World Food Programme'], 'https://allafrica.com/stories/202604290715.html'),
    R('regional', 'Approved', 'Sudan Emergency Wheat Production Project II',
      'African Development Bank Group · Approved, announced 4 July 2025 · Grants · Delivered by the World Food Programme', '$93.6M',
      'Seed, fertiliser and support so farmers in the most fragile regions can grow the nation’s wheat.',
      ['African Development Bank Group', 'World Food Programme'], 'https://allafrica.com/stories/202507040608.html'),
    R('regional', 'Signed', 'Emergency water and sanitation for Port Sudan, North and South Kordofan',
      'African Development Bank and UNICEF · Signed 4 June 2026 · Three stalled water projects restructured into one', '$51M',
      'Safe water for Port Sudan, the seat of government, and for Kordofan.',
      ['African Development Bank', 'UNICEF', 'Ministry of Finance and Economic Planning'], 'https://allafrica.com/stories/202606050009.html'),
    R('multi', 'Approved', 'Emergency safety nets and health (SANAD and SHARE)',
      'World Bank (IDA) · Approved, announced 12 January 2025 · Grants to WFP, UNICEF and WHO', '$182M',
      'US$100 million of safety nets for food-insecure families and US$82 million to keep health services running, delivered by UN agencies.',
      [WB, 'World Food Programme', 'UNICEF', 'World Health Organization'],
      'https://www.worldbank.org/en/news/press-release/2025/01/12/world-bank-approves-182-million-to-enhance-health-and-safety-nets-in-afe-sudan'),
    W('P504621', 'Sudan Primary Education Emergency Support Project', '22 May 2025', '$41.9M',
      'Keeps primary schools open and children learning through the war, financed by the Global Partnership for Education.'),
    W('P515196', 'Sudan Enhancing Community Resilience Project', '24 April 2026', '$10M',
      'Services and livelihoods for communities hit by the conflict.'),
    R('humanitarian', 'Signed', 'Emergency response operations with Islamic Relief USA',
      'Islamic Development Bank · Signed 19 June 2026, Baku · Two operations of US$25 million and US$7 million', '$32M',
      'An integrated emergency response for people affected by the war.',
      ['Islamic Development Bank', 'Islamic Relief USA'], ISDB_BAKU),
]
RECORD['sudan'] = [
    C('$87M', 'African Development Bank grant for food production, approved 22 April 2026 and delivered by the World Food Programme', 'African Development Bank, 2026',
      'https://allafrica.com/stories/202604290715.html'),
    C('$182M', 'World Bank grants for safety nets and health, January 2025, delivered through WFP, UNICEF and WHO', 'World Bank, 2025',
      'https://www.worldbank.org/en/news/press-release/2025/01/12/world-bank-approves-182-million-to-enhance-health-and-safety-nets-in-afe-sudan'),
]
ENTERPRISES['sudan'] = [
    E('Food', 'Kenana Sugar Company', 'The only sugar factory that kept working through the war: about 200,000 tonnes in 2023–24 and 125,000 in 2024–25.',
      'Al Jazeera, 2025', 'https://www.aljazeera.net/ebusiness/2025/10/5/sudan-agriculture-livestock-war-losses'),
    E('Food', 'Al Teital Advance Industries', 'A Khartoum sesame-oil maker that employed 300 people before the war and is bringing its factory back.',
      'Al Jazeera, 2026', 'https://www.aljazeera.com/news/2026/11/4/sudan-factories-struggle-to-restart-after-devastating-wartime-losses'),
    E('Water', 'Practical Action', 'Repaired sixteen solar water yards and built ten more in Kassala and Gedarif: safe water for more than 20,000 families.',
      'Practical Action, 2025', 'https://practicalaction.org/?p=120569'),
    E('Livelihood', 'Bankak', 'The Bank of Khartoum’s mobile banking app: salaries, money from relatives abroad and aid payments, when cash ran out.',
      'AFP, 2025', 'https://english.ahram.org.eg/News/557834.aspx'),
]
GAPS['sudan'] = [
    'An honest short list: the war has closed about one firm in three (UNDP, April 2026) and cut most lending to the state; capital on record comes through UN agencies and grants. Nine register lines.',
    'Secondary sources: the AfDB–UNICEF water agreement (SUNA, on allAfrica). Reported but not listed: an AfDB allocation of US$379.6 million (Sudan Tribune, January 2026) and an US$83 million agriculture agreement (Sudan Tribune, August 2026).',
]

# ------------------------------------------------------------------ Togo
REGISTER['togo'] = [
    R('multi', 'Approved', 'Sustainable Agricultural Transformation Program (ProMAT, phase 1)',
      'World Bank and IFC · Approved 11 June 2025 · First phase of the Agricultural Modernization Program 2025–2034', '$300M',
      'Makes Togo a regional hub for agribusiness and animal feed, led jointly by the World Bank and IFC.',
      [WB, 'IFC'], 'https://www.worldbank.org/en/news/press-release/2025/06/11/positioning-togo-as-a-regional-hub-in-agribusiness-and-animal-nutrition'),
    R('regional', 'Approved', 'Label d’Or shea processing',
      'BOAD · Approved at the 150th Board session, Dakar, 25 and 26 March 2026', 'XOF 6bn',
      'Modernises shea processing at Label d’Or, which buys from 33,000 women.',
      ['West African Development Bank (BOAD)', 'Label d’Or SA'], BOAD150),
]

# ------------------------------------------------------------------ Tunisia: already above the standard (21 lines, 5 record, 5 enterprises)
