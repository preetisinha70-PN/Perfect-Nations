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
san-marino | Gerardo Giovagnoli and William Casali | Captains Regent of the Republic of San Marino | UN | 2026-10-01 | 09-03 | National Day | CPH
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

# Two records for every nation (the Steward-General, 15 November 2026): `head_of_state` and `head_of_government`, and
# `band`, the office the band on the blueprint shows. Both records are kept and checked whichever office the band shows.
#
# The office the band shows: the elected leader who runs the government. Where
# the head of state is a monarch or a ceremonial president (chosen by parliament, or elected by the people while a
# prime minister runs the government), the band shows the prime minister. Presidents who run the government keep the
# band; rulers who are not elected (and leaders of one-party states) stay as they are. Source: the UN Protocol list of
# 13 November 2026, heads of government, English titles, names without honorifics or post-nominals.
# slug | name | title | since (if changed in 2026)
LEADERS = """
albania | Edi Rama | Prime Minister of the Republic of Albania |
andorra | Xavier Espot Zamora | Head of Government of the Principality of Andorra |
antigua-and-barbuda | Gaston Alphonso Browne | Prime Minister of Antigua and Barbuda |
armenia | Nikol Pashinyan | Prime Minister of the Republic of Armenia |
australia | Anthony Albanese | Prime Minister of the Commonwealth of Australia |
austria | Christian Stocker | Federal Chancellor of the Republic of Austria |
bahamas | Philip Edward Davis | Prime Minister of the Commonwealth of The Bahamas |
bangladesh | Tarique Rahman | Prime Minister of the People’s Republic of Bangladesh | 2026-02-17
barbados | Mia Amor Mottley | Prime Minister of Barbados |
belgium | Bart De Wever | Prime Minister of the Kingdom of Belgium |
belize | John Briceño | Prime Minister of Belize |
bhutan | Tshering Tobgay | Prime Minister of the Kingdom of Bhutan |
bosnia-and-herzegovina | Borjana Krišto | Chairwoman of the Council of Ministers of Bosnia and Herzegovina |
bulgaria | Rumen Radev | Prime Minister of the Republic of Bulgaria | 2026-05-08
cabo-verde | Francisco Avelino Vieira de Carvalho | Prime Minister of the Republic of Cabo Verde | 2026-05-17
cambodia | Hun Manet | Prime Minister of the Kingdom of Cambodia |
canada | Mark Carney | Prime Minister of Canada |
croatia | Andrej Plenković | Prime Minister of the Republic of Croatia |
czechia | Andrej Babiš | Prime Minister of the Czech Republic |
denmark | Mette Frederiksen | Prime Minister of Denmark |
dominica | Roosevelt Skerrit | Prime Minister of the Commonwealth of Dominica |
estonia | Kristen Michal | Prime Minister of the Republic of Estonia |
ethiopia | Abiy Ahmed | Prime Minister of the Federal Democratic Republic of Ethiopia |
fiji | Sitiveni Ligamamada Rabuka | Prime Minister of the Republic of Fiji |
finland | Petteri Orpo | Prime Minister of the Republic of Finland |
georgia | Irakli Kobakhidze | Prime Minister of Georgia |
germany | Friedrich Merz | Chancellor of the Federal Republic of Germany |
greece | Kyriakos Mitsotakis | Prime Minister of the Hellenic Republic |
grenada | Dickon Mitchell | Prime Minister of Grenada |
hungary | Péter Magyar | Prime Minister of Hungary | 2026-06-22
iceland | Kristrún Frostadóttir | Prime Minister of Iceland |
india | Narendra Modi | Prime Minister of the Republic of India |
iraq | Ali Falih Al-Zaidi | Prime Minister of the Republic of Iraq | 2026-05-14
ireland | Micheál Martin | Taoiseach of Ireland |
israel | Benjamin Netanyahu | Prime Minister of the State of Israel |
italy | Giorgia Meloni | President of the Council of Ministers of the Italian Republic |
jamaica | Andrew Holness | Prime Minister of Jamaica |
japan | Takaichi Sanae | Prime Minister of Japan |
latvia | Andris Kulbergs | Prime Minister of the Republic of Latvia | 2026-05-28
lebanon | Nawaf Salam | President of the Council of Ministers of the Republic of Lebanon |
lesotho | Samuel Ntsokoane Matekane | Prime Minister of the Kingdom of Lesotho |
liechtenstein | Brigitte Haas | Prime Minister of the Principality of Liechtenstein |
lithuania | Inga Ruginienė | Prime Minister of the Republic of Lithuania |
luxembourg | Luc Frieden | Prime Minister of the Grand Duchy of Luxembourg |
malaysia | Anwar Ibrahim | Prime Minister of Malaysia |
malta | Robert Abela | Prime Minister of the Republic of Malta |
mauritius | Navinchandra Ramgoolam | Prime Minister of the Republic of Mauritius |
moldova | Vasile Tofan | Prime Minister of the Republic of Moldova | 2026-07-22
mongolia | Uchral Nyam-Osor | Prime Minister of Mongolia | 2026-03-30
montenegro | Milojko Spajić | Prime Minister of Montenegro |
morocco | Aziz Akhannouch | Head of Government of the Kingdom of Morocco |
nepal | Balendra Shah | Prime Minister of Nepal | 2026-03-27
netherlands | Rob Jetten | Prime Minister of the Kingdom of the Netherlands | 2026-02-23
new-zealand | Christopher Luxon | Prime Minister of New Zealand |
north-macedonia | Hristijan Mickoski | President of the Government of the Republic of North Macedonia |
norway | Jonas Gahr Støre | Prime Minister of Norway |
pakistan | Muhammad Shehbaz Sharif | Prime Minister of the Islamic Republic of Pakistan |
papua-new-guinea | James Marape | Prime Minister of the Independent State of Papua New Guinea |
poland | Donald Tusk | Prime Minister of the Republic of Poland |
portugal | Luís Montenegro | Prime Minister of the Portuguese Republic |
romania | Luca-Alexandru Niculescu | Prime Minister of Romania |
saint-kitts-and-nevis | Terrance Micheal Drew | Prime Minister of Saint Kitts and Nevis |
saint-lucia | Philip J. Pierre | Prime Minister of Saint Lucia |
saint-vincent-and-the-grenadines | Godwin Friday | Prime Minister of Saint Vincent and the Grenadines | 2025-12-01
samoa | Laaulialemalietoa Leuatea Polataivao Fosi Schmidt | Prime Minister of the Independent State of Samoa |
sao-tome-and-principe | Américo d’Oliveira dos Ramos | Prime Minister of the Democratic Republic of São Tomé and Príncipe |
serbia | Đuro Macut | Prime Minister of the Republic of Serbia |
singapore | Lawrence Wong | Prime Minister of the Republic of Singapore |
slovakia | Robert Fico | Prime Minister of the Slovak Republic |
slovenia | Janez Janša | Prime Minister of the Republic of Slovenia | 2026-06-04
solomon-islands | Matthew Cooper Wale | Prime Minister of Solomon Islands |
somalia | Hamza Abdi Barre | Prime Minister of the Federal Republic of Somalia |
spain | Pedro Sánchez | President of the Government of Spain |
sweden | Ulf Kristersson | Prime Minister of Sweden |
thailand | Anutin Charnvirakul | Prime Minister of the Kingdom of Thailand |
timor-leste | Xanana Gusmão | Prime Minister of the Democratic Republic of Timor-Leste |
togo | Faure Gnassingbé | President of the Council of Ministers of the Togolese Republic |
tonga | Lord Fakafanua | Prime Minister of the Kingdom of Tonga |
trinidad-and-tobago | Kamla Persad-Bissessar | Prime Minister of the Republic of Trinidad and Tobago |
tuvalu | Feleti Penitala Teo | Prime Minister of Tuvalu |
united-kingdom | Andrew Burnham | Prime Minister of the United Kingdom of Great Britain and Northern Ireland | 2026-07-20
vanuatu | Jotham Napat | Prime Minister of the Republic of Vanuatu |
"""

