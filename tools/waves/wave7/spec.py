"""Wave 7 of the remaining blueprints (11 November 2026): Central and Eastern Europe, 19 nations. First editions.
The figures in the words come from tools/waves/common/wb_raw.txt and notes.md in this folder. Strings in record and
stats name the automatic lines in tools/waves/common/gen.py: debt and growth (IMF, WEO October 2026), remit and
tourism (World Bank)."""

WAVE = 'wave 7, Central and Eastern Europe'


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


def PROJ(pid):
    return 'https://projects.worldbank.org/en/projects-operations/project-detail/%s' % pid


def WBP(name, pid, date, amount, text):
    return R('multi', 'Approved', name, 'World Bank · Approved %s' % date, amount, text, ['World Bank'], PROJ(pid))


COUNCIL = 'https://www.consilium.europa.eu/en/policies/eu-recovery-plan/timeline/'


def RRF(amount, date, kind='grants and loans'):
    return R('regional', 'Approved', 'Recovery and resilience plan', 'Council of the EU · Approved %s · EU Recovery and Resilience Facility' % date, amount,
             'EU funding, in %s, for agreed reforms and investments.' % kind, ['European Union'], COUNCIL)


def RRFC(amount, date, kind='grants and loans'):
    return C(amount, 'Recovery and resilience plan (%s), as approved by the Council of the EU on %s' % (kind, date), 'Council of the EU, %s' % date[-4:], COUNCIL)


WB_GP = 'https://webalkans.eu/en/growth-plan-for-the-western-balkans-progress-is-being-made-but-at-different-speeds/'
EWB = 'https://europeanwesternbalkans.com/2026/05/20/commission-releases-158-9-million-euros-to-albania-montenegro-and-north-macedonia/'


def GP(amount, approved, text):
    return R('regional', 'Disbursing', 'Reform and Growth Facility (EU Growth Plan)', 'European Commission · Reform Agenda approved %s' % approved, amount,
             text, ['European Union'], WB_GP, note='€6 billion in all for the Western Balkans: €2 billion in grants, €4 billion in loans')


def GPC(alloc, received):
    return [C(alloc, 'Preliminary allocation under the EU Reform and Growth Facility for the Western Balkans, 2024-2027', 'WeBalkans (EU), 2026', WB_GP),
            C(received, 'Received under the Growth Plan by August 2026', 'WeBalkans (EU), 2026', WB_GP)]


EC_MD = 'https://enlargement.ec.europa.eu/funding-technical-assistance/reform-and-growth-facility-moldova_en'
LOV_MD = 'https://www.lovguiden.dk/en/det-offentlige/europa-kommissionen-press-corner/2026-10-05-eu-udbetaler-157-mio-euro-til-moldova-under-vaekstplanen'
EEAS_MD = 'https://www.eeas.europa.eu/delegations/moldova/first-meeting-eu-moldova-monitoring-committee-reform-and-growth-facility_en'
MEI_RS = 'https://www.mei.gov.rs/eng/news/2430/more/w/0/serbia-receives-first-56-5-million-euros-from-eu-growth-plan/'
IEU_PL = 'https://ieu-monitoring.com/?p=1251187'
RO_BF = 'https://businessforum.ro/finance/20260310/romania-raises-eur47-billion-in-international-bond-issue-2964'
RO_NOV = 'https://www.romania-insider.com/business/romania-issues-eur-45-bln-eurobonds-borrowing-cost'
TASS = 'https://tass.com/economy/2198899'

PRESS = 'The Growth Plan allocation and receipts are read in WeBalkans, the EU’s regional portal; to cite the Commission scoreboard.'


