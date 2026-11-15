"""The head of state and the National Day of every blueprint nation (the Steward-General, 15 November 2026).

Writes the `head_of_state` and `national_day` of each nation into data/nation-protocol.json, keeping every other field
(France keeps its own entry, its letters and its recipients untouched). Run from the repository root:

    python3 tools/protocol/all_nations.py            # write data/nation-protocol.json
    python3 tools/protocol/all_nations.py --check    # list what would change, write nothing

Sources (primary, read on 15 November 2026):
  UN   United Nations Protocol and Liaison Service, Heads of State, Heads of Government and Ministers for Foreign
       Affairs, list of 13 November 2026. Titles are the list's English titles; names are written without honorifics
       or ranks.
  CPH  Ministry of Foreign Affairs of Denmark, Copenhagen Diplomatic List, 26 October 2026 (National Days).
  SE   Government Offices of Sweden, National Days list; NZ New Zealand MFAT, National Days; AU Australia DFAT
       Protocol, National Days; PH Philippines DFA Office of Protocol, National Days; and each nation's own source
       where noted.

The Blueprints Steward checks every head of state on the 1st of each month, and each nation again 15 days before its
National Day, against the UN list and the nation's own sources, and updates the table below, then reruns this file.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'nation-protocol.json'
CHECKED = '2026-11-15'

SRC = {
    'UN': ('United Nations Protocol, list of 13 November 2026',
           'https://www.un.org/dgacm/sites/www.un.org.dgacm/files/Documents_Protocol/hspmfmlist.pdf'),
    'CPH': ('Copenhagen Diplomatic List, 26 October 2026',
            'https://um.dk/media/3pjjbw5h/copenhagen-diplomatic-list-26102026.pdf'),
    'SE': ('Government Offices of Sweden, National Days',
           'https://www.government.se/globalassets/government/dokument/utrikesdepartementet/diplomatportalen/national-days/national-days-20240618.pdf'),
    'NZ': ('New Zealand Ministry of Foreign Affairs and Trade, National Days', 'https://www.mfat.govt.nz/en/embassies/national-days'),
    'AU': ('Australian Government DFAT Protocol, National Days', 'https://protocol.dfat.gov.au/Public/NationalDays'),
    'PH': ('Philippines Department of Foreign Affairs, National Days', 'https://dfa.gov.ph/office-of-protocol/national-days'),
    'LI': ('The Princely House of Liechtenstein, National Day 2026',
           'https://fuerstenhaus.li/wp-content/uploads/2026/08/Staatsfeiertag-2026_Rede-S.D.-Erbprinz-Alois-final-Englisch.pdf'),
    'OM': ('Ministry of Foreign Affairs of Oman', 'https://www.fm.gov.om/en/31490/'),
    'BB': ('Official Gazette of Barbados, 2 July 2026',
           'https://www.barbadosparliament.com/uploads/gazette/Gazette_July_2_2026_Part_C_CLXI_No_77.pdf'),
    'NO': ('The Royal House of Norway', 'https://www.kongehuset.no/for-pressen/information-in-english/oath-of-allegiance-to-the-constitution-en'),
    'SM': ('Reggenza della Repubblica di San Marino',
           'https://reggenzadellarepubblica.sm/pub1/ReggenzaSM/en/Capitani_Reggenti/Capitani_Reggenti_In_Carica.html'),
}

# slug | head of state (names joined by " and " for joint heads; blank where the band shows the National Day only)
#      | English title | source of the head of state | since (if changed in 2026) | MM-DD | name of the day | source of the day
TABLE = """
afghanistan||||| 08-19 | National Day | CPH
albania | Bajram Begaj | President of the Republic of Albania | UN || 11-28 | National Day | CPH
algeria | Abdelmadjid Tebboune | President of the People’s Democratic Republic of Algeria | UN || 11-01 | National Day | CPH
andorra | Josep-Lluís Serrano Pentinat and Emmanuel Macron | Co-Princes of Andorra | UN || 09-08 | Our Lady of Meritxell Day | CPH
angola | João Manuel Gonçalves Lourenço | President of the Republic of Angola | UN || 11-11 | Independence Day | CPH
antigua-and-barbuda | Charles III | King of Antigua and Barbuda | UN || 11-01 | Independence Day | CPH
argentina | Javier Milei | President of the Argentine Republic | UN || 05-25 | National Day | CPH
armenia | Vahagn Khachaturyan | President of the Republic of Armenia | UN || 09-21 | National Day | CPH
australia | Charles III | King of Australia | UN || 01-26 | Australia Day | CPH
austria | Alexander Van der Bellen | Federal President of the Republic of Austria | UN || 10-26 | National Day | CPH
azerbaijan | Ilham Aliyev | President of the Republic of Azerbaijan | UN || 05-28 | Independence Day | CPH
bahamas | Charles III | King of The Bahamas | UN || 07-10 | National Day | SE
bahrain | Hamad bin Isa Al Khalifa | King of the Kingdom of Bahrain | UN || 12-16 | National Day | CPH
bangladesh | Mirza Fakhrul Islam Alamgir | President of the People’s Republic of Bangladesh | UN | 2026-09-01 | 03-26 | Independence Day | CPH
barbados | Jeffrey Bostic | President of Barbados | BB | 2026 | 11-30 | National Day | CPH
belarus | Aleksandr Lukashenko | President of the Republic of Belarus | UN || 07-03 | Independence Day | CPH
belgium | Philippe | King of the Belgians | UN || 07-21 | National Day | CPH
belize | Charles III | King of Belize | UN || 09-21 | Independence Day | CPH
benin | Romuald Wadagni | President of the Republic of Benin | UN | 2026-05-24 | 08-01 | Independence Day | CPH
bhutan | Jigme Khesar Namgyel Wangchuck | King of Bhutan | UN || 12-17 | National Day | CPH
bolivia | Rodrigo Paz Pereira | President of the Plurinational State of Bolivia | UN || 08-06 | Independence Day | CPH
bosnia-and-herzegovina | Denis Bećirović | Chairman of the Presidency of Bosnia and Herzegovina | UN || 11-25 | Statehood Day | CPH
botswana | Duma Gideon Boko | President of the Republic of Botswana | UN || 09-30 | National Day | CPH
brazil | Luiz Inácio Lula da Silva | President of the Federative Republic of Brazil | UN || 09-07 | Independence Day | CPH
brunei | Hassanal Bolkiah | Sultan and Yang Di-Pertuan of Brunei Darussalam | UN || 02-23 | National Day | CPH
bulgaria | Iliana Iotova | President of the Republic of Bulgaria | UN || 03-03 | National Day | CPH
burkina-faso | Ibrahim Traoré | President of Faso, Head of State | UN || 12-11 | National Day | CPH
burundi | Évariste Ndayishimiye | President of the Republic of Burundi | UN || 07-01 | National Day | CPH
cabo-verde | José Maria Pereira Neves | President of the Republic of Cabo Verde | UN || 07-05 | National Day | SE
cambodia | Norodom Sihamoni | King of Cambodia | UN || 11-09 | Independence Day | CPH
cameroon | Paul Biya | President of the Republic of Cameroon | UN || 05-20 | National Day | CPH
canada | Charles III | King of Canada | UN || 07-01 | Canada Day | CPH
central-african-republic | Faustin-Archange Touadéra | President of the Central African Republic | UN || 12-01 | National Day | CPH
chad | Mahamat Idriss Déby Itno | President of the Republic of Chad | UN || 08-11 | National Day | CPH
chile | José Antonio Kast | President of the Republic of Chile | UN || 09-18 | Independence Day | CPH
china | Xi Jinping | President of the People’s Republic of China | UN || 10-01 | National Day | CPH
colombia | Abelardo de la Espriella | President of the Republic of Colombia | UN | 2026-08-07 | 07-20 | Independence Day | CPH
comoros | Azali Assoumani | President of the Union of the Comoros | UN || 07-06 | National Day | CPH
costa-rica | Laura Fernández Delgado | President of the Republic of Costa Rica | UN || 09-15 | Independence Day | CPH
croatia | Zoran Milanović | President of the Republic of Croatia | UN || 05-30 | Statehood Day | CPH
cuba | Miguel Díaz-Canel Bermúdez | President of the Republic of Cuba | UN || 01-01 | Liberation Day | CPH
cyprus | Nikos Christodoulides | President of the Republic of Cyprus | UN || 10-01 | Independence Day | CPH
czechia | Petr Pavel | President of the Czech Republic | UN || 10-28 | National Day | CPH
cote-divoire | Alassane Ouattara | President of the Republic of Côte d’Ivoire | UN || 08-07 | National Day | CPH
denmark | Frederik X | King of Denmark | UN || 06-05 | Constitution Day | CPH
djibouti | Ismaïl Omar Guelleh | President of the Republic of Djibouti | UN || 06-27 | National Day | CPH
dominica | Sylvanie Burton | President of the Commonwealth of Dominica | UN || 11-03 | National Day | SE
dominican-republic | Luis Abinader | President of the Dominican Republic | UN || 02-27 | Independence Day | CPH
dr-congo | Félix Tshisekedi | President of the Democratic Republic of the Congo | UN || 06-30 | Independence Day | CPH
ecuador | Daniel Noboa | President of the Republic of Ecuador | UN || 08-10 | National Day | CPH
egypt | Abdel Fattah Al Sisi | President of the Arab Republic of Egypt | UN || 07-23 | National Day | CPH
el-salvador | Nayib Bukele | President of the Republic of El Salvador | UN || 09-15 | Independence Day | CPH
equatorial-guinea | Teodoro Obiang Nguema Mbasogo | President of the Republic of Equatorial Guinea | UN || 10-12 | National Day | SE
eritrea | Isaias Afwerki | President of the State of Eritrea | UN || 05-24 | Independence Day | CPH
estonia | Ülle Madise | President of the Republic of Estonia | UN | 2026-10-12 | 02-24 | Independence Day | CPH
eswatini | Mswati III | King of Eswatini | UN || 09-06 | Independence Day | CPH
ethiopia | Taye Atske Selassie | President of the Federal Democratic Republic of Ethiopia | UN || 05-28 | National Day | CPH
fiji | Naiqama Lalabalavu | President of the Republic of Fiji | UN || 10-10 | National Day | CPH
finland | Alexander Stubb | President of the Republic of Finland | UN || 12-06 | National Day | CPH
gabon | Brice Clotaire Oligui Nguema | President of the Gabonese Republic | UN || 08-17 | Independence Day | CPH
gambia | Adama Barrow | President of the Republic of The Gambia | UN || 02-18 | Independence Day | CPH
georgia | Mikheil Kavelashvili | President of Georgia | UN || 05-26 | Independence Day | CPH
germany | Frank-Walter Steinmeier | President of the Federal Republic of Germany | UN || 10-03 | German Unity Day | CPH
ghana | John Dramani Mahama | President of the Republic of Ghana | UN || 03-06 | Independence Day | CPH
greece | Konstantinos Tasoulas | President of the Hellenic Republic | UN || 03-25 | Independence Day | CPH
grenada | Charles III | King of Grenada | UN || 02-07 | National Day | CPH
guatemala | Bernardo Arévalo | President of the Republic of Guatemala | UN || 09-15 | Independence Day | CPH
guinea | Mamadi Doumbouya | President of the Republic of Guinea | UN || 10-02 | National Day | CPH
guinea-bissau | Horta Inta-a | Transitional President of the Republic of Guinea-Bissau | UN || 09-24 | National Day | CPH
guyana | Mohamed Irfaan Ali | President of the Co-operative Republic of Guyana | UN || 02-23 | National Day | CPH
haiti | Laurent Saint-Cyr | President of the Transitional Presidential Council of the Republic of Haiti | UN || 01-01 | National Day | CPH
holy-see | Leo XIV | Supreme Pontiff | UN || 05-08 | Anniversary of the Pope’s Election | CPH
honduras | Nasry Asfura | President of the Republic of Honduras | UN || 09-15 | Independence Day | CPH
hungary | András Bálint Baka | President of Hungary | UN | 2026-08-19 | 08-20 | St Stephen’s Day | CPH
iceland | Halla Tómasdóttir | President of Iceland | UN || 06-17 | Republic Day | CPH
india | Droupadi Murmu | President of the Republic of India | UN || 08-15 | Independence Day | CPH
indonesia | Prabowo Subianto | President of the Republic of Indonesia | UN || 08-17 | Independence Day | CPH
iran | Masoud Pezeshkian | President of the Islamic Republic of Iran | UN || 02-11 | National Day | CPH
iraq | Nazar Amedi | President of the Republic of Iraq | UN | 2026-04-11 | 10-03 | National Day | SE
ireland | Catherine Connolly | President of Ireland | UN || 03-17 | St Patrick’s Day | CPH
israel | Isaac Herzog | President of the State of Israel | UN || 05-12 | Independence Day | CPH
italy | Sergio Mattarella | President of the Italian Republic | UN || 06-02 | National Day | CPH
jamaica | Charles III | King of Jamaica | UN || 08-06 | Independence Day | CPH
japan | Naruhito | Emperor of Japan | UN || 02-23 | The Emperor’s Birthday | CPH
jordan | Abdullah II ibn Al Hussein | King of the Hashemite Kingdom of Jordan | UN || 05-25 | Independence Day | CPH
kazakhstan | Kassym-Jomart Tokayev | President of the Republic of Kazakhstan | UN || 10-25 | Republic Day | SE
kenya | William Ruto | President of the Republic of Kenya | UN || 12-12 | National Day | CPH
kiribati | Taneti Maamau | President of the Republic of Kiribati | UN || 07-12 | Independence Day | NZ
kuwait | Meshal Al-Ahmad Al-Jaber Al-Sabah | Amir of the State of Kuwait | UN || 02-25 | National Day | CPH
kyrgyzstan | Sadyr Japarov | President of the Kyrgyz Republic | UN || 08-31 | National Day | CPH
laos | Thongloun Sisoulith | President of the Lao People’s Democratic Republic | UN || 12-02 | National Day | CPH
latvia | Edgars Rinkēvičs | President of the Republic of Latvia | UN || 11-18 | National Day | CPH
lebanon | Joseph Aoun | President of the Republic of Lebanon | UN || 11-22 | National Day | CPH
lesotho | Letsie III | King of Lesotho | UN || 10-04 | National Day | CPH
liberia | Joseph Nyuma Boakai | President of the Republic of Liberia | UN || 07-26 | Independence Day | CPH
libya | Mohamed Younis Menfi | President of the Presidential Council of Libya | UN || 12-24 | National Day | CPH
liechtenstein | Hans-Adam II | Reigning Prince of Liechtenstein | UN || 08-15 | National Day | LI
lithuania | Gitanas Nausėda | President of the Republic of Lithuania | UN || 02-16 | Independence Day | CPH
luxembourg | Guillaume | Grand Duke of Luxembourg | UN || 06-23 | National Day | CPH
madagascar | Michaël Randrianirina | President of the Refoundation of the Republic of Madagascar | UN || 06-26 | Independence Day | CPH
malawi | Peter Mutharika | President of the Republic of Malawi | UN || 07-06 | National Day | CPH
malaysia | Sultan Ibrahim | King of Malaysia | UN || 08-31 | National Day | CPH
maldives | Mohamed Muizzu | President of the Republic of Maldives | UN || 07-26 | National Day | SE
mali | Assimi Goïta | President of the Transition, Head of State of the Republic of Mali | UN || 09-22 | National Day | CPH
malta | Myriam Spiteri Debono | President of the Republic of Malta | UN || 09-21 | National Day | CPH
marshall-islands | Hilda Heine | President of the Republic of the Marshall Islands | UN || 05-01 | Constitution Day | PH
mauritania | Mohamed Ould Cheikh El Ghazouani | President of the Islamic Republic of Mauritania | UN || 11-28 | National Day | CPH
mauritius | Dharambeer Gokhool | President of the Republic of Mauritius | UN || 03-12 | National Day | CPH
mexico | Claudia Sheinbaum Pardo | President of the United Mexican States | UN || 09-16 | Independence Day | CPH
micronesia | Wesley W. Simina | President of the Federated States of Micronesia | UN || 11-03 | National Day | NZ
moldova | Maia Sandu | President of the Republic of Moldova | UN || 08-27 | Independence Day | CPH
monaco | Albert II | Sovereign Prince of Monaco | UN || 11-19 | National Day | CPH
mongolia | Khurelsukh Ukhnaa | President of Mongolia | UN || 07-11 | Naadam | CPH
montenegro | Jakov Milatović | President of Montenegro | UN || 07-13 | National Day | CPH
morocco | Mohammed VI | King of Morocco | UN || 07-30 | Throne Day | CPH
mozambique | Daniel Chapo | President of the Republic of Mozambique | UN || 06-25 | Independence Day | CPH
myanmar||||| 01-04 | Independence Day | CPH
namibia | Netumbo Nandi-Ndaitwah | President of the Republic of Namibia | UN || 03-21 | Independence Day | CPH
nauru | David Adeang | President of the Republic of Nauru | UN || 01-31 | Independence Day | NZ
nepal | Ramchandra Paudel | President of Nepal | UN || 09-19 | Constitution Day | CPH
netherlands | Willem-Alexander | King of the Netherlands | UN || 04-27 | King’s Day | CPH
new-zealand | Charles III | King of New Zealand | UN || 02-06 | Waitangi Day | CPH
nicaragua | Daniel Ortega Saavedra and Rosario Murillo | Co-Presidents of the Republic of Nicaragua | UN || 09-15 | Independence Day | CPH
niger | Abdourahamane Tiani | President of the Republic of Niger, Head of State | UN || 12-18 | National Day | CPH
nigeria | Bola Ahmed Tinubu | President of the Federal Republic of Nigeria | UN || 10-01 | National Day | CPH
north-korea | Kim Jong Un | President of the State Affairs of the Democratic People’s Republic of Korea | UN || 09-09 | National Day | CPH
north-macedonia | Gordana Siljanovska-Davkova | President of the Republic of North Macedonia | UN || 09-08 | National Day | CPH
norway | Haakon VIII | King of Norway | NO | 2026-08-28 | 05-17 | Constitution Day | CPH
oman | Haitham bin Tarik | Sultan of Oman | UN || 11-20 | National Day | OM
pakistan | Asif Ali Zardari | President of the Islamic Republic of Pakistan | UN || 03-23 | Pakistan Day | CPH
palau | Surangel Whipps Jr. | President of the Republic of Palau | UN || 10-01 | Independence Day | PH
palestine | Mahmoud Abbas | President of the State of Palestine | UN || 11-15 | National Day | SE
panama | José Raúl Mulino | President of the Republic of Panama | UN || 11-03 | National Day | CPH
papua-new-guinea | Charles III | King of Papua New Guinea | UN || 09-16 | Independence Day | CPH
paraguay | Santiago Peña | President of the Republic of Paraguay | UN || 05-15 | Independence Day | CPH
peru | Keiko Fujimori | President of the Republic of Peru | UN || 07-28 | Independence Day | CPH
philippines | Ferdinand R. Marcos Jr. | President of the Republic of the Philippines | UN || 06-12 | Independence Day | CPH
poland | Karol Nawrocki | President of the Republic of Poland | UN || 05-03 | Constitution Day | CPH
portugal | António José Seguro | President of the Portuguese Republic | UN || 06-10 | National Day | CPH
qatar | Tamim bin Hamad Al Thani | Amir of the State of Qatar | UN || 12-18 | National Day | CPH
republic-of-congo | Denis Sassou Nguesso | President of the Republic of the Congo | UN || 08-15 | National Day | CPH
romania | Nicușor Dan | President of Romania | UN || 12-01 | National Day | CPH
russia | Vladimir Putin | President of the Russian Federation | UN || 06-12 | National Day | CPH
rwanda | Paul Kagame | President of the Republic of Rwanda | UN || 07-01 | National Day | CPH
saint-kitts-and-nevis | Charles III | King of Saint Kitts and Nevis | UN || 09-19 | National Day | SE
saint-lucia | Charles III | King of Saint Lucia | UN || 02-22 | National Day | SE
saint-vincent-and-the-grenadines | Charles III | King of Saint Vincent and the Grenadines | UN || 10-27 | Independence Day | CPH
samoa | Tuimalealiifano Vaaletoa Sualauvi II | Head of State of Samoa | UN || 06-01 | Independence Day | CPH
san-marino | The Captains Regent | Heads of State of the Republic of San Marino | SM || 09-03 | National Day | CPH
sao-tome-and-principe | Carlos Vila Nova | President of the Democratic Republic of São Tomé and Príncipe | UN || 07-12 | National Day | CPH
saudi-arabia | Salman bin Abdulaziz Al Saud | King of Saudi Arabia, Custodian of the Two Holy Mosques | UN || 09-23 | National Day | CPH
senegal | Bassirou Diomaye Faye | President of the Republic of Senegal | UN || 04-04 | National Day | CPH
serbia | Aleksandar Vučić | President of the Republic of Serbia | UN || 02-15 | National Day | CPH
seychelles | Patrick Herminie | President of the Republic of Seychelles | UN || 06-18 | Constitution Day | CPH
sierra-leone | Julius Maada Bio | President of the Republic of Sierra Leone | UN || 04-27 | National Day | CPH
singapore | Tharman Shanmugaratnam | President of the Republic of Singapore | UN || 08-09 | National Day | CPH
slovakia | Peter Pellegrini | President of the Slovak Republic | UN || 09-01 | Constitution Day | CPH
slovenia | Nataša Pirc Musar | President of the Republic of Slovenia | UN || 06-25 | Statehood Day | CPH
solomon-islands | Charles III | King of Solomon Islands | UN || 07-07 | Independence Day | NZ
somalia | Hassan Sheikh Mohamud | President of the Federal Republic of Somalia | UN || 07-01 | National Day | SE
south-africa | Cyril Ramaphosa | President of the Republic of South Africa | UN || 04-27 | National Day | CPH
south-korea | Lee Jae Myung | President of the Republic of Korea | UN || 10-03 | National Day | CPH
south-sudan | Salva Kiir Mayardit | President of the Republic of South Sudan | UN || 07-09 | National Day | SE
spain | Felipe VI | King of Spain | UN || 10-12 | National Day | CPH
sri-lanka | Anura Kumara Dissanayake | President of the Democratic Socialist Republic of Sri Lanka | UN || 02-04 | Independence Day | CPH
sudan | Abdel Fattah Al-Burhan | President of the Transitional Sovereignty Council of the Republic of the Sudan | UN || 01-01 | Independence Day | CPH
suriname | Jennifer Geerlings-Simons | President of the Republic of Suriname | UN || 11-25 | Independence Day | AU
sweden | Carl XVI Gustaf | King of Sweden | UN || 06-06 | National Day | CPH
switzerland | Guy Parmelin | President of the Swiss Confederation | UN || 08-01 | National Day | CPH
syria | Ahmad Al-Sharaa | President of the Syrian Arab Republic | UN || 04-17 | National Day | CPH
tajikistan | Emomali Rahmon | President of the Republic of Tajikistan | UN || 09-09 | Independence Day | CPH
tanzania | Samia Suluhu Hassan | President of the United Republic of Tanzania | UN || 04-26 | Union Day | CPH
thailand | Maha Vajiralongkorn | King of Thailand | UN || 12-05 | National Day | CPH
timor-leste | José Ramos-Horta | President of the Democratic Republic of Timor-Leste | UN || 05-20 | Restoration of Independence Day | AU
togo | Jean-Lucien Savi de Tové | President of the Togolese Republic | UN || 04-27 | National Day | CPH
tonga | Tupou VI | King of Tonga | UN || 11-04 | Constitution Day | CPH
trinidad-and-tobago | Christine Kangaloo | President of the Republic of Trinidad and Tobago | UN || 08-31 | National Day | CPH
tunisia | Kaïs Saïed | President of the Republic of Tunisia | UN || 03-20 | National Day | CPH
turkmenistan | Serdar Berdimuhamedov | President of Turkmenistan | UN || 09-27 | Independence Day | CPH
tuvalu | Charles III | King of Tuvalu | UN || 10-01 | Independence Day | NZ
turkiye | Recep Tayyip Erdoğan | President of the Republic of Türkiye | UN || 10-29 | Republic Day | CPH
uganda | Yoweri Kaguta Museveni | President of the Republic of Uganda | UN || 10-09 | National Day | CPH
ukraine | Volodymyr Zelenskyy | President of Ukraine | UN || 08-24 | Independence Day | CPH
united-arab-emirates | Mohamed bin Zayed Al Nahyan | President of the United Arab Emirates | UN || 12-02 | National Day | CPH
united-kingdom | Charles III | King of the United Kingdom | UN || 06-08 | National Day | CPH
united-states | Donald J. Trump | President of the United States of America | UN || 07-04 | Independence Day | CPH
uruguay | Yamandú Orsi | President of the Oriental Republic of Uruguay | UN || 08-25 | Independence Day | CPH
uzbekistan | Shavkat Mirziyoyev | President of the Republic of Uzbekistan | UN || 09-01 | National Day | SE
vanuatu | Nikenike Vurobaravu | President of the Republic of Vanuatu | UN || 07-30 | National Day | SE
venezuela | Delcy Rodríguez | Acting President of the Bolivarian Republic of Venezuela | UN || 07-05 | Independence Day | CPH
vietnam | Tô Lâm | President of the Socialist Republic of Viet Nam | UN || 09-02 | National Day | CPH
yemen | Rashad Al-Alimi | President of the Presidential Leadership Council of the Republic of Yemen | UN || 05-22 | National Day | CPH
zambia | Hakainde Hichilema | President of the Republic of Zambia | UN || 10-24 | Independence Day | CPH
zimbabwe | Emmerson Mnangagwa | President of the Republic of Zimbabwe | UN || 04-18 | Independence Day | CPH
"""

# What the Steward watches for each nation; never shown on the page.
NOTES = {
    'afghanistan': 'The UN Protocol list of 13 November 2026 names no head of state for Afghanistan. The band shows the National Day only, until the Steward-General decides.',
    'myanmar': 'The UN Protocol list of 13 November 2026 still names Win Myint, while the Union Parliament elected a new President on 3 April 2026. The two do not agree, so the band shows the National Day only, until the Steward-General decides.',
    'andorra': 'Two Co-Princes, the Bishop of Urgell and the President of the French Republic. When the French presidency changes, Andorra changes too.',
    'nicaragua': 'Two Co-Presidents under the constitutional reform of 2025.',
    'san-marino': 'Two Captains Regent, elected every six months and installed on 1 April and 1 October. Their names are added once the Reggenza publishes them; check on each 1 April and 1 October.',
    'bosnia-and-herzegovina': 'The Chair of the Presidency rotates every eight months; the next rotation is due about 16 November 2026.',
    'switzerland': 'The President of the Swiss Confederation changes every 1 January.',
    'united-kingdom': 'The date moves: the King’s Official Birthday, set each year. Confirm the date every January.',
    'israel': 'The date moves: Independence Day follows the Hebrew calendar (5 Iyar). 12 May is the 2027 date; confirm it with the Embassy of Israel and set the next date after each celebration.',
    'holy-see': 'The anniversary of the election of Pope Leo XIV (8 May 2025). The date changes with each pontificate.',
    'micronesia': 'Two government lists disagree: New Zealand MFAT gives 3 November (National Day); other lists give 10 May (Constitution Day). The Steward-General to choose.',
    'india': 'India also celebrates Republic Day on 26 January; the Copenhagen list gives 15 August.',
    'barbados': 'The UN Protocol list of 13 November 2026 still names the previous President; the Official Gazette of Barbados is the source.',
    'norway': 'King Haakon VIII succeeded King Harald V on 28 August 2026; the Royal House of Norway is the source.',
    'denmark': 'The Copenhagen list also gives 26 May, the King’s Birthday.',
    'venezuela': 'The UN Protocol list gives an Acting President; check monthly.',
}

# Official portraits uploaded to the Media Library by the Steward-General (named pn-hos-<slug>). The band uses the
# WordPress "medium" size (about 300 px tall) and crops it to a circle. Only a portrait whose credit and licence are
# known is listed; each credit shows under the name. Never take a photograph of a head of state from the web.
UP = 'https://perfectnations.com/wp-content/uploads/2026/11/'
CC_BY_SA_3 = {'label': 'CC BY-SA 3.0', 'url': 'https://creativecommons.org/licenses/by-sa/3.0/'}
CC_BY_4 = {'label': 'CC BY 4.0', 'url': 'https://creativecommons.org/licenses/by/4.0/'}
PORTRAITS = {
    'rwanda': (UP + 'pn-hos-rwanda-232x300.jpg', 'Maayan Toaf, Government Press Office of Israel', CC_BY_SA_3),
    'brazil': (UP + 'pn-hos-brazil-272x300.jpg', 'Ricardo Stuckert, Presidency of Brazil', None),
    'kenya': (UP + 'pn-hos-kenya-237x300.jpg', 'Government of Kenya', None),
    'cote-divoire': (UP + 'pn-hos-cote-divoire-200x300.jpg', 'Dario Pignatelli, European Union', None),
    'ukraine': (UP + 'pn-hos-ukraine-222x300.jpg', 'President.gov.ua', CC_BY_4),
}

GREET = {
    'Naadam': 'Happy Naadam',
    'The Emperor’s Birthday': 'Felicitations on the Emperor’s Birthday',
    'Anniversary of the Pope’s Election': 'Felicitations to the Holy See',
    'Our Lady of Meritxell Day': 'Happy Meritxell Day',
}


def greeting(label):
    return GREET.get(label) or ('Happy %s' % label)


def rows():
    out = {}
    for line in TABLE.strip().splitlines():
        p = [x.strip() for x in line.split('|')]
        if len(p) != 8:
            raise SystemExit('bad row: %r' % line)
        slug, name, title, hsrc, since, mmdd, label, dsrc = p
        m, d = (int(x) for x in mmdd.split('-'))
        out[slug] = dict(name=name, title=title, hsrc=hsrc, since=since, month=m, day=d, label=label, dsrc=dsrc)
    return out


def src(key):
    label, url = SRC[key]
    return {'label': label, 'url': url}


def main():
    check = '--check' in sys.argv
    index = json.loads((ROOT / 'data' / 'blueprints.json').read_text(encoding='utf-8'))
    names = {x['slug']: x['name'] for x in index['open']}
    table = rows()
    missing = sorted(set(names) - set(table) - {'france'})
    extra = sorted(set(table) - set(names))
    if missing or extra:
        raise SystemExit('missing: %s; not a blueprint: %s' % (missing, extra))
    data = json.loads(OUT.read_text(encoding='utf-8'))
    nations = data.setdefault('nations', {})
    changed = []
    for slug in sorted(names):
        if slug == 'france':
            nations[slug].setdefault('checked', CHECKED)
            continue
        r = table[slug]
        cur = nations.get(slug, {})
        hs = {'title': r['title'], 'name': r['name'], 'portrait': ''}
        if slug in PORTRAITS:
            url, credit, licence = PORTRAITS[slug]
            hs['portrait'], hs['portrait_credit'] = url, credit
            if licence:
                hs['portrait_licence'] = licence
        if r['name'] and ' and ' in r['name'] and slug in ('andorra', 'nicaragua'):
            hs['names'] = r['name'].split(' and ')
        if r['hsrc']:
            hs['source'] = src(r['hsrc'])
        if r['since']:
            hs['since'] = r['since']
        if not r['name']:
            hs = {'title': '', 'name': '', 'portrait': ''}
        nd = {'month': r['month'], 'day': r['day'], 'name': r['label'], 'name_en': r['label'],
              'greeting': greeting(r['label']), 'source': src(r['dsrc'])}
        if slug in ('united-kingdom', 'israel'):
            nd['movable'] = True
        new = dict(cur)
        new['nation'] = names[slug]
        new['head_of_state'] = hs
        new['national_day'] = nd
        new['checked'] = CHECKED
        if NOTES.get(slug):
            new['steward_note'] = NOTES[slug]
        if new != cur:
            changed.append(slug)
        nations[slug] = new
    data['nations'] = {k: nations[k] for k in sorted(nations)}
    data['updated'] = CHECKED
    print('%d nations, %d changed' % (len(data['nations']), len(changed)))
    if not check:
        OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