# Heads of government where the band shows the head of state (a president who leads, a ruler, a one-party state).
# Source: the UN Protocol list of 13 November 2026, English titles. Nations in neither table have no separate head of
# government: the head of state leads the government ("Same as Head of State" or "No Prime Minister" on the UN list).
OTHER_HOG = """
algeria | Sifi Ghrieb | Prime Minister of the People’s Democratic Republic of Algeria |
azerbaijan | Ali Asadov | Prime Minister of the Republic of Azerbaijan |
bahrain | Salman bin Hamad Al Khalifa | Crown Prince and Prime Minister of the Kingdom of Bahrain |
belarus | Aleksandr Turchin | Prime Minister of the Republic of Belarus |
burkina-faso | Rimtalba Jean Emmanuel Ouedraogo | Prime Minister, Head of Government of Burkina Faso |
burundi | Nestor Ntahontuye | Prime Minister of the Republic of Burundi | 2025-08-05
cameroon | Joseph Dion Ngute | Prime Minister, Head of Government of the Republic of Cameroon |
central-african-republic | Félix Moloua | Prime Minister, Head of Government of the Central African Republic |
chad | Allah-Maye Halina | Prime Minister, Head of Government of the Republic of Chad |
china | Li Qiang | Premier of the State Council of the People’s Republic of China |
cote-divoire | Robert Beugré Mambé | Prime Minister, Head of Government of Côte d’Ivoire |
cuba | Manuel Marrero Cruz | Prime Minister of the Republic of Cuba |
djibouti | Abdoulkader Kamil Mohamed | Prime Minister of the Republic of Djibouti |
dr-congo | Judith Suminwa Tuluka | Prime Minister, Head of Government of the Democratic Republic of the Congo |
egypt | Moustafa Kamal Madbouly | Prime Minister of the Arab Republic of Egypt |
equatorial-guinea | Manuel Osa Nsue Nsuga | Prime Minister of the Republic of Equatorial Guinea |
eswatini | Russell Mmiso Dlamini | Prime Minister of the Kingdom of Eswatini |
france | Sébastien Lecornu | Prime Minister of the French Republic |
guinea | Amadou Oury Bah | Prime Minister, Head of Government of the Republic of Guinea |
guinea-bissau | Ilídio Vieira Té | Prime Minister of the Republic of Guinea-Bissau |
guyana | Mark Phillips | Prime Minister of the Co-operative Republic of Guyana |
haiti | Alix Didier Fils-Aimé | Prime Minister of the Republic of Haiti |
holy-see | Pietro Parolin | Secretary of State of the Holy See |
jordan | Jafar Hassan | Prime Minister of the Hashemite Kingdom of Jordan |
kazakhstan | Olzhas Bektenov | Prime Minister of the Republic of Kazakhstan |
kuwait | Ahmad Abdullah Al-Ahmad Al-Sabah | Prime Minister of the State of Kuwait |
kyrgyzstan | Adylbek Kasymaliev | Chairman of the Cabinet of Ministers of the Kyrgyz Republic |
laos | Saleumxay Kommasith | Prime Minister of the Lao People’s Democratic Republic |
libya | Abdulhamid Al Dabiba | Prime Minister of the Government of National Unity of Libya |
madagascar | Mamitiana Rajaonarison | Prime Minister, Head of Government of the Refoundation of the Republic of Madagascar |
mali | Abdoulaye Maïga | Prime Minister, Head of Government of the Republic of Mali |
mauritania | Moktar Ould Djay | Prime Minister of the Islamic Republic of Mauritania |
monaco | Christophe Mirmand | Minister of State, Head of Government of the Principality of Monaco |
mozambique | Maria Benvinda Delfina Levi | Prime Minister of the Republic of Mozambique |
namibia | Elijah Ngurare | Prime Minister of the Republic of Namibia |
niger | Lamine Zeine Ali Mahaman | Prime Minister of the Transitional Government of the Republic of Niger |
north-korea | Pak Thae Song | Premier of the Cabinet of the Democratic People’s Republic of Korea |
palestine | Mohammad Mustafa | Prime Minister of the State of Palestine |
peru | Luis Fernando Galarreta Velarde | President of the Council of Ministers of the Republic of Peru |
qatar | Mohammed bin Abdulrahman bin Jassim Al-Thani | Prime Minister of the State of Qatar |
republic-of-congo | Anatole Collinet Makosso | Prime Minister of the Republic of the Congo |
russia | Mikhail Mishustin | Prime Minister of the Russian Federation |
rwanda | Justin Nsengiyumva | Prime Minister of the Republic of Rwanda |
saudi-arabia | Mohammed bin Salman bin Abdulaziz Al Saud | Crown Prince and Prime Minister of the Kingdom of Saudi Arabia |
senegal | Ahmadou Al Amine Mohamed Lo | Prime Minister of the Republic of Senegal | 2026-05-25
south-korea | Han Seong-sook | Prime Minister of the Republic of Korea |
sri-lanka | Harini Amarasuriya | Prime Minister of the Democratic Socialist Republic of Sri Lanka |
sudan | Kamil El-Tayeb Idris | Transitional Prime Minister of the Republic of the Sudan |
tajikistan | Kohir Rasulzoda | Prime Minister of the Republic of Tajikistan |
tanzania | Mwigulu Lameck Nchemba | Prime Minister of the United Republic of Tanzania |
tunisia | Sarra Zaafrani Zenzri | Head of Government of the Republic of Tunisia |
uganda | Robinah Nabbanja | Prime Minister of the Republic of Uganda |
ukraine | Sergii Koretskyi | Prime Minister of Ukraine | 2026-07-16
united-arab-emirates | Mohammed bin Rashid Al Maktoum | Vice-President and Prime Minister of the United Arab Emirates |
uzbekistan | Abdulla Aripov | Prime Minister of the Republic of Uzbekistan |
vietnam | Le Minh Hung | Prime Minister of the Socialist Republic of Viet Nam |
yemen | Shaya Mohsen Al-Zindani | Prime Minister of the Republic of Yemen |
"""

