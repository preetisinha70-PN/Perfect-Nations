from spec_a import R, C, W, WDI, STD

IMF_MUS = 'https://www.imf.org/en/news/articles/2026/07/15/pr26246-mauritius-imf-executive-board-concludes-2026-article-iv-consultation'
PWC_MUS = 'https://www.pwc.com/mu/en/events/budget/public-finance.html'
AA_MUS = 'https://allafrica.com/stories/202607010295.html'
CAP_MUS = 'https://www.capmad.com/post/imf-presses-mauritius-to-cut-public-debt-and-give-teeth-to-its-reform-plan'

IMF_NER = 'https://www.imf.org/en/news/articles/2026/07/29/pr26270-niger-imf-completes-9th-review-under-ecf-arrangement'
RT_NER = 'https://www.riotimesonline.com/imf-and-niger-agree-on-us203-million-plan/'
WB_NER = 'https://worldbank.org/ext/en/country/niger'
COF_NER = 'https://www.coface.com/news-economy-and-insights/business-risk-dashboard/country-risk-files/niger'

IMF_SLE = 'https://www.imf.org/-/media/files/publications/cr/2026/english/1sleea2026002.pdf'
IMF_SLE_ECF = 'https://www.imf.org/en/news/articles/2024/11/22/pr-24432-sierra-leone-imf-concludes-2024-aiv-consultation-approves-req-38-month-arr-under-ecf'
IMF_SLE_12 = 'https://www.imf.org/en/news/articles/2025/12/16/pr-25425-sierra-leone-imf-completes-1st-and-2nd-reviews-arrangement-under-ecf'
PM_SLE = 'https://www.premiermedia-sl.com/?p=27063'
CGTN_SLE = 'https://newsaf.cgtn.com/news/2026-06-19/IMF-approves-funds-for-climate-resilience-programme-for-Sierra-Leone-1O6zdRuWfS0/share_amp.html'
WARDIP = 'https://allafrica.com/stories/202603120094.html'

WFP_SDN = 'https://www.wfp.org/news/joint-news-release-wfpfaounicef-risk-famine-persists-nearly-195-million-people-face-acute-food'
OCHA_SDN = 'https://humanitarianaction.info/plan/1514/document/sudan-humanitarian-needs-and-response-plan-2026/article/23-cost-response'
ST_SDN = 'https://sudantribune.com/?p=319889'
WFP_SDN_E = 'https://www.wfp.org/emergencies/sudan'

WB_TGO = 'https://www.worldbank.org/en/news/press-release/2026/06/16/strengthening-togo-s-logistics-competitiveness-by-modernizing-its-transport-infrastructure'
AIIB_TGO = 'https://www.aiib.org/en/projects/details/2026/_download/Republic_of_Togo/Togo-Transport-Connectivity-and-Logistics-Improvement-Project.pdf'
LA_TGO = 'https://logistafrica.com/en/logistic/togo-world-bank-commits-us200-million-to-modernize-logistics-and-transport-systems/'
IMF_TGO = 'https://www.imf.org/en/News/Articles/2025/06/30/pr25229-togo-imf-completes-the-second-review-under-the-ecf-arrangement-for-togo'
IMF_TGO_SLA = 'https://www.imf.org/en/news/articles/2026/05/21/pr26167-togo-imf-reaches-sla-with-togo-on-the-combined-3rd-and-4th-reviews-under-ecf-arrangement'
TF_TGO = 'https://www.togofirst.com/en/transport/2306-19331-togo-secures-200-million-world-bank-financing-to-modernize-road-and-rail-transport'
WB_COSO = 'https://www.worldbank.org/en/news/press-release/2026/06/25/world-bank-scales-up-support-to-boost-jobs-and-resilience-in-northern-gulf-of-guinea'