NATIONS = [
    {
        'slug': 'albania', 'demonym': 'Albanians', 'steward': 'Elira Dervishi',
        'lead': 'A nation of 2.3 million on the Adriatic whose power is almost all renewable, with €922.1 million earmarked under the EU Growth Plan and €212.8 million already received.',
        'stats': [{'value': '€922.1M', 'label': 'EU Growth Plan allocation, 2024-2027'}, 'growth', 'remit'],
        'cap_heading': 'Paid for every reform, and food for every table.',
        'record': GPC('€922.1M', '€212.8M') + ['growth', 'debt'],
        'register': [GP('€922.1M', 'October 2024', 'Grants and concessional loans paid against reforms; €49 million was released on 20 May 2026.'),
                     WBP('First Resilience and Green Development DPL', 'P178202', '16 March 2023', '$120M', 'Budget support for resilience and green growth.'),
                     WBP('Clean and Resilient Environment for Blue Sea', 'P176163', '1 December 2023', '$80M', 'Cleaner coasts and waters.')],
        'newswire': [W('2026-05-20', 'Commission releases 158.9 million euros to Albania, Montenegro and North Macedonia', EWB, 'European Western Balkans')],
        'assets': ['grid', 'visitors', 'diaspora', 'farmland', 'people'],
        'letter': 'Almost all your electricity is renewable, visitors and Albanians abroad bring in steady income, and the EU pays you for every reform you complete. Yet 33% of you are moderately or severely food insecure. Let the farms and the coast that feed your visitors feed every Albanian family.',
        'quote': 'Let the farms and the coast feed every family.',
        'sources': ['WeBalkans (EU), 6 August 2026; European Western Balkans, 20 May 2026.', 'World Bank projects P178202 and P176163.'],
        'gaps': [PRESS, 'The tourism share dates from 2020, a pandemic year.'],
    },
    {
        'slug': 'belarus', 'demonym': 'Belarusians', 'steward': 'Alesia Kavalenka',
        'lead': 'A nation of 9.1 million with forest across four tenths of its land, where power, clean fuel and schooling reach every home and public debt is 31.3% of GDP.',
        'stats': ['debt', 'growth', {'value': '9.1m', 'label': 'People, 2025'}],
        'cap_heading': 'Capital still to be drawn.',
        'record': ['debt', 'growth', 'remit'],
        'register': [],
        'newswire': [],
        'assets': ['forest', 'farmland', 'people', 'water', 'land'],
        'letter': 'Your forests cover four tenths of your land, and power, clean fuel and schooling reach every home. Almost none of you is food insecure. Yet by the strict international measure, 25.6% of you lack safely managed sanitation. Let every home have sanitation as reliable as its power.',
        'quote': 'Sanitation as reliable as the power in every home.',
        'sources': [],
        'gaps': ['No capital already committed and no Newswire item on record yet.'],
    },
    {
        'slug': 'bosnia-and-herzegovina', 'demonym': 'Bosnians and Herzegovinians', 'of_people': 'people in Bosnia and Herzegovina',
        'people_word': 'the people of Bosnia and Herzegovina', 'steward': 'Amra Hadžić',
        'lead': 'A nation of 3.1 million with forest across four tenths of its land, where citizens abroad send home a tenth of the economy and the EU has earmarked €976.6 million under its Growth Plan.',
        'stats': [{'value': '€976.6M', 'label': 'EU Growth Plan allocation'}, 'remit', 'debt'],
        'cap_heading': 'A Growth Plan waiting to pay, and sanitation to build.',
        'record': [C('€976.6M', 'Allocation under the EU Reform and Growth Facility, reduced by 10% after the Reform Agenda was finalised last in the region', 'WeBalkans (EU), 2026', WB_GP),
                   C('$100M', 'Health Sectors Programmatic Development Policy Loan, March 2023', 'World Bank, 2023', PROJ('P175191')),
                   'remit', 'debt'],
        'register': [GP('€976.6M', 'November 2025', 'Grants and concessional loans paid against reforms; no payment had been made by August 2026.'),
                     WBP('Health Sectors Programmatic Development Policy Loan', 'P175191', '20 March 2023', '$100M', 'Budget support for health sector reforms.'),
                     WBP('Air Quality Improvement Project', 'P176040', '30 May 2023', '$50M', 'Cleaner air in the most polluted towns.'),
                     WBP('Sava and Drina Rivers Corridors, additional financing', 'P180507', '25 July 2023', '$40.53M', 'Flood protection along the Sava and Drina.'),
                     WBP('Geospatial Infrastructure and Valuation Enhancement (GIVE)', 'P180409', '16 May 2024', '$24.9M', 'Land registers and property valuation.')],
        'newswire': [W('2026-08-06', 'Growth Plan for the Western Balkans: Progress is being made, but at different speeds', WB_GP, 'WeBalkans')],
        'assets': ['forest', 'diaspora', 'water', 'grid', 'people'],
        'letter': 'Your forests cover four tenths of your land, four tenths of your power is renewable, and citizens abroad send home a tenth of your economy. Yet by the strict international measure, 43.4% of you lack safely managed sanitation, and a third of homes cook without clean fuel. Let the EU Growth Plan reach the pipes and treatment every home needs.',
        'quote': 'Let the Growth Plan reach the pipes every home needs.',
        'sources': ['WeBalkans (EU), 6 August 2026.', 'World Bank projects P175191, P176040, P180507 and P180409.'],
        'gaps': [PRESS, 'Urban slum data date from 2018.'],
    },
    {
        'slug': 'bulgaria', 'demonym': 'Bulgarians', 'steward': 'Desislava Petrova',
        'lead': 'A nation of 6.4 million with farmland across almost half its land, public debt of 29.9% of GDP and a €6.3 billion recovery and resilience plan.',
        'stats': ['debt', 'growth', {'value': '€6.3bn', 'label': 'EU recovery and resilience grants'}],
        'cap_heading': 'Low debt, and sanitation and incomes to build.',
        'record': [RRFC('€6.3bn', '3 May 2022', 'grants'), 'debt', 'growth'],
        'register': [RRF('€6.3bn', '3 May 2022', 'grants')],
        'newswire': [],
        'assets': ['farmland', 'forest', 'people', 'grid', 'water'],
        'letter': 'Your farmland covers almost half your land, and your public debt is 29.9% of GDP. Water, power and clean fuel reach almost every home. Yet by the strict international measure, 24.3% of you lack safely managed sanitation, and 21.2% live below the national poverty line. Let low debt finance the sanitation and the incomes every household needs.',
        'quote': 'Let low debt finance sanitation and incomes for every household.',
        'sources': ['Council of the European Union: recovery plan timeline (Bulgaria, 3 May 2022).'],
        'gaps': ['The Council figure dates from May 2022; the amended plan is to source.', 'No Newswire item with a verified date yet.'],
    },
    {
        'slug': 'croatia', 'demonym': 'Croatians', 'steward': 'Ivana Horvat',
        'lead': 'A nation of 3.9 million on the Adriatic with a €10 billion recovery and resilience plan and seven tenths of its power renewable.',
        'stats': [{'value': '€10bn', 'label': 'EU recovery and resilience plan'}, 'debt', 'growth'],
        'cap_heading': 'A coast that welcomes the world, and only treated water.',
        'record': [RRFC('€10bn', '20 June 2025'), 'debt', 'growth'],
        'register': [RRF('€10bn', '20 June 2025')],
        'newswire': [],
        'assets': ['visitors', 'grid', 'forest', 'diaspora', 'people'],
        'letter': 'Visitors come for your coast, seven tenths of your power is renewable, and the EU funds €10 billion of your reforms and investments. Yet by the strict international measure, 25.3% of you lack safely managed sanitation, and 20.3% live below the national poverty line. Let the coast that welcomes the world receive only treated water.',
        'quote': 'Let the coast receive only treated water.',
        'sources': ['Council of the European Union: recovery plan timeline (Croatia, 20 June 2025).'],
        'gaps': ['The tourism share dates from 2020, a pandemic year.', 'No Newswire item with a verified date yet.'],
    },
    {
        'slug': 'czechia', 'demonym': 'Czechs', 'steward': 'Tereza Novotná',
        'lead': 'A nation of 10.9 million at the centre of Europe, with farmland across almost half its land and a €9.2 billion recovery and resilience plan.',
        'stats': [{'value': '€9.2bn', 'label': 'EU recovery and resilience plan'}, 'debt', 'growth'],
        'cap_heading': 'Recovery funding, and every child a reader.',
        'record': [RRFC('€9.2bn', '5 November 2024'), 'debt', 'growth'],
        'register': [RRF('€9.2bn', '5 November 2024')],
        'newswire': [],
        'assets': ['farmland', 'forest', 'people', 'grid', 'water'],
        'letter': 'Your farmland covers almost half your land, your forests four tenths, and the EU funds €9.2 billion of your reforms and investments. Water, sanitation and power reach almost every home. Yet on the 2021 data, 14.2% of your children could not read a simple text by the end of primary school. Let every Czech child leave primary school a confident reader.',
        'quote': 'Let every child leave primary school a confident reader.',
        'sources': ['Council of the European Union: recovery plan timeline (Czechia, 5 November 2024).'],
        'gaps': ['No Newswire item with a verified date yet.'],
    },
    {
        'slug': 'estonia', 'demonym': 'Estonians', 'steward': 'Liis Tamm',
        'lead': 'A nation of 1.4 million on the Baltic with forest across almost six tenths of its land and public debt of 24.0% of GDP.',
        'stats': ['debt', 'growth', 'gdppc'],
        'cap_heading': 'Low debt and strong schools, and a living income for all.',
        'record': ['debt', 'growth'],
        'register': [],
        'newswire': [],
        'assets': ['forest', 'people', 'grid', 'farmland', 'water'],
        'letter': 'Your forests cover almost six tenths of your land, your public debt is 24.0% of GDP, and almost every young person completes lower secondary school. Yet 22.5% of you live below the national poverty line. Let low debt and strong schools build a living income for every household.',
        'quote': 'Let low debt and strong schools build a living income for all.',
        'sources': [],
        'gaps': ['The amount of Estonia’s recovery and resilience plan is to source.', 'No capital already committed and no Newswire item on record yet.'],
    },
    {
        'slug': 'hungary', 'demonym': 'Hungarians', 'steward': 'Réka Nagy',
        'lead': 'A nation of 9.5 million with farmland across more than half its land, where the Council of the EU approved a new recovery and resilience plan of about €10 billion in July 2026.',
        'stats': [{'value': '€10bn', 'label': 'New EU recovery and resilience plan, July 2026'}, 'debt', 'growth'],
        'cap_heading': 'Farmland, and every table full.',
        'record': [C('€10bn', 'New recovery and resilience plan of about €10 billion, about €6.5 billion in grants and €3.5 billion in loans, approved by the Council of the EU on 10 July 2026', 'Council of the EU, 2026', COUNCIL),
                   'debt', 'growth'],
        'register': [RRF('€10bn', '10 July 2026')],
        'newswire': [],
        'assets': ['farmland', 'forest', 'people', 'water', 'grid'],
        'letter': 'Your farmland covers more than half your land, and in July 2026 the EU approved a new recovery plan of about €10 billion for you. Water, sanitation and power reach almost every home. Yet 15.6% of you are moderately or severely food insecure. A nation with so much farmland can make sure every table is full.',
        'quote': 'A nation with so much farmland can keep every table full.',
        'sources': ['Council of the European Union: recovery plan timeline (Hungary, 10 July 2026).'],
        'gaps': ['No Newswire item with a verified date yet.'],
    },
    {
        'slug': 'latvia', 'demonym': 'Latvians', 'steward': 'Ilze Bērziņa',
        'lead': 'A nation of 1.8 million on the Baltic with forest across more than half its land, six tenths of its power renewable and €1.97 billion in EU recovery grants.',
        'stats': ['debt', 'growth', {'value': '€1.97bn', 'label': 'EU recovery and resilience grants'}],
        'cap_heading': 'Forests and clean power, and a living income for all.',
        'record': [RRFC('€1.97bn', '18 February 2025', 'grants'), 'debt', 'growth'],
        'register': [RRF('€1.97bn', '18 February 2025', 'grants')],
        'newswire': [],
        'assets': ['forest', 'grid', 'people', 'farmland', 'water'],
        'letter': 'Your forests cover more than half your land, six tenths of your power is renewable, and the EU funds €1.97 billion of your reforms. Yet 22.5% of you live below the national poverty line. Let the forests and the recovery grants build a living income for every household.',
        'quote': 'Let the forests build a living income for every household.',
        'sources': ['Council of the European Union: recovery plan timeline (Latvia, 18 February 2025).'],
        'gaps': ['Tourism receipts date from 2007 and are not used.', 'No Newswire item with a verified date yet.'],
    },
    {
        'slug': 'lithuania', 'demonym': 'Lithuanians', 'steward': 'Eglė Kazlauskienė',
        'lead': 'A nation of 2.9 million on the Baltic with a €3.85 billion recovery and resilience plan and two thirds of its power renewable.',
        'stats': [{'value': '€3.85bn', 'label': 'EU recovery and resilience plan'}, 'debt', 'growth'],
        'cap_heading': 'Clean power and recovery, and a living income for all.',
        'record': [C('€3.85bn', 'Recovery and resilience plan: €2.297 billion in grants and €1.551 billion in loans, as approved by the Council of the EU on 8 October 2024', 'Council of the EU, 2024', COUNCIL),
                   'debt', 'growth'],
        'register': [RRF('€3.85bn', '8 October 2024')],
        'newswire': [],
        'assets': ['grid', 'farmland', 'forest', 'people', 'water'],
        'letter': 'Two thirds of your power is renewable, and the EU funds €3.85 billion of your reforms and investments. Water, sanitation and power reach almost every home. Yet 20.9% of you live below the national poverty line. Let the recovery plan build a living income for every household.',
        'quote': 'Let the recovery build a living income for every household.',
        'sources': ['Council of the European Union: recovery plan timeline (Lithuania, 8 October 2024 and 20 June 2025).'],
        'gaps': ['Tourism receipts date from 2004 and are not used.', 'No Newswire item with a verified date yet.'],
    },
    {
        'slug': 'moldova', 'demonym': 'Moldovans', 'steward': 'Doina Rusu',
        'lead': 'A nation of 2.4 million with farmland across three quarters of its land, where the EU’s €1.9 billion Growth Plan had made €661 million available by October 2026.',
        'stats': [{'value': '€1.9bn', 'label': 'EU Growth Plan, 2025-2027'}, 'remit', 'growth'],
        'cap_heading': 'Paid for every reform, and a living income for every family.',
        'record': [C('€1.9bn', 'EU Growth Plan for Moldova: a Reform and Growth Facility for 2025-2027', 'European Commission, 2026', EC_MD),
                   C('€661M', 'Made available under the Growth Plan after the third payment of €157 million, October 2026', 'European Commission, read in Lovguiden, 2026', LOV_MD),
                   C('$105.98M', 'Rural Connectivity Project, April 2024', 'World Bank, 2024', PROJ('P180153')),
                   'remit'],
        'register': [R('regional', 'Disbursing', 'Reform and Growth Facility for Moldova', 'European Commission · 2025-2027', '€1.9bn',
                       'Grants and concessional loans paid against reforms: €189 million in March 2026 and €157 million in October 2026.', ['European Union'], EC_MD),
                     WBP('Rural Connectivity Project', 'P180153', '29 April 2024', '$105.98M', 'Roads that connect villages to markets and services.'),
                     WBP('Sustainable Transition through Energy Efficiency (STEEM)', 'P500560', '25 June 2024', '$50M', 'Lower energy bills in public buildings and homes.'),
                     WBP('Supporting Growth and Resilience DPO', 'P181479', '14 June 2024', '$40M', 'Budget support for growth and resilience reforms.'),
                     WBP('Strengthening Disaster Risk Management and Resilience', 'P504278', '5 September 2024', '$40M', 'Preparedness for floods, droughts and other disasters.')],
        'newswire': [W('2026-09-24', 'First Meeting of the EU-Moldova Monitoring Committee on the Reform and Growth Facility', EEAS_MD, 'EEAS'),
                     W('2026-03-17', 'The European Commission announces the second regular payment under the Growth Plan (€189 million)', EC_MD, 'European Commission')],
        'assets': ['farmland', 'diaspora', 'people', 'forest', 'water'],
        'letter': 'Your farmland covers three quarters of your land, Moldovans abroad send home almost a tenth of your economy, and the EU is paying you for every reform you complete. Yet 33.6% of you live below the national poverty line, and a quarter are moderately or severely food insecure. Let the farmland and the Growth Plan build a living income for every family.',
        'quote': 'Let the farmland and the Growth Plan build a living income for every family.',
        'sources': ['European Commission: Reform and Growth Facility for Moldova; EEAS, 24 September 2026.', 'World Bank projects P180153, P500560, P181479 and P504278.'],
        'gaps': ['The €661 million total is read in Lovguiden from a Commission press release of 5 October 2026; to cite the Commission directly.', 'The tourism share dates from 2020, a pandemic year.'],
    },
    {
        'slug': 'montenegro', 'demonym': 'Montenegrins', 'steward': 'Jelena Vuković',
        'lead': 'A nation of 623,000 between the mountains and the Adriatic, with forest across six tenths of its land and €383.5 million earmarked under the EU Growth Plan.',
        'stats': [{'value': '€383.5M', 'label': 'EU Growth Plan allocation, 2024-2027'}, 'debt', 'growth'],
        'cap_heading': 'Mountains, coast and reforms, and only treated water.',
        'record': GPC('€383.5M', '€91.2M') + [C('$86.6M', 'First Resilient Fiscal and Sustainable Development DPF, October 2024', 'World Bank, 2024', PROJ('P178646')), 'debt'],
        'register': [GP('€383.5M', 'October 2024', 'Grants and concessional loans paid against reforms; €44.2 million was released on 20 May 2026.'),
                     WBP('First Resilient Fiscal and Sustainable Development DPF', 'P178646', '4 October 2024', '$86.6M', 'Budget support for fiscal and sustainable development reforms.'),
                     WBP('Energy Sector Decarbonization Project', 'P505964', '4 December 2024', '$20.2M', 'Cleaner power and energy efficiency.')],
        'newswire': [W('2026-05-20', 'Commission releases 158.9 million euros to Albania, Montenegro and North Macedonia', EWB, 'European Western Balkans')],
        'assets': ['forest', 'grid', 'visitors', 'diaspora', 'people'],
        'letter': 'Your forests cover six tenths of your land, six tenths of your power is renewable, and the EU pays you for every reform you complete. Yet by the strict international measure, 49.1% of you lack safely managed sanitation, and a quarter of homes cook without clean fuel. Let the coast and the mountains receive only treated water.',
        'quote': 'Let the coast and the mountains receive only treated water.',
        'sources': ['WeBalkans (EU), 6 August 2026; European Western Balkans, 20 May 2026.', 'World Bank projects P178646 and P505964.'],
        'gaps': [PRESS, 'The Commission put Montenegro’s receipts at €89.3 million on 20 May 2026; WeBalkans gives €91.2 million in August 2026.', 'The tourism share dates from 2020, a pandemic year.'],
    },
    {
        'slug': 'north-macedonia', 'demonym': 'citizens of North Macedonia', 'of_people': 'people in North Macedonia', 'people_word': 'the people of North Macedonia',
        'steward': 'Marija Stojanovska',
        'lead': 'A nation of 1.8 million in the Balkans, with €750.4 million earmarked under the EU Growth Plan and €142.1 million already received.',
        'stats': [{'value': '€750.4M', 'label': 'EU Growth Plan allocation, 2024-2027'}, 'growth', 'debt'],
        'cap_heading': 'Paid for every reform, and treatment for every town.',
        'record': GPC('€750.4M', '€142.1M') + [C('$100M', 'Sustainability and Resilience Development Policy Operation, December 2023', 'World Bank, 2023', PROJ('P180587')), 'debt'],
        'register': [GP('€750.4M', 'October 2024', 'Grants and concessional loans paid against reforms; €65.7 million was released on 20 May 2026.'),
                     WBP('Sustainability and Resilience DPO', 'P180587', '15 December 2023', '$100M', 'Budget support for sustainability and resilience reforms.'),
                     WBP('Road Upgrading and Development Project', 'P181422', '18 January 2024', '$33.8M', 'Safer, better roads.'),
                     WBP('Second Social Services Improvement Project', 'P180350', '16 January 2024', '$30M', 'Social services for families in need.')],
        'newswire': [W('2026-05-20', 'Commission releases 158.9 million euros to Albania, Montenegro and North Macedonia', EWB, 'European Western Balkans')],
        'assets': ['farmland', 'forest', 'people', 'grid', 'water'],
        'letter': 'Your farmland covers half your land, and the EU pays you for every reform you complete, €142.1 million so far. Yet by the strict international measure, 87.9% of you lack safely managed sanitation, and on the 2021 data a third of your children could not read a simple text by the end of primary school. Let the Growth Plan build the treatment plants and the classrooms every community needs.',
        'quote': 'Build the treatment plants and the classrooms every community needs.',
        'sources': ['WeBalkans (EU), 6 August 2026; European Western Balkans, 20 May 2026.', 'World Bank projects P180587, P181422 and P180350.'],
        'gaps': [PRESS, 'The safely managed sanitation figure (12.1%) reflects limited wastewater treatment; to confirm with the JMP country file.', 'No tourism receipts figure is published.'],
    },
    {
        'slug': 'poland', 'demonym': 'Poles', 'of_people': 'people in Poland', 'steward': 'Zofia Kowalska',
        'skip': ['SE.SEC.CMPT.LO.ZS'],
        'lead': 'A nation of 36.4 million with farmland across almost half its land, where the EU’s recovery funding for Poland totals €54.72 billion and the IMF projects growth of 3.4% this year.',
        'stats': [{'value': '€54.72bn', 'label': 'EU recovery and resilience allocation'}, 'growth', 'debt'],
        'cap_heading': 'Growth and recovery, and every household above the line.',
        'record': [C('€54.72bn', 'Recovery and resilience allocation: €25.28 billion in grants and €29.44 billion in loans; 77% received by October 2026', 'European Commission, read in IEU Monitoring, 2026', IEU_PL),
                   'growth', 'debt'],
        'register': [R('regional', 'Disbursing', 'Recovery and resilience plan', 'European Commission · Fifth payment, 1 October 2026', '€54.72bn',
                       'EU Recovery and Resilience Facility funding in grants and loans; 77% received by October 2026.', ['European Union'], IEU_PL)],
        'newswire': [],
        'assets': ['farmland', 'forest', 'people', 'water', 'grid'],
        'letter': 'Your farmland covers almost half your land, your economy is growing by 3.4% this year, and the EU funds €54.72 billion of your reforms and investments. Water, sanitation and power reach almost every home. Yet 13.5% of you live below the national poverty line. Let growth and recovery lift every household above the line.',
        'quote': 'Let growth and recovery lift every household above the line.',
        'sources': ['European Commission press release of 1 October 2026 (read in IEU Monitoring); Council of the European Union recovery plan timeline.'],
        'gaps': ['ASSUMPTION: the World Bank lower-secondary completion rate for Poland (55.0%, 2024) is left out of the Education standard, because the 2017 school reform changed how completion is counted. Decision for the Steward-General.',
                 'The €54.72 billion allocation is read in IEU Monitoring from a Commission press release; the Council timeline gives almost €60 billion (June 2025).', 'No Newswire item with a verified date yet.'],
    },
    {
        'slug': 'romania', 'demonym': 'Romanians', 'steward': 'Ioana Popescu',
        'lead': 'A nation of 19.0 million with farmland across more than half its land, which raised about €4.7 billion on international markets in February 2026 and about €4.5 billion more in November.',
        'stats': [{'value': '€4.7bn', 'label': 'Eurobonds sold, February 2026'}, 'debt', 'growth'],
        'cap_heading': 'Investors at the door, and every young person in school.',
        'record': [C('€4.7bn', 'Eurobonds issued on 25 February 2026: €2.25 billion due 2033, $2 billion due 2036 and a €750 million reopening due 2044; demand above €15.5 billion', 'Ministry of Finance of Romania, read in Business Forum, 2026', RO_BF),
                   C('€4.5bn', 'Eurobonds issued on 2 November 2026, including a 12-year green bond', 'Ministry of Finance of Romania, read in Romania Insider, 2026', RO_NOV),
                   'debt', 'growth'],
        'register': [R('govt', 'Issued', 'Eurobonds, November 2026', 'Ministry of Finance · 2 November 2026', '€4.5bn', '4-year and 8-year bonds and a 12-year green bond.', ['Romania'], RO_NOV),
                     R('govt', 'Issued', 'Eurobonds, February 2026', 'Ministry of Finance · 25 February 2026', '€4.7bn', 'Three tranches in euros and dollars, with demand above €15.5 billion.', ['Romania'], RO_BF)],
        'newswire': [W('2026-03-10', 'Romania raises €4.7 billion in international bond issue', RO_BF, 'Business Forum')],
        'assets': ['farmland', 'forest', 'grid', 'people', 'water'],
        'letter': 'Your farmland covers more than half your land, and investors offered more than €15.5 billion for your bonds in February 2026. Power and clean fuel reach almost every home. Yet 22% of your young people do not complete lower secondary school, and the IMF projects the economy to shrink by 0.5% this year. Let the capital you raise keep every young Romanian in school.',
        'quote': 'Let the capital you raise keep every young person in school.',
        'sources': ['Ministry of Finance of Romania: Eurobond issues of February and November 2026, read in Business Forum and Romania Insider.'],
        'gaps': ['The Eurobond figures are read in Business Forum and Romania Insider from Ministry of Finance releases; to cite the Ministry directly.', 'The amount of Romania’s recovery and resilience plan is to source.'],
    },
    {
        'slug': 'russia', 'demonym': 'Russians', 'of_people': 'people in Russia', 'steward': 'Anna Smirnova',
        'gov': 'the Government of the Russian Federation',
        'lead': 'A nation of 143.5 million with forest across half its land and oil and gas rents of 15.6% of GDP, whose National Wealth Fund held 12.985 trillion roubles on 1 October 2026.',
        'stats': ['debt', 'growth', {'value': 'RUB 12.985tn', 'label': 'National Wealth Fund, 1 October 2026'}],
        'cap_heading': 'A wealth fund, and safe water for every home.',
        'record': [C('RUB 12.985tn', 'National Wealth Fund on 1 October 2026, 5.5% of projected GDP; liquid assets of RUB 3.8 trillion', 'Ministry of Finance of Russia, read in TASS, 2026', TASS, money=False),
                   'debt', 'growth'],
        'register': [R('govt', 'Held', 'National Wealth Fund', 'Ministry of Finance of the Russian Federation · 1 October 2026', 'RUB 12.985tn',
                       'A fiscal fund built from oil and gas revenue; its liquid part is held in yuan and gold at the Bank of Russia.', ['Russian Federation'], TASS, money=False)],
        'newswire': [W('2026-10-07', 'Russia’s National Wealth Fund totals $151.85 bln as of October 1', TASS, 'TASS')],
        'assets': ['oilgas', 'forest', 'water', 'land', 'minerals'],
        'letter': 'Your land holds forest across half its area, oil, gas and minerals, and fresh water on a continental scale. Food, power, schooling and incomes reach almost every home. Yet by the strict international measure, 41.8% of you lack safely managed sanitation, and almost a quarter lack safely managed drinking water. Let the wealth of the land bring safe water and sanitation to every home.',
        'quote': 'Let the wealth of the land bring safe water to every home.',
        'sources': ['Ministry of Finance of the Russian Federation: National Wealth Fund, 1 October 2026, read in TASS.'],
        'gaps': ['The National Wealth Fund figures are read in TASS from the Ministry of Finance website; to cite minfin.gov.ru directly.'],
    },
    {
        'slug': 'serbia', 'demonym': 'Serbians', 'of_people': 'people in Serbia', 'steward': 'Milica Jovanović',
        'lead': 'A nation of 6.5 million with €1.59 billion earmarked under the EU Growth Plan, the largest envelope in the Western Balkans, and growth of 3.3% projected this year.',
        'stats': [{'value': '€1.59bn', 'label': 'EU Growth Plan allocation, 2024-2027'}, 'growth', 'debt'],
        'cap_heading': 'The largest envelope in the region, and water for every home.',
        'record': GPC('€1.59bn', '€167.5M') + ['growth', 'debt'],
        'register': [GP('€1.59bn', 'October 2024', 'Grants and concessional loans paid against reforms; a first tranche of €56.5 million was approved in January 2026.')],
        'newswire': [W('2026-01-16', 'Serbia receives first 56.5 million euros from EU Growth Plan', MEI_RS, 'Ministry of European Integration of Serbia')],
        'assets': ['farmland', 'forest', 'diaspora', 'people', 'water'],
        'letter': 'Your farmland and forests cover eight tenths of your land, and the EU has earmarked €1.59 billion for your reforms. Power and clean fuel reach nine in ten homes. Yet by the strict international measure, 75.9% of you lack safely managed sanitation, and a quarter lack safely managed drinking water. Let the Growth Plan build the water and sanitation every home needs.',
        'quote': 'Let the Growth Plan build the water and sanitation every home needs.',
        'sources': ['WeBalkans (EU), 6 August 2026; Ministry of European Integration of Serbia, 16 January 2026.'],
        'gaps': [PRESS, 'No World Bank project since 2023 appears in the World Bank projects API.'],
    },
    {
        'slug': 'slovakia', 'demonym': 'Slovaks', 'steward': 'Zuzana Kováčová',
        'lead': 'A nation of 5.4 million with forest across four tenths of its land and a €6.4 billion recovery and resilience plan.',
        'stats': [{'value': '€6.4bn', 'label': 'EU recovery and resilience plan'}, 'debt', 'growth'],
        'cap_heading': 'Recovery funding, and every child a reader.',
        'record': [RRFC('€6.4bn', '13 May 2025'), 'debt', 'growth'],
        'register': [RRF('€6.4bn', '13 May 2025')],
        'newswire': [],
        'assets': ['forest', 'farmland', 'people', 'grid', 'water'],
        'letter': 'Your forests cover four tenths of your land, and the EU funds €6.4 billion of your reforms and investments. Water, power and clean fuel reach almost every home. Yet on the 2021 data, 22.1% of your children could not read a simple text by the end of primary school. Let the recovery plan make every Slovak child a reader.',
        'quote': 'Let the recovery plan make every child a reader.',
        'sources': ['Council of the European Union: recovery plan timeline (Slovakia, 13 May 2025).'],
        'gaps': ['No Newswire item with a verified date yet.'],
    },
    {
        'slug': 'slovenia', 'demonym': 'Slovenes', 'of_people': 'people in Slovenia', 'steward': 'Nina Kovač',
        'lead': 'A nation of 2.1 million with forest across six tenths of its land, a €2.2 billion recovery and resilience plan and growth of 3.2% projected this year.',
        'stats': [{'value': '€2.2bn', 'label': 'EU recovery and resilience plan'}, 'growth', 'debt'],
        'cap_heading': 'Green and growing, and every drop treated.',
        'record': [RRFC('€2.2bn', '20 June 2025'), 'growth', 'debt'],
        'register': [RRF('€2.2bn', '20 June 2025')],
        'newswire': [],
        'assets': ['forest', 'water', 'people', 'grid', 'farmland'],
        'letter': 'Your forests cover six tenths of your land, and the EU funds €2.2 billion of your reforms and investments. Water, power and schooling reach almost every home. Yet by the strict international measure, 15.5% of you lack safely managed sanitation. Let a nation so green treat every drop it returns to its rivers.',
        'quote': 'Treat every drop returned to the rivers.',
        'sources': ['Council of the European Union: recovery plan timeline (Slovenia, 20 June 2025).'],
        'gaps': ['No Newswire item with a verified date yet.'],
    },
]