# What the Steward watches for each nation; never shown on the page.
NOTES = {
    'tanzania': 'The band shows the President, Samia Suluhu Hassan, as confirmed by the Steward-General on 16 November 2026. The Prime Minister, Mwigulu Lameck Nchemba, is kept on the head-of-government record.',
    'rwanda': 'The band shows the President, Paul Kagame, as confirmed by the Steward-General on 16 November 2026. The Prime Minister, Justin Nsengiyumva, is kept on the head-of-government record.',
    'afghanistan': 'The UN Protocol list of 13 November 2026 names no head of state for Afghanistan. The band shows the National Day only, until the Steward-General decides.',
    'myanmar': 'The UN Protocol list of 13 November 2026 still names Win Myint, while the Union Parliament elected a new President on 3 April 2026. The two do not agree, so the band shows the National Day only, until the Steward-General decides.',
    'andorra': 'The band shows the Head of Government. The two Co-Princes are the Bishop of Urgell and the President of the French Republic.',
    'nicaragua': 'Two Co-Presidents under the constitutional reform of 2025.',
    'san-marino': 'Two Captains Regent, elected every six months and installed on 1 April and 1 October; the next pair takes office on 1 April 2027.',
    'bosnia-and-herzegovina': 'The band shows the Chairwoman of the Council of Ministers. The Chair of the Presidency rotates every eight months.',
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
    'burundi': 'Prime Minister Nestor Ntahontuye, appointed 5 August 2025; the name was confirmed by the Steward-General against official sources on 15 November 2026. The UN Protocol list prints "Ntahontuye Ntahontuye", a repeated surname.',
    'gabon': 'Under the new constitution the President is both Head of State and Head of Government (confirmed by the Steward-General against official sources on 15 November 2026). The UN Protocol list still names a Prime Minister, Raymond Ndong Sima, from the earlier arrangement.',
    'syria': 'The President leads the government; the UN Protocol list names no Prime Minister.',
}