WB_TUN = 'https://thedocs.worldbank.org/en/doc/65cf93926fdb3ea23b72f277fc249a72-0500042021/related/mpo-tun.pdf'
TXF_TUN = 'https://www.txfnews.com/news/74157/afreximbank-signs-500m-term-loan-with-central-bank-of-tunisia'
LP_TUN = 'https://www.lapresse.tn/2026/07/31/pret-afreximbank-un-taux-ramene-de-9-a-586-apres-negociations/'
FA_TUN = 'https://www.financialafrik.com/en/2026/06/11/tunisia-500-million-loan-from-afreximbank-approved/'
ENT_TUN = 'https://enterpriseam.com/menaplus/2026/11/02/tunisia-is-funding-a-32-bigger-deficit-next-year-by-leaning-harder-on-domestic-borrowing-crowding-out-smes/'

NATIONS = [
    {
        'slug': 'mauritius', 'name': 'Mauritius', 'iso3': 'MUS', 'iso2': 'MU', 'ne': None, 'small': True, 'latlng': (-20.25, 57.55),
        'demonym': 'Mauritians', 'of_people': 'Mauritians', 'steward': 'Priya Ramdin',
        'lead': 'An island nation of 1.24 million with $10.3 billion of reserves, which has set itself a legal anchor to bring public debt of 87.8% of GDP down to 75% by 2030.',
        'stats': [{'value': '$10.3bn', 'label': 'Gross international reserves, 2025'}, {'value': '87.8%', 'label': 'Public sector debt, share of GDP, 2025/26'},
                  {'value': '3.7%', 'label': 'Budget deficit target, 2026/27'}],
        'cap_heading': 'Rich in reserves, heavy in debt, anchored by law.',
        'record': [C('$10.3bn', 'Gross international reserves, 2025', 'IMF, 2026', IMF_MUS),
                   C('87.8%', 'Public sector debt, share of GDP, 2025/26 (Rs682 billion); the budget aims for 79.8% within three years', 'PwC Mauritius, 2026', PWC_MUS, False),
                   C('75%', 'Fiscal anchor in law: public sector debt of 75% of GDP by end-June 2030, Public Debt Management Act as amended in 2025', 'allAfrica, 2026', AA_MUS, False)],
        'register': [],
        'newswire': [W('2026-07-15', 'IMF Executive Board Concludes 2026 Article IV Consultation with Mauritius', IMF_MUS, 'IMF'),
                     W('2026-07-01', 'Mauritius: Avoiding Stagflation - a Budget Analysis', AA_MUS, 'allAfrica')],
        'assets': [dict(name='The Reserves', figure='$10.3bn', money=True, label='Gross international reserves, 2025', text='Reserves worth about two thirds of a year’s output: a base for long-term finance in local currency.', src='IMF, PR 26/246; GDP 2024 $14.94 billion'),
                   'farmland', 'grid', 'forest', 'people'],
        'farm_text': 'Cane fields that built the economy, ready to be priced as land, energy and food.',
        'grid_text': 'Cane, sun and water already give a fifth of the power.',
        'letter': 'You built one of Africa’s most prosperous nations from cane fields and an open port, and you hold reserves worth about two thirds of a year’s output. Your debt is high, and you have written its limit into law. Let your institutions, your reserves and your ocean carry capital at the price they deserve.',
        'quote': 'You wrote the limit into law. Let the markets read it, and price it.',
        'sources': [WDI, STD, 'IMF, PR 26/246, 15 July 2026 (2026 Article IV).', 'PwC Mauritius, Budget 2026/27 public finance; allAfrica, 1 July 2026 (fiscal anchor). Capmad, IMF on debt of about 88% of GDP.'],
        'gaps': ['Exclusive economic zone: no primary figure read yet.', 'Safely managed sanitation and water are not measured; basic water and slum share used.', 'No outline at map scale: shown with the gold marker.'],
    },
    {
        'slug': 'niger', 'name': 'Niger', 'iso3': 'NER', 'iso2': 'NE', 'ne': 'Niger', 'demonym': 'Nigeriens', 'of_people': 'Nigeriens',
        'steward': 'Hadiza Moussa',
        'lead': 'A nation of 27.9 million, almost half under fifteen, that exports oil through a pipeline to the Atlantic and holds $4.6 billion of World Bank commitments.',
        'stats': [{'value': '$4.6bn', 'label': 'World Bank commitments, 23 operations, September 2026'}, {'value': '45.6%', 'label': 'Public debt, share of GDP, 2025'},
                  {'value': '$203M', 'label': 'New IMF programme agreed by staff, October 2026'}],
        'cap_heading': 'Oil to the sea, power to the people.',
        'record': [C('$4.6bn', 'World Bank commitments in grants and loans across 23 operations, September 2026', 'World Bank, 2026', WB_NER),
                   C('45.6%', 'Total public and publicly guaranteed debt, share of GDP, 2025', 'IMF, 2026', IMF_NER, False),
                   C('$203M', 'Proposed 38-month IMF programme, staff-level agreement 8 October 2026', 'Rio Times, 2026', RT_NER),
                   C('$15', 'Pipeline tariff a barrel to the Benin terminal, cut from $27 in a May 2026 agreement with CNPC', 'Coface, 2026', COF_NER)],
        'register': [R('multi', 'Active', 'Electricity access, including the Kandadji Dam programme', 'World Bank · One national and four regional projects', '$1.2bn', 'Power for more than 4.5 million people; about 905,000 connected since January 2026.', ['World Bank'], WB_NER),
                     R('multi', 'Active', 'Extended Credit Facility', 'IMF · Ninth review completed 29 July 2026', '', 'Oil revenue management and public financial management reforms.', ['IMF'], IMF_NER),
                     R('multi', 'Pipeline', 'New 38-month IMF programme', 'IMF · Staff-level agreement 8 October 2026 · Board expected December 2026', '$203M', 'Growth of about 7% expected in 2026.', ['IMF'], RT_NER, tone='pipeline'),
                     R('private', 'Signed', 'Niger–Benin pipeline tariff agreement', 'CNPC · May 2026', '', 'Transport rate to the Benin terminal cut from $27 to $15 a barrel.', ['CNPC'], COF_NER)],
        'newswire': [W('2026-07-29', 'IMF Executive Board Completes Ninth Review under the Extended Credit Facility Arrangement with Niger', IMF_NER, 'IMF')],
        'assets': [dict(name='The Oil Line', figure='$15', money=True, label='Pipeline tariff a barrel to the Atlantic, 2026', text='A landlocked nation now selling oil by sea; the cheaper the barrel travels, the more stays at home.', src='Coface country risk file, 2026'),
                   dict(name='The Power to Come', figure='905,000', money=False, label='Citizens connected to electricity since January 2026', text='A nation where one in five has power is connecting the rest, with the Kandadji Dam at its heart.', src='World Bank, Niger country page, 2026'),
                   'farmland', 'land', 'people'],
        'farm_text': 'Farms and herds that carry most families, from the river to the Sahel.',
        'letter': 'You send your oil to the sea through a pipeline across a neighbour, and you are connecting hundreds of thousands of citizens to power each year. Almost half of you are children, and on the last measure nine in ten could not read by the end of primary school. Let the oil teach and light every one of them.',
        'quote': 'Half of you are children. Let every barrel buy a classroom and a light.',
        'sources': [WDI, STD, 'IMF, PR 26/270, 29 July 2026; Rio Times, 8 October 2026 staff-level agreement.', 'World Bank, Niger country page (September 2026). Coface, Niger country risk file (CNPC tariff agreement, May 2026).'],
        'gaps': ['The pipeline tariff and staff-level amount are read in secondary sources; the IMF and CNPC releases are to be linked.', 'Learning outcomes date from 2019.'],
    },
    {
        'slug': 'sierra-leone', 'name': 'Sierra Leone', 'iso3': 'SLE', 'iso2': 'SL', 'ne': 'Sierra Leone', 'demonym': 'Sierra Leoneans', 'of_people': 'Sierra Leoneans',
        'steward': 'Isata Kamara',
        'lead': 'A nation of 8.8 million with three quarters of its power from water, which secured $211.5 million from the IMF for climate resilience in June 2026.',
        'stats': [{'value': '$211.5M', 'label': 'IMF Resilience and Sustainability Facility, June 2026'}, {'value': '47.3%', 'label': 'Public debt, share of GDP, 2026 projection'},
                  {'value': '75.3%', 'label': 'Electricity from renewable sources, 2021'}],
        'cap_heading': 'Rivers, iron and a climate arrangement.',
        'record': [C('$211.5M', 'IMF Resilience and Sustainability Facility, approved 18 June 2026', 'IMF, 2026', IMF_SLE),
                   C('$158.6M', 'Total disbursed under the Extended Credit Facility after the third review, June 2026', 'IMF, 2026', IMF_SLE),
                   C('47.3%', 'Public debt, share of GDP, projected for 2026, from 50.8% in 2024; high risk of distress', 'Premier Media, 2025', PM_SLE, False),
                   C('$137M', 'Regional digital integration programme with Benin and Liberia, March 2026', 'allAfrica, 2026', WARDIP)],
        'register': [R('multi', 'Approved', 'Resilience and Sustainability Facility', 'IMF · Approved 18 June 2026', '$211.5M', 'Climate resilience, public investment and financial stability; SDR 155.55 million.', ['IMF'], IMF_SLE),
                     R('multi', 'Active', 'Extended Credit Facility', 'IMF · Approved 31 October 2024 · 38 months', '', 'Third review completed 18 June 2026; a safe-harbour pricing formula for iron ore among the prior actions.', ['IMF'], IMF_SLE_ECF),
                     R('regional', 'Approved', 'West Africa Regional Digital Integration (WARDIP2)', 'World Bank · Approved 10 March 2026 · With Benin and Liberia', '$137M', 'Jobs through an integrated regional digital market.', ['World Bank'], WARDIP)],
        'newswire': [W('2026-06-19', 'IMF approves $211 million climate resilience programme for Sierra Leone', CGTN_SLE, 'CGTN', '$211 million'),
                     W('2025-12-16', 'IMF Executive Board Completes First and Second Reviews of Sierra Leone’s Arrangement under the Extended Credit Facility', IMF_SLE_12, 'IMF')],
        'assets': ['grid', 'water', 'farmland', 'forest', 'people'],
        'grid_text': 'Rivers already give three quarters of the power; four in ten have electricity, and every new line can be clean.',
        'letter': 'Your rivers already give three quarters of your power, and you renew more fresh water per person than most of the world. About one in nine of you drinks safely managed water. Let the rivers that light the grid also fill every tap.',
        'quote': 'The rivers already light your grid. Let them fill every tap as well.',
        'sources': [WDI, STD, 'IMF, PR 24/432 (22 November 2024), PR 25/424 (16 December 2025), PR 26/213 and Country Report 26/168 (June 2026).', 'Premier Media, IMF debt projections; CGTN, 19 June 2026; allAfrica, 12 March 2026.'],
        'gaps': ['Iron ore output: no primary page read yet.', 'Learning outcomes not measured; lower-secondary completion used.'],
    },
    {
        'slug': 'sudan', 'name': 'Sudan', 'iso3': 'SDN', 'iso2': 'SD', 'ne': 'Sudan', 'demonym': 'Sudanese', 'of_people': 'Sudanese',
        'steward': 'Nour Abdelrahman',
        'food': {'value': 60.0, 'display': '60%', 'note': 'Not in IPC Phase 3 or above; nearly 19.5 million, two in five, face acute food insecurity',
                 'source': 'IPC via WFP, 2026', 'url': WFP_SDN},
        'lead': 'A nation of 51.7 million in its fourth year of war, where nearly 19.5 million people face acute hunger and the $2.9 billion humanitarian plan for 2026 is less than half funded.',
        'stats': [{'value': '$2.9bn', 'label': 'Humanitarian Needs and Response Plan, 2026'}, {'value': '19.5M', 'label': 'People facing acute food insecurity, May 2026'},
                  {'value': '57%', 'label': 'Funding gap of the 2026 plan, 8 October 2026'}],
        'cap_heading': 'Relief first. Then the capital to rebuild.',
        'record': [C('$2.9bn', 'Humanitarian Needs and Response Plan 2026, including $526 million for refugees', 'OCHA, 2026', OCHA_SDN),
                   C('57%', 'Funding gap of the 2026 plan as of 8 October 2026; nutrition 30% and water and sanitation 23% funded', 'Sudan Tribune, 2026', ST_SDN, False),
                   C('$402M', 'Needed by WFP from October 2026 to March 2027 for emergency food for 4 million people', 'WFP, 2026', WFP_SDN_E)],
        'register': [R('humanitarian', 'Appeal', 'Humanitarian Needs and Response Plan 2026', 'United Nations and partners · Less than half funded, October 2026', '$2.9bn', 'Food, nutrition, water, health, protection and education for more than 20 million people.', ['OCHA'], OCHA_SDN, tone='appeal'),
                     R('humanitarian', 'Appeal', 'WFP emergency food and nutrition', 'WFP · October 2026 to March 2027', '$402M', 'Life-saving assistance for 4 million people; 800,000 cut from assistance for lack of funds.', ['WFP'], WFP_SDN_E, tone='appeal')],
        'newswire': [W('2026-10-13', 'Famine risk surges across Sudan’s Darfur and Kordofan regions, alert warns', ST_SDN, 'Sudan Tribune'),
                     W('2026-05-15', 'Risk of Famine persists as nearly 19.5 million people face acute food insecurity in Sudan', WFP_SDN, 'WFP')],
        'assets': ['farmland', 'grid', 'ground', 'land', 'people'],
        'farm_text': 'Six tenths of the land in agriculture along the Niles: the breadbasket the nation can be again.',
        'grid_text': 'The Nile dams gave six tenths of the power before the war.',
        'letter': 'You are living through the largest hunger crisis on earth, and nearly nine million of you have been driven from your homes. Relief comes first, and peace above all. When it comes, your Nile farmland, your gold and your people will need capital that arrives as fast as the need. We will be ready to design it with you.',
        'quote': 'Peace first. Then capital as fast as the need, so that no Sudanese family goes hungry again.',
        'sources': [WDI, STD, 'FAO, UNICEF and WFP joint news release, 15 May 2026; WFP Sudan emergency page; OCHA, Sudan Humanitarian Needs and Response Plan 2026.', 'Sudan Tribune, 13 October 2026 (IPC alert and OCHA funding figures).'],
        'gaps': ['Public debt: no primary figure read (IMF WEO projection reported in secondary sources).', 'Poverty data date from 2009 and 2014, before the war: marked dated.', 'Learning outcomes not measured; lower-secondary completion 2019 used.'],
    },
    {
        'slug': 'togo', 'name': 'Togo', 'iso3': 'TGO', 'iso2': 'TG', 'ne': 'Togo', 'demonym': 'Togolese', 'of_people': 'Togolese',
        'steward': 'Akossiwa Mensah',
        'lead': 'A nation of 8.6 million building West Africa’s logistics hub, which signed $429 million with the World Bank in 2026, including $200 million to modernise its transport.',
        'stats': [{'value': '$429M', 'label': 'Five World Bank agreements signed, 2026'}, {'value': '$385M', 'label': 'Transport and logistics programme, all financiers'},
                  {'value': '$403.4M', 'label': 'IMF Extended Credit Facility, 2024'}],
        'cap_heading': 'A port nation, financed as a hub.',
        'record': [C('$200M', 'Logistics and Transport Systems Improvement Program (PASLT), IDA, approved 16 June 2026', 'World Bank, 2026', WB_TGO),
                   C('$385M', 'Total cost of the transport programme: World Bank $200 million, EIB $90 million, AIIB $75 million, private $20 million', 'AIIB, 2026', AIIB_TGO),
                   C('$429M', 'Five financing agreements signed with the World Bank; active portfolio of $2.1 billion', 'LogistAfrica, 2026', LA_TGO),
                   C('$403.4M', 'IMF Extended Credit Facility, 42 months, approved March 2024', 'IMF, 2025', IMF_TGO)],
        'register': [R('multi', 'Approved', 'Logistics and Transport Systems Improvement Program (PASLT)', 'IDA · Approved 16 June 2026 · P508939', '$200M', 'Roads, rail and urban logistics linking farm regions to markets; about 2.2 million residents of Greater Lomé benefit.', ['World Bank'], WB_TGO),
                     R('multi', 'Proposed', 'Transport Connectivity and Logistics Improvement Project', 'AIIB · Sovereign-backed loan · Co-financing with the World Bank', '$75M', 'Part of a $385 million programme with the EIB and private capital.', ['AIIB'], AIIB_TGO, tone='pipeline'),
                     R('multi', 'Active', 'Extended Credit Facility', 'IMF · Approved March 2024 · Third and fourth reviews agreed by staff May 2026', '$403.4M', 'Seven of eight structural benchmarks met since the second review.', ['IMF'], IMF_TGO_SLA),
                     R('regional', 'Approved', 'Northern Gulf of Guinea Social Cohesion (COSO), additional financing', 'World Bank · Approved 25 June 2026 · With Benin and Côte d’Ivoire', '$163M', 'Jobs and services in fragile border areas.', ['World Bank'], WB_COSO, note='Total for three nations')],
        'newswire': [W('2026-06-23', 'Togo Secures $200 Million World Bank Financing to Modernize Road and Rail Transport', TF_TGO, 'Togo First', '$200 Million'),
                     W('2026-05-21', 'IMF Reaches Staff-Level Agreement with Togo on the Combined Third and Fourth Reviews under the ECF Arrangement', IMF_TGO_SLA, 'IMF')],
        'assets': [dict(name='The Port', figure='2.2m', money=False, label='Greater Lomé residents served by the transport programme', text='A deep-water port and corridors to the Sahel: a hub that can be priced as an asset.', src='World Bank press release, 16 June 2026'),
                   'farmland', 'forest', 'water', 'people'],
        'farm_text': 'Seven tenths of the land in agriculture, linked to the port by new corridors.',
        'letter': 'You have turned a narrow strip of coast into a gateway for the Sahel, and your partners are financing the roads and rails behind your port. Four in ten of you are under fifteen. Let the hub that moves the region’s goods also move every Togolese family above the Living Line.',
        'quote': 'You built the gateway. Let it carry every family through.',
        'sources': [WDI, STD, 'World Bank, 16 and 25 June 2026; AIIB project summary (PASLT co-financing); LogistAfrica on the five agreements of July 2026.', 'IMF, PR 25/229 (30 June 2025) and PR 26/167 (21 May 2026).'],
        'gaps': ['Public debt in % of GDP: the IMF table is to be read with its years before publication.', 'Learning outcomes date from 2019.'],
    },
    {
        'slug': 'tunisia', 'name': 'Tunisia', 'iso3': 'TUN', 'iso2': 'TN', 'ne': 'Tunisia', 'demonym': 'Tunisians', 'of_people': 'Tunisians',
        'steward': 'Yasmine Gharbi',
        'lead': 'A nation of 12.3 million that repays its debts on time and finances itself at home, with public debt of 82.2% of GDP in 2025 and a $500 million Afreximbank loan in June 2026.',
        'stats': [{'value': '$500M', 'label': 'Afreximbank term loan, June 2026'}, {'value': '82.2%', 'label': 'Public debt, share of GDP, 2025'},
                  {'value': '5.86%', 'label': 'Rate negotiated on the Afreximbank loan, from 9%'}],
        'cap_heading': 'Paid on time, financed at home.',
        'record': [C('$500M', 'Afreximbank term loan to the Central Bank of Tunisia for the Ministry of Finance, signed June 2026', 'TXF, 2026', TXF_TUN),
                   C('82.2%', 'Public debt, share of GDP, 2025, down from 84.9% in 2024', 'World Bank, 2026', WB_TUN, False),
                   C('5.86%', 'Interest rate on the Afreximbank loan after negotiation, from 9%', 'La Presse, 2026', LP_TUN, False),
                   C('TND 9.8bn', 'Interest-free central bank facility in the draft 2027 budget, the fourth year running', 'Enterprise, 2026', ENT_TUN)],
        'register': [R('regional', 'Signed', 'Afreximbank term loan', 'Afreximbank · Approved by decree 8 June 2026 · Signed June 2026', '$500M', 'Budget support within the 2026 budget law.', ['Afreximbank', 'Central Bank of Tunisia'], TXF_TUN),
                     R('regional', 'Pipeline', 'Second Afreximbank financing', 'Afreximbank · Before Parliament, July 2026', '$500M', 'A further $500 million for the 2026 budget.', ['Afreximbank'], LP_TUN, tone='pipeline'),
                     R('govt', 'Proposed', 'Central bank interest-free facility, 2027', 'Central Bank of Tunisia · Draft 2027 budget', 'TND 9.8bn', 'Direct financing of the budget by the central bank, about $3.3 billion.', ['Central Bank of Tunisia'], ENT_TUN, tone='pipeline')],
        'newswire': [W('2026-11-02', 'Tunisia is funding a 32% bigger deficit next year by leaning harder on domestic borrowing, crowding out SMEs', ENT_TUN, 'Enterprise', '32%'),
                     W('2026-07-31', 'Prêt Afreximbank : un taux ramené de 9 % à 5,86 % après négociations', LP_TUN, 'La Presse'),
                     W('2026-06-11', 'Tunisia: $500 million loan from Afreximbank approved', FA_TUN, 'Financial Afrik', '$500 million')],
        'assets': ['farmland', dict(name='The Grid', figure='100%', money=False, label='Of citizens with electricity, 2024', text='Every household connected and every kitchen on clean fuel: a base for sun and wind to export power north.', src='World Bank, access to electricity and clean cooking, 2024'),
                   dict(name='The Schools', figure='82.4%', money=False, label='Complete lower secondary school, 2021', text='One of the most educated workforces in Africa, ready for industry and services.', src='World Bank, lower secondary completion rate, 2021'),
                   'land', 'people'],
        'farm_text': 'Six tenths of the land in agriculture: olive groves, cereals and dates.',
        'letter': 'You pay your debts on time, every household has electricity, and most of your young people finish lower secondary school. Yet you finance yourself almost entirely at home, at the cost of your own companies. Let your institutions and your sun open cheaper capital from abroad.',
        'quote': 'A nation that pays on time should borrow at the price of its word.',
        'sources': [WDI, STD, 'World Bank, Macro Poverty Outlook, Tunisia (2026).', 'TXF, 23 June 2026; Financial Afrik, 11 June 2026; La Presse, 31 July 2026; Enterprise, 2 November 2026.'],
        'gaps': ['Learning outcomes date from 2011.', 'The Grid and The Schools are World Bank figures; the olive and date output need a primary source before they are named with figures.'],
    },
]