# Official portraits uploaded to the Media Library by the Steward-General (named pn-hos-<slug>). The band uses the
# WordPress "medium" size (about 300 px tall) and crops it to a circle. Only a portrait whose credit and licence are
# known is listed; each credit shows under the name. Never take a photograph of a head of state from the web.
UP = 'https://perfectnations.com/wp-content/uploads/2026/11/'
CC_BY_SA_3 = {'label': 'CC BY-SA 3.0', 'url': 'https://creativecommons.org/licenses/by-sa/3.0/'}
CC_BY_4 = {'label': 'CC BY 4.0', 'url': 'https://creativecommons.org/licenses/by/4.0/'}
CC_BY_2 = {'label': 'CC BY 2.0', 'url': 'https://creativecommons.org/licenses/by/2.0/'}
CC_BY_SA_4 = {'label': 'CC BY-SA 4.0', 'url': 'https://creativecommons.org/licenses/by-sa/4.0/'}
PD = {'label': 'public domain'}
CC_BY_SA_2 = {'label': 'CC BY-SA 2.0', 'url': 'https://creativecommons.org/licenses/by-sa/2.0/'}
CC_BY_2_5_DK = {'label': 'CC BY 2.5 DK', 'url': 'https://creativecommons.org/licenses/by/2.5/dk/deed.en'}
GOJ = {'label': 'Government of Japan Standard Terms of Use 2.0, compatible with CC BY 4.0'}
CC_BY_3_CL = {'label': 'CC BY 3.0 CL', 'url': 'https://creativecommons.org/licenses/by/3.0/cl/'}
CC_BY_SA_2_5 = {'label': 'CC BY-SA 2.5', 'url': 'https://creativecommons.org/licenses/by-sa/2.5/'}
# Portraits by office (the Steward-General, 15 November 2026): files named pn-hos-<slug> show the head of state, files
# named pn-hog-<slug> the head of government. PORTRAITS holds heads of state; PORTRAITS_HOG heads of government.
# Where one person holds both offices (Brazil, Kenya, the United States, Mexico, Ghana, the Philippines, Cyprus, South
# Africa, Oman), the portrait is a pn-hog- file, copied on 15 November 2026 from the pn-hos- upload, which is kept.
PORTRAITS = {
    'rwanda': (UP + 'pn-hos-rwanda-232x300.jpg', 'Maayan Toaf, Government Press Office of Israel', CC_BY_SA_3),
    'brazil': (UP + 'pn-hog-brazil-272x300.jpg', 'Ricardo Stuckert, Presidency of Brazil', None),
    'kenya': (UP + 'pn-hog-kenya-237x300.jpg', 'Government of Kenya', PD),
    'cote-divoire': (UP + 'pn-hos-cote-divoire-200x300.jpg', 'Dario Pignatelli, European Union', None),
    'ukraine': (UP + 'pn-hos-ukraine-222x300.jpg', 'President.gov.ua', CC_BY_4),
    'india': (UP + 'pn-hos-india-1-218x300.jpg', 'President’s Secretariat, Government of India', {'label': 'GODL-India'}),
    'germany': (UP + 'pn-hos-germany-225x300.jpg', 'Jnwnklr', {'label': 'CC BY-SA 4.0', 'url': 'https://creativecommons.org/licenses/by-sa/4.0/'}),
    'finland': (UP + 'pn-hos-finland-224x300.jpg', 'Jaan Kynnap', CC_BY_4),
    'singapore': (UP + 'pn-hos-singapore-225x300.jpg', 'Actuall7', CC_BY_4),
    'mongolia': (UP + 'pn-hos-mongolia-225x300.jpg', 'President.mn', CC_BY_4),
    # second batch, 15 November 2026 evening: the leader shown on the band, with a known credit and licence
    'france': (UP + 'pn-hos-france-241x300.jpg', 'Dati Bendo, European Commission', CC_BY_4),
    'united-states': (UP + 'pn-hog-united-states-240x300.jpg', 'Daniel Torok, The White House', PD),
    'mexico': (UP + 'pn-hog-mexico-202x300.jpg', 'EneasMx', CC_BY_4),
    'ghana': (UP + 'pn-hog-ghana-298x300.png', 'U.S. Department of State', PD),
    'tanzania': (UP + 'pn-hos-tanzania-300x300.jpg', 'U.S. Embassy Dar es Salaam', PD),
    'philippines': (UP + 'pn-hos-philippines-185x300.jpg', 'Department of Foreign Affairs of the Philippines', PD),
    'cyprus': (UP + 'pn-hog-cyprus-243x300.jpg', 'European Union 2023, European Parliament / Laia Ros', None),
    'cuba': (UP + 'pn-hos-cuba-215x300.jpg', 'Ricardo Stuckert, Presidency of Brazil', CC_BY_2),
    # Commons: Cyril_Ramaphosa_in_2026.jpg (Planalto, 9 March 2026)
    'south-africa': (UP + 'pn-hog-south-africa-222x300.jpg', 'Ricardo Stuckert, Presidency of Brazil, cropped', CC_BY_SA_4),
    'united-arab-emirates': (UP + 'pn-hos-united-arab-emirates-250x300.jpg', 'Alan Santos, Presidency of Brazil', CC_BY_2),
    'oman': (UP + 'pn-hos-oman-250x300.jpg', 'Prime Minister’s Office, Government of India', {'label': 'GODL-India'}),
    # third batch: licences read from the Wikimedia Commons file pages by the Steward-General, 15 November 2026
    'nigeria': (UP + 'pn-hog-nigeria-240x300.jpg', 'Nosa Asemota, cropped', CC_BY_SA_4),
    'zambia': (UP + 'pn-hog-zambia-300x200.jpg', 'TheophilusMaurice, cropped', CC_BY_SA_4),
    # official portrait (Commons: Retrato_oficial_de_Presidente_Bernardo_Arévalo.jpg), Guatemala government work
    'guatemala': (UP + 'pn-hog-guatemala-194x300.jpg', 'Daniel Hernández-Salazar, Government of Guatemala', PD),
    'uganda': (UP + 'pn-hos-uganda-228x300.jpg', 'Prime Minister’s Office, Government of India', {'label': 'GODL-India'}),
    # Commons: extracted from "Mattarella Lourenço 2023.jpg"; Quirinale.it permission (VRT) for any use with attribution
    'angola': (UP + 'pn-hog-angola-217x300.jpg', 'Presidency of the Italian Republic (Quirinale.it), cropped', {'label': 'free use with attribution'}),
    # fourth batch (15 November 2026, night): credits and licences from the uploads' captions and file data
    'dr-congo': (UP + 'pn-hos-democratic-republic-of-the-congo-232x300.jpg', 'Freddie Everett, U.S. Department of State', PD),
    'botswana': (UP + 'perfect-nations-official-portr-224x300.jpg', 'Freddie Everett, U.S. Department of State', PD),
    'comoros': (UP + 'brazilian-leaders-portrait-240x300.jpg', 'Ricardo Stuckert, Presidency of Brazil', CC_BY_2),
    'namibia': (UP + 'pn-hos-namibia-242x300.jpg', 'Prime Minister’s Office, Government of India', {'label': 'GODL-India'}),
    'micronesia': (UP + 'man-near-private-jet-smile-250x300.jpg', 'Joshua Martin, U.S. Navy, 2008', PD),
    # Commons: Retrato_oficial_Presidente_Milei.png
    'argentina': (UP + 'pn-hog-argentina-209x300.png', 'Government of Argentina', CC_BY_4),
    # Commons: Luis_Abinader_(25-04-2024).jpg (16 November 2026)
    'dominican-republic': (UP + 'pn-hog-dominican-republic-225x300.jpg', 'Chairman of the Joint Chiefs of Staff (U.S.), cropped', CC_BY_2),
    'kyrgyzstan': (UP + 'pn-hos-kyrgyzstan-225x300.jpg', 'Ermek Sydykov, Press Service of the President of Kyrgyzstan, cropped', CC_BY_SA_4),
    # sixth batch (17 November 2026): the Steward-General's pn-hog uploads; credits and licences from their captions
    # (citing the Wikimedia Commons files) and their file data
    'ecuador': (UP + 'pn-hog-ecuador-235x300.jpg', 'Fernando Sandoval, National Assembly of Ecuador, 2022', CC_BY_SA_2),
    'indonesia': (UP + 'pn-hog-indonesia-226x300.jpg', 'Ministry of State Secretariat, Republic of Indonesia', {'label': 'public domain under Indonesian law'}),
    'panama': (UP + 'pn-hog-panama-215x300.jpg', 'Ricardo Stuckert, Presidency of Brazil, cropped', CC_BY_SA_2),
    'paraguay': (UP + 'pn-hog-paraguay-235x300.jpg', 'Wang Yu Ching, Office of the President, Taiwan, cropped', CC_BY_4),
    'maldives': (UP + 'pn-hog-maldives-200x300.jpg', 'The President’s Office, Maldives', CC_BY_4),
    'sri-lanka': (UP + 'pn-hog-sri-lanka-218x300.jpg', 'Cabinet Public Affairs Office, Government of Japan, cropped', GOJ),
    'kazakhstan': (UP + 'pn-hog-kazakhstan-225x300.jpg', 'Press Service of the President of Azerbaijan, cropped', CC_BY_4),
    # White House photos: public domain as U.S. government works; the White House adds a courtesy notice (personal
    # use, no suggestion of endorsement). The Steward-General decided to use them (16 November 2026, 22:54 New York).
    'senegal': (UP + 'pn-hog-senegal-225x300.jpg', 'Molly Riley, The White House, cropped', PD),
    'south-korea': (UP + 'pn-hog-south-korea-214x300.jpg', 'The White House, cropped', PD),
    'liberia': (UP + 'pn-hos-liberia-234x300.jpg', 'Daniel Torok, The White House, cropped', PD),
    'cameroon': (UP + 'prominent-leader-portrait-233x300.jpg', 'Adam Schultz, The White House, 2022, cropped', PD),
    'eswatini': (UP + 'perfect-nations-leader-portrai-214x300.jpg', 'Lawrence Jackson, The White House, 2009, cropped', PD),
    # seventh batch (17 November 2026): the Steward-General's pn-hog uploads of 16 and 17 November; credits and licences
    # from their captions (citing the Wikimedia Commons files) and their file data
    'uzbekistan': (UP + 'pn-hog-uzbekistan-195x300.jpg', 'Press Service of the President of Uzbekistan, 2018, cropped', CC_BY_SA_4),
    'azerbaijan': (UP + 'pn-hog-azerbaijan-239x300.jpg', 'Press Service of the President of Azerbaijan, 2018, cropped', CC_BY_4),
    'turkiye': (UP + 'pn-hog-turkey-300x185.jpg', 'Presidential Executive Office of Russia (kremlin.ru), 2019', CC_BY_4),
    'el-salvador': (UP + 'pn-hog-el-salvador-200x300.jpg', 'AndreX, 2019', CC_BY_SA_4),
    'chile': (UP + 'pn-hog-chile-238x300.jpg', 'Government of Chile', CC_BY_3_CL),
    'bolivia': (UP + 'pn-hog-bolivia-235x300.jpg', 'Press Office, Presidency of Chile, cropped', CC_BY_3_CL),
    'guyana': (UP + 'pn-hog-guyana-257x300.jpg', 'Alan Santos, Presidency of Brazil, 2022, cropped', CC_BY_2),
    # Commons: Retrato_presidente_Yamandú_Orsi_(cropped).jpg, the 2025 official portrait (176 x 235, enough for the
    # 72 px circle); the file data names Ernesto Ryan. The 2014 photograph (pn-hog-uruguay-1) is kept in the library.
    'uruguay': (UP + 'pn-hog-uruguay.jpg', 'Ernesto Ryan, Presidency of Uruguay, cropped', CC_BY_SA_2_5),
    'suriname': (UP + 'pn-hog-suriname-212x300.jpg', 'Ricardo Stuckert, Presidency of Brazil, cropped', CC_BY_SA_4),
    'mozambique': (UP + 'pn-hog-mozambique-224x300.jpg', 'Ricardo Stuckert, Presidency of Brazil, cropped', CC_BY_SA_4),
    'costa-rica': (UP + 'pn-hog-costa-rica-200x300.jpg', 'Esteban Rojas Saurez, Legislative Assembly of Costa Rica, cropped', {'label': 'public domain in Costa Rica'}),
    # head of state on record (the band shows the Prime Minister)
    'albania': (UP + 'pn-hos-albania-296x300.jpg', 'Presidential Press and Information Office of Azerbaijan, cropped', CC_BY_4),
}
PORTRAITS_HOG = {
    'india': (UP + 'pn-hos-india-240x300.jpg', 'Prime Minister’s Office, Government of India', {'label': 'GODL-India'}),
    # licence confirmed by the Steward-General from the Wikimedia Commons file page, 15 November 2026
    'cambodia': (UP + 'pn-hog-cambodia-229x300.jpg', 'Government of Japan', GOJ),
    'japan': (UP + 'pn-hog-japan-242x300.jpg', 'Government of Japan', GOJ),
    # Commons gives CC BY 3.0 IT; the Italian Government's site now gives CC BY-NC-SA 3.0 IT for its images. The
    # Steward-General chose the Commons licence on 15 November 2026.
    'italy': (UP + 'pn-hog-italy-228x300.jpg', 'Presidency of the Council of Ministers of Italy', {'label': 'CC BY 3.0 IT', 'url': 'https://creativecommons.org/licenses/by/3.0/it/'}),
    # Commons: Edi_Rama,_press_conference,_ITB_2025,_Berlin_(ITB56291)_(cropped_1).jpg
    'albania': (UP + 'mature-man-suit-portrait-225x300.jpg', 'Matti Blume, cropped', CC_BY_SA_4),
    # Commons: Luxon_portrait_2024.png
    'new-zealand': (UP + 'pn-hog-new-zealand-237x300.png', 'New Zealand Government', CC_BY_4),
    # fifth batch (16 November 2026): licences from the Steward-General's captions, citing the Commons files
    'belgium': (UP + 'pn-hog-belgium-216x300.jpg', 'Dati Bendo, European Union, cropped', CC_BY_4),
    # Commons: 100226-sanchez-biografia4.jpg; La Moncloa allows any use, commercial included, with attribution
    'spain': (UP + 'pn-hog-spain-2026-300x200.jpg', 'Pool Moncloa / Carlos Spottorno, Ministry of the Presidency, Government of Spain', {'label': 'free use with attribution'}),
    'poland': (UP + 'pn-hog-poland-200x300.jpg', 'Tomasz Leśniowski', CC_BY_SA_4),
    'ireland': (UP + 'pn-hog-ireland-255x300.jpg', 'Houses of the Oireachtas', CC_BY_4),
    'denmark': (UP + 'pn-hog-denmark-300x266.jpg', 'Pietro Naj-Oleari, European Parliament, cropped', CC_BY_4),
    'greece': (UP + 'pn-hog-greece-228x300.jpg', 'Yorgos Karahalis, European Union, cropped', CC_BY_4),
    # sixth batch (17 November 2026)
    'luxembourg': (UP + 'pn-hog-luxembourg-225x300.jpg', 'Finnish Prime Minister’s Office, cropped', CC_BY_2),
    'croatia': (UP + 'pn-hog-croatia-225x300.jpg', 'Claudio Centonze, European Union, cropped', CC_BY_4),
    'iceland': (UP + 'pn-hog-iceland-225x300.jpg', 'Dati Bendo, European Union, cropped', CC_BY_4),
    'malta': (UP + 'pn-hog-malta-225x300.jpg', 'Office of the Prime Minister of Malta, cropped', CC_BY_SA_4),
    'slovakia': (UP + 'pn-hog-slovakia-215x300.jpg', 'Christophe Licoppe, European Union', CC_BY_4),
    'austria': (UP + 'pn-hog-austria-225x300.jpg', 'Michael Gruber, Austrian Foreign Ministry, cropped', CC_BY_2),
    'singapore': (UP + 'pn-hog-singapore-225x300.jpg', 'Cabinet Public Relations Office, Government of Japan, cropped', GOJ),
    'norway': (UP + 'pn-hog-norway-200x300.jpg', 'Johannes Jansson, norden.org, 2011', CC_BY_2_5_DK),
    'australia': (UP + 'pn-hog-australia-219x300.jpg', 'Australian Government, cropped', CC_BY_4),
    # sixth batch (16 November 2026): licences from the Steward-General's captions, citing the Commons files
    # Commons: Petteri-Orpo-01_(cropped).jpg; an upright crop of the same official portrait, for the circle
    'finland': (UP + 'pn-hog-finland-214x300.jpg', 'Lauri Heikkinen, Finnish Prime Minister’s Office, cropped', CC_BY_4),
    # Commons: Kristen_Michal.jpg (2012 government portrait, cropped on Commons in 2024)
    'estonia': (UP + 'pn-hog-estonia-227x300.jpg', 'Kaupo Kikkas, Estonian Government Office, cropped', {'label': 'CC BY 3.0 EE', 'url': 'https://creativecommons.org/licenses/by/3.0/ee/deed.en'}),
    # Commons: Luís_Montenegro.jpg (EPP summit, 20 October 2022)
    'portugal': (UP + 'pn-hog-portugal-202x300.jpg', 'Nicolas Lobet, European People’s Party, cropped', CC_BY_2),
    'sweden': (UP + 'professional-speech-navy-suit-200x300.jpg', 'Christophe Licoppe, European Union', CC_BY_4),
    'canada': (UP + 'pn-hog-canada-251x300.jpg', 'Prime Minister of Canada', {'label': 'CC BY 3.0', 'url': 'https://creativecommons.org/licenses/by/3.0/'}),
    # seventh batch (17 November 2026)
    'montenegro': (UP + 'pn-hog-montenegro-224x300.jpg', 'Lukasz Kobus, European Union, 2023, cropped', CC_BY_4),
    'north-macedonia': (UP + 'pn-hog-north-macedonia-227x300.jpg', 'Government of North Macedonia, 2024, cropped', CC_BY_SA_4),
    'serbia': (UP + 'pn-hog-serbia-225x300.jpg', 'Ministry of Defence of Serbia', CC_BY_SA_4),
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
    def hog_table(text):
        out = {}
        for line in text.strip().splitlines():
            p = [x.strip() for x in line.split('|')]
            if len(p) != 4 or p[0] not in names:
                raise SystemExit('bad head-of-government row: %r' % line)
            out[p[0]] = dict(name=p[1], title=p[2], since=p[3])
        return out
    leaders = hog_table(LEADERS)
    others = hog_table(OTHER_HOG)
    both = set(leaders) & set(others)
    if both:
        raise SystemExit('in both tables: %s' % sorted(both))

    def hog_record(slug):
        l = leaders.get(slug) or others.get(slug)
        if not l:
            return {'same_as_head_of_state': True}
        rec = {'title': l['title'], 'name': l['name'], 'portrait': '', 'source': src('UN')}
        if l['since']:
            rec['since'] = l['since']
        return rec

    def put_portrait(rec, table, slug):
        if rec.get('same_as_head_of_state'):
            return
        for k in ('portrait_credit', 'portrait_licence'):
            rec.pop(k, None)
        rec['portrait'] = rec.get('portrait', '') if slug not in table else ''
        if slug in table and rec.get('name'):
            url, credit, licence = table[slug]
            rec['portrait'], rec['portrait_credit'] = url, credit
            if licence:
                rec['portrait_licence'] = licence
    missing = sorted(set(names) - set(table) - {'france'})
    extra = sorted(set(table) - set(names))
    if missing or extra:
        raise SystemExit('missing: %s; not a blueprint: %s' % (missing, extra))
    data = json.loads(OUT.read_text(encoding='utf-8'))
    nations = data.setdefault('nations', {})
    changed = []
    for slug in sorted(names):
        if slug == 'france':
            fr = nations[slug]
            fr.setdefault('checked', CHECKED)
            put_portrait(fr['head_of_state'], PORTRAITS, slug)
            fr['head_of_government'] = hog_record(slug)
            put_portrait(fr['head_of_government'], PORTRAITS_HOG, slug)
            fr['band'] = 'head_of_state'
            fr.pop('leader', None)
            continue
        r = table[slug]
        cur = nations.get(slug, {})
        hs = {'title': r['title'], 'name': r['name'], 'portrait': ''}
        if r['name'] and ' and ' in r['name'] and slug in ('andorra', 'nicaragua', 'san-marino'):
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
        hg = {'title': '', 'name': '', 'portrait': ''} if not r['name'] else hog_record(slug)
        put_portrait(hs, PORTRAITS, slug)
        put_portrait(hg, PORTRAITS_HOG, slug)
        new = dict(cur)
        new['nation'] = names[slug]
        new['head_of_state'] = hs
        new['head_of_government'] = hg
        new['band'] = 'head_of_government' if slug in leaders else 'head_of_state'
        new.pop('leader', None)
        new['national_day'] = nd
        new['checked'] = CHECKED
        if NOTES.get(slug):
            new['steward_note'] = NOTES[slug]
        if new != cur:
            changed.append(slug)
        nations[slug] = new
    data['nations'] = {k: nations[k] for k in sorted(nations)}
    data['updated'] = CHECKED
    data['note'] = ('Protocol facts for each blueprint: its head of state, its head of government (or same_as_head_of_state where '
                    'one person holds both offices), band (the office the band on the blueprint shows), its National Day and the offices '
                    'that receive the National Day letters. The band shows the elected leader who runs the government (the Steward-General, '
                    '15 November 2026); both records are kept whichever it shows. Kept by the Blueprints Steward, who checks both offices once '
                    'a month, and each nation again 15 days before its National Day. Portraits are supplied by the Steward-General: '
                    'pn-hos-<nation> files for heads of state, pn-hog-<nation> files for heads of government, each with its credit and licence; '
                    'until one is supplied the band shows the initials.')
    print('%d nations, %d changed' % (len(data['nations']), len(changed)))
    if not check:
        OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
