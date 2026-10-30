"""俱乐部主表（含地理坐标与队徽来源）以及引援/地理派生查询。"""

import os

from .dataset import PLAYERS
from .i18n import CLUB_NAME_ZH, NATION_ZH, POSITION_ZH
from .periods import period_end, period_start

CLUBS = {
    # --- Spain ---
    "Real Madrid":      {"club_id":"c01","zh_name":"皇家马德里","en_name":"Real Madrid CF","city":"Madrid","region":"Community of Madrid","stadium":"Santiago Bernabéu","country":"Spain","league":"LaLiga","lat":40.45,"lng":-3.69,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/6tnDq9REYo","transfermarkt_club_id":418},
    "Atletico Madrid":  {"club_id":"c02","zh_name":"马德里竞技","en_name":"Atlético Madrid","city":"Madrid","region":"Community of Madrid","stadium":"Metropolitano","country":"Spain","league":"LaLiga","lat":40.44,"lng":-3.60,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/YYze785Ong","transfermarkt_club_id":13},
    "Barcelona":        {"club_id":"c03","zh_name":"巴塞罗那","en_name":"FC Barcelona","city":"Barcelona","region":"Catalonia","stadium":"Spotify Camp Nou","country":"Spain","league":"LaLiga","lat":41.36,"lng":2.10,"sportsapi_team_id":132,"fclogo_url":"https://aka.doubaocdn.com/s/ZmbTTNmm7q","transfermarkt_club_id":None},
    "Villarreal":       {"club_id":"c04","zh_name":"比利亚雷亚尔","en_name":"Villarreal CF","city":"Villarreal","region":"Valencian Community","stadium":"Estadio de la Cerámica","country":"Spain","league":"LaLiga","lat":39.94,"lng":-0.10,"sportsapi_team_id":133,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- England ---
    "Manchester City":  {"club_id":"c05","zh_name":"曼城","en_name":"Manchester City","city":"Manchester","region":"Greater Manchester","stadium":"Etihad Stadium","country":"England","league":"Premier League","lat":53.48,"lng":-2.24,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/vFnFooqzg7","transfermarkt_club_id":281},
    "Manchester Utd":   {"club_id":"c06","zh_name":"曼联","en_name":"Manchester United","city":"Trafford","region":"Greater Manchester","stadium":"Old Trafford","country":"England","league":"Premier League","lat":53.46,"lng":-2.29,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/JfUaofAsmo","transfermarkt_club_id":985},
    "Liverpool":        {"club_id":"c07","zh_name":"利物浦","en_name":"Liverpool FC","city":"Liverpool","region":"Merseyside","stadium":"Anfield","country":"England","league":"Premier League","lat":53.43,"lng":-2.96,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/LUVSbxiDFk","transfermarkt_club_id":31},
    "Arsenal":          {"club_id":"c08","zh_name":"阿森纳","en_name":"Arsenal FC","city":"London","region":"Greater London","stadium":"Emirates Stadium","country":"England","league":"Premier League","lat":51.55,"lng":-0.11,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/JVxf9Up3U2","transfermarkt_club_id":11},
    "Chelsea":          {"club_id":"c09","zh_name":"切尔西","en_name":"Chelsea FC","city":"London","region":"Greater London","stadium":"Stamford Bridge","country":"England","league":"Premier League","lat":51.48,"lng":-0.19,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/tXt9Hinbm6","transfermarkt_club_id":631},
    "Tottenham":        {"club_id":"c10","zh_name":"热刺","en_name":"Tottenham Hotspur","city":"London","region":"Greater London","stadium":"Tottenham Hotspur Stadium","country":"England","league":"Premier League","lat":51.60,"lng":-0.07,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/TOzXh3veDz","transfermarkt_club_id":148},
    "Aston Villa":      {"club_id":"c11","zh_name":"阿斯顿维拉","en_name":"Aston Villa","city":"Birmingham","region":"West Midlands","stadium":"Villa Park","country":"England","league":"Premier League","lat":52.51,"lng":-1.89,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/Sg96IZEP4l","transfermarkt_club_id":405},
    "Birmingham City":  {"club_id":"c12","zh_name":"伯明翰城","en_name":"Birmingham City","city":"Birmingham","region":"West Midlands","stadium":"St Andrew's","country":"England","league":"Championship","lat":52.49,"lng":-1.87,"sportsapi_team_id":1,"fclogo_url":None,"transfermarkt_club_id":None},
    "Newcastle":        {"club_id":"c13","zh_name":"纽卡斯尔联","en_name":"Newcastle United","city":"Newcastle upon Tyne","region":"Tyne and Wear","stadium":"St James' Park","country":"England","league":"Premier League","lat":54.97,"lng":-1.62,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/oIbIWR5Zzh","transfermarkt_club_id":762},
    "Southampton":      {"club_id":"c14","zh_name":"南安普顿","en_name":"Southampton FC","city":"Southampton","region":"Hampshire","stadium":"St Mary's Stadium","country":"England","league":"Premier League","lat":50.91,"lng":-1.39,"sportsapi_team_id":21,"fclogo_url":None,"transfermarkt_club_id":None},
    "Celtic":           {"club_id":"c15","zh_name":"凯尔特人","en_name":"Celtic FC","city":"Glasgow","region":"Scotland","stadium":"Celtic Park","country":"Scotland","league":"Scottish Prem.","lat":55.85,"lng":-4.26,"sportsapi_team_id":754,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- Germany ---
    "Bayern Munich":    {"club_id":"c16","zh_name":"拜仁慕尼黑","en_name":"Bayern Munich","city":"Munich","region":"Bavaria","stadium":"Allianz Arena","country":"Germany","league":"Bundesliga","lat":48.14,"lng":11.57,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/MVQz50o7Rh","transfermarkt_club_id":27},
    "Dortmund":         {"club_id":"c17","zh_name":"多特蒙德","en_name":"Borussia Dortmund","city":"Dortmund","region":"North Rhine-Westphalia","stadium":"Signal Iduna Park","country":"Germany","league":"Bundesliga","lat":51.51,"lng":7.46,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/UDh2jhK9V3","transfermarkt_club_id":16},
    "Bayer Leverkusen": {"club_id":"c18","zh_name":"勒沃库森","en_name":"Bayer Leverkusen","city":"Leverkusen","region":"North Rhine-Westphalia","stadium":"BayArena","country":"Germany","league":"Bundesliga","lat":51.04,"lng":7.00,"sportsapi_team_id":333,"fclogo_url":None,"transfermarkt_club_id":None},
    "Wolfsburg":        {"club_id":"c19","zh_name":"沃尔夫斯堡","en_name":"VfL Wolfsburg","city":"Wolfsburg","region":"Lower Saxony","stadium":"Volkswagen Arena","country":"Germany","league":"Bundesliga","lat":52.43,"lng":10.78,"sportsapi_team_id":339,"fclogo_url":None,"transfermarkt_club_id":None},
    "Werder Bremen":    {"club_id":"c20","zh_name":"云达不来梅","en_name":"SV Werder Bremen","city":"Bremen","region":"Bremen","stadium":"Weserstadion","country":"Germany","league":"Bundesliga","lat":53.07,"lng":8.81,"sportsapi_team_id":332,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- Italy ---
    "Inter Milan":      {"club_id":"c21","zh_name":"国际米兰","en_name":"Inter Milan","city":"Milan","region":"Lombardy","stadium":"San Siro","country":"Italy","league":"Serie A","lat":45.46,"lng":9.19,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/pSiUwart4b","transfermarkt_club_id":46},
    "AC Milan":         {"club_id":"c22","zh_name":"AC米兰","en_name":"AC Milan","city":"Milan","region":"Lombardy","stadium":"San Siro","country":"Italy","league":"Serie A","lat":45.47,"lng":9.20,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/0FsK2tzv8p","transfermarkt_club_id":5},
    "Juventus":         {"club_id":"c23","zh_name":"尤文图斯","en_name":"Juventus FC","city":"Turin","region":"Piedmont","stadium":"Allianz Stadium","country":"Italy","league":"Serie A","lat":45.11,"lng":7.69,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/7jGdROUadj","transfermarkt_club_id":506},
    "AS Roma":          {"club_id":"c24","zh_name":"罗马","en_name":"AS Roma","city":"Rome","region":"Lazio","stadium":"Stadio Olimpico","country":"Italy","league":"Serie A","lat":41.93,"lng":12.46,"sportsapi_team_id":225,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- France / Monaco ---
    "PSG":              {"club_id":"c25","zh_name":"巴黎圣日耳曼","en_name":"Paris Saint-Germain","city":"Paris","region":"Île-de-France","stadium":"Parc des Princes","country":"France","league":"Ligue 1","lat":48.84,"lng":2.35,"sportsapi_team_id":None,"fclogo_url":"https://aka.doubaocdn.com/s/c4O6JKFRXG","transfermarkt_club_id":583},
    "AS Monaco":        {"club_id":"c26","zh_name":"摩纳哥","en_name":"AS Monaco","city":"Monaco","region":"Monaco","stadium":"Stade Louis II","country":"Monaco","league":"Ligue 1","lat":43.74,"lng":7.42,"sportsapi_team_id":471,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- Switzerland ---
    "Basel":            {"club_id":"c27","zh_name":"巴塞尔","en_name":"FC Basel","city":"Basel","region":"Basel-Stadt","stadium":"St. Jakob-Park","country":"Switzerland","league":"Swiss Super L.","lat":47.56,"lng":7.59,"sportsapi_team_id":1138,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- Austria ---
    "RB Salzburg":      {"club_id":"c28","zh_name":"萨尔茨堡红牛","en_name":"RB Salzburg","city":"Salzburg","region":"Salzburg","stadium":"Red Bull Arena","country":"Austria","league":"Bundesliga A","lat":47.80,"lng":13.04,"sportsapi_team_id":1739,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- Norway ---
    "Molde FK":         {"club_id":"c29","zh_name":"莫尔德","en_name":"Molde FK","city":"Molde","region":"Møre og Romsdal","stadium":"Aker Stadion","country":"Norway","league":"Eliteserien","lat":62.74,"lng":7.16,"sportsapi_team_id":1983,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- South America ---
    "Flamengo":         {"club_id":"c30","zh_name":"弗拉门戈","en_name":"Clube de Regatas do Flamengo","city":"Rio de Janeiro","region":"Rio de Janeiro","stadium":"Maracanã","country":"Brazil","league":"Brasileirão","lat":-22.95,"lng":-43.21,"sportsapi_team_id":1215,"fclogo_url":None,"transfermarkt_club_id":None},
    "Racing Club":      {"club_id":"c31","zh_name":"竞技俱乐部","en_name":"Racing Club","city":"Avellaneda","region":"Buenos Aires","stadium":"Estadio Presidente Perón","country":"Argentina","league":"Primera Div.","lat":-34.67,"lng":-58.36,"sportsapi_team_id":876,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- Additional clubs (introduced with the expanded player roster) ---
    "Real Sociedad":    {"club_id":"c32","zh_name":"皇家社会","en_name":"Real Sociedad","city":"San Sebastián","region":"Basque Country","stadium":"Reale Arena","country":"Spain","league":"LaLiga","lat":43.30,"lng":-1.97,"sportsapi_team_id":154,"fclogo_url":None,"transfermarkt_club_id":None},
    "Napoli":           {"club_id":"c33","zh_name":"那不勒斯","en_name":"SSC Napoli","city":"Naples","region":"Campania","stadium":"Stadio Diego Armando Maradona","country":"Italy","league":"Serie A","lat":40.83,"lng":14.19,"sportsapi_team_id":234,"fclogo_url":None,"transfermarkt_club_id":None},
    "Benfica":          {"club_id":"c34","zh_name":"本菲卡","en_name":"SL Benfica","city":"Lisbon","region":"Lisbon","stadium":"Estádio da Luz","country":"Portugal","league":"Primeira Liga","lat":38.75,"lng":-9.18,"sportsapi_team_id":888,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- Additional Premier League clubs (current clubs of expanded roster) ---
    "Bournemouth":      {"club_id":"c35","zh_name":"伯恩茅斯","en_name":"AFC Bournemouth","city":"Bournemouth","region":"Dorset","stadium":"Vitality Stadium","country":"England","league":"Premier League","lat":50.73,"lng":-1.84,"sportsapi_team_id":50,"fclogo_url":None,"transfermarkt_club_id":None},
    "Brighton":         {"club_id":"c36","zh_name":"布莱顿","en_name":"Brighton & Hove Albion","city":"Brighton","region":"East Sussex","stadium":"Amex Stadium","country":"England","league":"Premier League","lat":50.86,"lng":-0.08,"sportsapi_team_id":38,"fclogo_url":None,"transfermarkt_club_id":None},
    "Wolves":           {"club_id":"c37","zh_name":"狼队","en_name":"Wolverhampton Wanderers","city":"Wolverhampton","region":"West Midlands","stadium":"Molineux","country":"England","league":"Premier League","lat":52.59,"lng":-2.13,"sportsapi_team_id":15,"fclogo_url":None,"transfermarkt_club_id":None},
    "Brentford":        {"club_id":"c38","zh_name":"布伦特福德","en_name":"Brentford FC","city":"London","region":"Greater London","stadium":"Gtech Community Stadium","country":"England","league":"Premier League","lat":51.49,"lng":-0.30,"sportsapi_team_id":63,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- Additional clubs referenced in career histories ---
    "RB Leipzig":       {"club_id":"c39","zh_name":"莱比锡红牛","en_name":"RB Leipzig","city":"Leipzig","region":"Saxony","stadium":"Red Bull Arena","country":"Germany","league":"Bundesliga","lat":51.34,"lng":12.37,"sportsapi_team_id":7171,"fclogo_url":None,"transfermarkt_club_id":None},
    "Lille":            {"club_id":"c40","zh_name":"里尔","en_name":"LOSC Lille","city":"Lille","region":"Hauts-de-France","stadium":"Stade Pierre-Mauroy","country":"France","league":"Ligue 1","lat":50.61,"lng":3.13,"sportsapi_team_id":478,"fclogo_url":None,"transfermarkt_club_id":None},
    "Rennes":           {"club_id":"c41","zh_name":"雷恩","en_name":"Stade Rennais","city":"Rennes","region":"Brittany","stadium":"Roazhon Park","country":"France","league":"Ligue 1","lat":48.11,"lng":-1.68,"sportsapi_team_id":477,"fclogo_url":None,"transfermarkt_club_id":None},
    "Lyon":             {"club_id":"c42","zh_name":"里昂","en_name":"Olympique Lyonnais","city":"Lyon","region":"Auvergne-Rhône-Alpes","stadium":"Groupama Stadium","country":"France","league":"Ligue 1","lat":45.77,"lng":4.98,"sportsapi_team_id":465,"fclogo_url":None,"transfermarkt_club_id":None},
    "Eintracht Frankfurt": {"club_id":"c43","zh_name":"法兰克福","en_name":"Eintracht Frankfurt","city":"Frankfurt","region":"Hesse","stadium":"Deutsche Bank Park","country":"Germany","league":"Bundesliga","lat":50.07,"lng":8.65,"sportsapi_team_id":337,"fclogo_url":None,"transfermarkt_club_id":None},
    # --- Historical clubs (career stops of expanded roster) ---
    "Ajax":                 {"club_id":"c44","zh_name":"阿贾克斯","en_name":"AFC Ajax","city":"Amsterdam","region":"North Holland","stadium":"Johan Cruijff Arena","country":"Netherlands","league":"Eredivisie","lat":52.3147,"lng":4.9417,"sportsapi_team_id":690,"fclogo_url":None,"transfermarkt_club_id":None},
    "Anderlecht":           {"club_id":"c45","zh_name":"安德莱赫特","en_name":"RSC Anderlecht","city":"Brussels","region":"Brussels","stadium":"Lotto Park","country":"Belgium","league":"Belgian Pro League","lat":50.8292,"lng":4.3236,"sportsapi_team_id":1173,"fclogo_url":None,"transfermarkt_club_id":None},
    "Brescia":              {"club_id":"c46","zh_name":"布雷西亚","en_name":"Brescia Calcio","city":"Brescia","region":"Lombardy","stadium":"Stadio Mario Rigamonti","country":"Italy","league":"Serie B","lat":45.5369,"lng":10.2167,"sportsapi_team_id":249,"fclogo_url":None,"transfermarkt_club_id":None},
    "Bristol City":         {"club_id":"c47","zh_name":"布里斯托尔城","en_name":"Bristol City FC","city":"Bristol","region":"South West England","stadium":"Ashton Gate","country":"England","league":"Championship","lat":51.4458,"lng":-2.6397,"sportsapi_team_id":6,"fclogo_url":None,"transfermarkt_club_id":None},
    "Crystal Palace":       {"club_id":"c48","zh_name":"水晶宫","en_name":"Crystal Palace FC","city":"London","region":"Greater London","stadium":"Selhurst Park","country":"England","league":"Premier League","lat":51.3948,"lng":-0.0855,"sportsapi_team_id":10,"fclogo_url":None,"transfermarkt_club_id":None},
    "Fenerbahce":           {"club_id":"c49","zh_name":"费内巴切","en_name":"Fenerbahçe SK","city":"Istanbul","region":"Istanbul","stadium":"Şükrü Saracoğlu Stadium","country":"Turkey","league":"Süper Lig","lat":40.9727,"lng":29.0411,"sportsapi_team_id":946,"fclogo_url":None,"transfermarkt_club_id":None},
    "Fluminense":           {"club_id":"c50","zh_name":"弗鲁米嫩塞","en_name":"Fluminense FC","city":"Rio de Janeiro","region":"Rio de Janeiro","stadium":"Maracanã","country":"Brazil","league":"Brasileirão","lat":-22.95,"lng":-43.21,"sportsapi_team_id":1216,"fclogo_url":None,"transfermarkt_club_id":None},
    "Hertha BSC":           {"club_id":"c51","zh_name":"柏林赫塔","en_name":"Hertha BSC","city":"Berlin","region":"Berlin","stadium":"Olympiastadion","country":"Germany","league":"Bundesliga","lat":52.5148,"lng":13.2394,"sportsapi_team_id":342,"fclogo_url":None,"transfermarkt_club_id":None},
    "Independiente del Valle": {"club_id":"c52","zh_name":"山谷独立","en_name":"Independiente del Valle","city":"Quito","region":"Pichincha","stadium":"Estadio Banco Guayaquil","country":"Ecuador","league":"Serie A","lat":-0.1807,"lng":-78.4847,"sportsapi_team_id":9142,"fclogo_url":None,"transfermarkt_club_id":None},
    "Las Palmas":           {"club_id":"c53","zh_name":"拉斯帕尔马斯","en_name":"UD Las Palmas","city":"Las Palmas","region":"Canary Islands","stadium":"Estadio Gran Canaria","country":"Spain","league":"LaLiga","lat":28.1042,"lng":-15.4553,"sportsapi_team_id":167,"fclogo_url":None,"transfermarkt_club_id":None},
    "Middlesbrough":        {"club_id":"c54","zh_name":"米德尔斯堡","en_name":"Middlesbrough FC","city":"Middlesbrough","region":"North Yorkshire","stadium":"Riverside Stadium","country":"England","league":"Championship","lat":54.5786,"lng":-1.2242,"sportsapi_team_id":115,"fclogo_url":None,"transfermarkt_club_id":None},
    "Palmeiras":            {"club_id":"c55","zh_name":"帕尔梅拉斯","en_name":"SE Palmeiras","city":"São Paulo","region":"São Paulo","stadium":"Allianz Parque","country":"Brazil","league":"Brasileirão","lat":-23.5265,"lng":-46.6664,"sportsapi_team_id":1222,"fclogo_url":None,"transfermarkt_club_id":None},
    "Penarol":              {"club_id":"c56","zh_name":"佩纳罗尔","en_name":"CA Peñarol","city":"Montevideo","region":"Montevideo","stadium":"Estadio Campeón del Siglo","country":"Uruguay","league":"Primera Div.","lat":-34.8719,"lng":-56.0697,"sportsapi_team_id":19545,"fclogo_url":None,"transfermarkt_club_id":None},
    "Porto":                {"club_id":"c57","zh_name":"波尔图","en_name":"FC Porto","city":"Porto","region":"Porto","stadium":"Estádio do Dragão","country":"Portugal","league":"Primeira Liga","lat":41.1518,"lng":-8.5847,"sportsapi_team_id":887,"fclogo_url":None,"transfermarkt_club_id":None},
    "Reading":              {"club_id":"c58","zh_name":"雷丁","en_name":"Reading FC","city":"Reading","region":"Berkshire","stadium":"Select Car Leasing Stadium","country":"England","league":"Championship","lat":51.4422,"lng":-0.9808,"sportsapi_team_id":2,"fclogo_url":None,"transfermarkt_club_id":None},
    "Reims":                {"club_id":"c59","zh_name":"兰斯","en_name":"Stade de Reims","city":"Reims","region":"Grand Est","stadium":"Stade Auguste-Delaune","country":"France","league":"Ligue 1","lat":49.2458,"lng":3.9972,"sportsapi_team_id":499,"fclogo_url":None,"transfermarkt_club_id":None},
    "River Plate":          {"club_id":"c60","zh_name":"河床","en_name":"CA River Plate","city":"Buenos Aires","region":"Buenos Aires","stadium":"Estadio Monumental","country":"Argentina","league":"Primera Div.","lat":-34.5444,"lng":-58.4453,"sportsapi_team_id":868,"fclogo_url":None,"transfermarkt_club_id":None},
    "Saint-Etienne":        {"club_id":"c61","zh_name":"圣埃蒂安","en_name":"AS Saint-Étienne","city":"Saint-Étienne","region":"Auvergne-Rhône-Alpes","stadium":"Stade Geoffroy-Guichard","country":"France","league":"Ligue 1","lat":45.4519,"lng":4.3986,"sportsapi_team_id":474,"fclogo_url":None,"transfermarkt_club_id":None},
    "Sporting CP":          {"club_id":"c62","zh_name":"葡萄牙体育","en_name":"Sporting CP","city":"Lisbon","region":"Lisbon","stadium":"Estádio José Alvalade","country":"Portugal","league":"Primeira Liga","lat":38.7621,"lng":-9.1550,"sportsapi_team_id":890,"fclogo_url":None,"transfermarkt_club_id":None},
    "Troyes":               {"club_id":"c63","zh_name":"特鲁瓦","en_name":"ESTAC Troyes","city":"Troyes","region":"Grand Est","stadium":"Stade de l'Aube","country":"France","league":"Ligue 1","lat":48.2903,"lng":4.0936,"sportsapi_team_id":488,"fclogo_url":None,"transfermarkt_club_id":None},
    "Watford":              {"club_id":"c64","zh_name":"沃特福德","en_name":"Watford FC","city":"Watford","region":"Hertfordshire","stadium":"Vicarage Road","country":"England","league":"Premier League","lat":51.6499,"lng":-0.4016,"sportsapi_team_id":4,"fclogo_url":None,"transfermarkt_club_id":None},
    "West Ham":             {"club_id":"c65","zh_name":"西汉姆联","en_name":"West Ham United","city":"London","region":"Greater London","stadium":"London Stadium","country":"England","league":"Premier League","lat":51.5388,"lng":-0.0166,"sportsapi_team_id":113,"fclogo_url":None,"transfermarkt_club_id":None},
    "Galatasaray":          {"club_id":"c66","zh_name":"加拉塔萨雷","en_name":"Galatasaray SK","city":"Istanbul","region":"Istanbul","stadium":"RAMS Park","country":"Turkey","league":"Süper Lig","lat":41.1049,"lng":29.0043,"sportsapi_team_id":945,"fclogo_url":None,"transfermarkt_club_id":None},
    "Como":                 {"club_id":"c67","zh_name":"科莫","en_name":"Como 1907","city":"Como","region":"Lombardy","stadium":"Stadio Giuseppe Sinigaglia","country":"Italy","league":"Serie A","lat":45.8078,"lng":9.0848,"sportsapi_team_id":6117,"fclogo_url":None,"transfermarkt_club_id":None},
    "Leganés":            {"club_id":"c68","zh_name":"莱加内斯","en_name":"CD Leganés","city":"Leganés","region":"Community of Madrid","stadium":"Estadio Municipal de Butarque","country":"Spain","league":"LaLiga","lat":40.3261,"lng":-3.7647,"sportsapi_team_id":9242,"fclogo_url":None,"transfermarkt_club_id":None},
    "AZ Alkmaar":          {"club_id":"c69","zh_name":"阿尔克马尔","en_name":"AZ Alkmaar","city":"Alkmaar","region":"North Holland","stadium":"AFAS Stadion","country":"Netherlands","league":"Eredivisie","lat":52.6125,"lng":4.7422,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":1090},
    "Aarhus":              {"club_id":"c70","zh_name":"奥胡斯","en_name":"Aarhus GF","city":"Aarhus","region":"Central Denmark","stadium":"Ceres Park","country":"Denmark","league":"Superliga","lat":56.1924,"lng":10.2103,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":678},
    "Al-Hilal":            {"club_id":"c71","zh_name":"利雅得新月","en_name":"Al-Hilal SFC","city":"Riyadh","region":"Riyadh Province","stadium":"Kingdom Arena","country":"Saudi Arabia","league":"Saudi Pro League","lat":24.7136,"lng":46.6753,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":1114},
    "Al-Qadsiah":          {"club_id":"c72","zh_name":"卡迪西亚","en_name":"Al-Qadsiah FC","city":"Khobar","region":"Eastern Province","stadium":"Prince Saud bin Jalawi Stadium","country":"Saudi Arabia","league":"Saudi Pro League","lat":26.2172,"lng":50.1971,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":26069},
    "Almería":             {"club_id":"c73","zh_name":"阿尔梅里亚","en_name":"UD Almería","city":"Almería","region":"Andalusia","stadium":"Power Horse Stadium","country":"Spain","league":"LaLiga 2","lat":36.8403,"lng":-2.4353,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":3302},
    "Atalanta":            {"club_id":"c74","zh_name":"亚特兰大","en_name":"Atalanta BC","city":"Bergamo","region":"Lombardy","stadium":"Gewiss Stadium","country":"Italy","league":"Serie A","lat":45.7095,"lng":9.6808,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":800},
    "Blackburn":           {"club_id":"c75","zh_name":"布莱克本流浪者","en_name":"Blackburn Rovers","city":"Blackburn","region":"Lancashire","stadium":"Ewood Park","country":"England","league":"Championship","lat":53.7286,"lng":-2.4892,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":164},
    "Bologna":             {"club_id":"c76","zh_name":"博洛尼亚","en_name":"Bologna FC 1909","city":"Bologna","region":"Emilia-Romagna","stadium":"Stadio Renato Dall'Ara","country":"Italy","league":"Serie A","lat":44.4926,"lng":11.3103,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":1025},
    "Clermont Foot":       {"club_id":"c77","zh_name":"克莱蒙","en_name":"Clermont Foot 63","city":"Clermont-Ferrand","region":"Auvergne-Rhône-Alpes","stadium":"Stade Gabriel-Montpied","country":"France","league":"Ligue 1","lat":45.8158,"lng":3.1219,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":3524},
    "Club Brugge":         {"club_id":"c78","zh_name":"布鲁日","en_name":"Club Brugge KV","city":"Bruges","region":"West Flanders","stadium":"Jan Breydel Stadium","country":"Belgium","league":"Pro League","lat":51.1933,"lng":3.1806,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":2282},
    "Corinthians":         {"club_id":"c79","zh_name":"科林蒂安","en_name":"SC Corinthians Paulista","city":"São Paulo","region":"São Paulo","stadium":"Neo Química Arena","country":"Brazil","league":"Série A","lat":-23.5455,"lng":-46.4743,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":199},
    "Coventry":            {"club_id":"c80","zh_name":"考文垂","en_name":"Coventry City","city":"Coventry","region":"West Midlands","stadium":"Coventry Building Society Arena","country":"England","league":"Championship","lat":52.4481,"lng":-1.4956,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":990},
    "Cruzeiro":            {"club_id":"c81","zh_name":"克鲁塞罗","en_name":"Cruzeiro EC","city":"Belo Horizonte","region":"Minas Gerais","stadium":"Mineirão","country":"Brazil","league":"Série A","lat":-19.8659,"lng":-43.9711,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":609},
    "Dinamo Zagreb":       {"club_id":"c82","zh_name":"萨格勒布迪纳摩","en_name":"GNK Dinamo Zagreb","city":"Zagreb","region":"Zagreb","stadium":"Stadion Maksimir","country":"Croatia","league":"HNL","lat":45.8186,"lng":16.0181,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":419},
    "Elversberg":          {"club_id":"c83","zh_name":"埃尔弗斯贝格","en_name":"SV 07 Elversberg","city":"Spiesen-Elversberg","region":"Saarland","stadium":"Waldstadion Kaiserlinde","country":"Germany","league":"2. Bundesliga","lat":49.3183,"lng":7.1217,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":64},
    "Energetik-BGU":       {"club_id":"c84","zh_name":"明斯克动力","en_name":"Energetik-BGU Minsk","city":"Minsk","region":"Minsk","stadium":"RCOR-BGU Stadium","country":"Belarus","league":"Belarusian Premier League","lat":53.901,"lng":27.5357,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":27204},
    "Estoril":             {"club_id":"c85","zh_name":"埃斯托里尔","en_name":"GD Estoril Praia","city":"Estoril","region":"Lisbon District","stadium":"Estádio António Coimbra da Mota","country":"Portugal","league":"Primeira Liga","lat":38.7164,"lng":-9.4069,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":1465},
    "Estudiantes":         {"club_id":"c86","zh_name":"拉普拉塔大学生","en_name":"Estudiantes de La Plata","city":"La Plata","region":"Buenos Aires Province","stadium":"Estadio Jorge Luis Hirschi","country":"Argentina","league":"Primera Div.","lat":-34.9122,"lng":-57.9389,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":288},
    "Everton":             {"club_id":"c87","zh_name":"埃弗顿","en_name":"Everton FC","city":"Liverpool","region":"Merseyside","stadium":"Hill Dickinson Stadium","country":"England","league":"Premier League","lat":53.4252,"lng":-2.9995,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":29},
    "FC Copenhagen":       {"club_id":"c88","zh_name":"哥本哈根","en_name":"FC Copenhagen","city":"Copenhagen","region":"Capital Region","stadium":"Parken Stadium","country":"Denmark","league":"Superliga","lat":55.7025,"lng":12.5722,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":190},
    "Freiburg":            {"club_id":"c89","zh_name":"弗赖堡","en_name":"SC Freiburg","city":"Freiburg im Breisgau","region":"Baden-Württemberg","stadium":"Europa-Park Stadion","country":"Germany","league":"Bundesliga","lat":48.0216,"lng":7.8297,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":60},
    "Genoa":               {"club_id":"c90","zh_name":"热那亚","en_name":"Genoa CFC","city":"Genoa","region":"Liguria","stadium":"Stadio Luigi Ferraris","country":"Italy","league":"Serie A","lat":44.4164,"lng":8.9525,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":252},
    "Getafe":              {"club_id":"c91","zh_name":"赫塔费","en_name":"Getafe CF","city":"Getafe","region":"Community of Madrid","stadium":"Coliseum Alfonso Pérez","country":"Spain","league":"LaLiga","lat":40.3256,"lng":-3.7147,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":3709},
    "Granada":             {"club_id":"c92","zh_name":"格拉纳达","en_name":"Granada CF","city":"Granada","region":"Andalusia","stadium":"Nuevo Estadio de Los Cármenes","country":"Spain","league":"LaLiga 2","lat":37.1528,"lng":-3.5958,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":16795},
    "Hajduk Split":        {"club_id":"c93","zh_name":"哈伊杜克","en_name":"HNK Hajduk Split","city":"Split","region":"Split-Dalmatia","stadium":"Stadion Poljud","country":"Croatia","league":"HNL","lat":43.5197,"lng":16.4317,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":447},
    "Hamburger SV":        {"club_id":"c94","zh_name":"汉堡","en_name":"Hamburger SV","city":"Hamburg","region":"Hamburg","stadium":"Volksparkstadion","country":"Germany","league":"Bundesliga","lat":53.5872,"lng":9.8986,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":41},
    "Hellas Verona":       {"club_id":"c95","zh_name":"维罗纳","en_name":"Hellas Verona FC","city":"Verona","region":"Veneto","stadium":"Stadio Marcantonio Bentegodi","country":"Italy","league":"Serie A","lat":45.4353,"lng":10.9686,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":276},
    "Hoffenheim":          {"club_id":"c96","zh_name":"霍芬海姆","en_name":"TSG 1899 Hoffenheim","city":"Sinsheim","region":"Baden-Württemberg","stadium":"PreZero Arena","country":"Germany","league":"Bundesliga","lat":49.2389,"lng":8.8878,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":533},
    "Huddersfield":        {"club_id":"c97","zh_name":"哈德斯菲尔德","en_name":"Huddersfield Town","city":"Huddersfield","region":"West Yorkshire","stadium":"John Smith's Stadium","country":"England","league":"League One","lat":53.6543,"lng":-1.7683,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":1110},
    "Leeds United":        {"club_id":"c98","zh_name":"利兹联","en_name":"Leeds United","city":"Leeds","region":"West Yorkshire","stadium":"Elland Road","country":"England","league":"Premier League","lat":53.7779,"lng":-1.5722,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":399},
    "Lens":                {"club_id":"c99","zh_name":"朗斯","en_name":"RC Lens","city":"Lens","region":"Hauts-de-France","stadium":"Stade Bollaert-Delelis","country":"France","league":"Ligue 1","lat":50.4328,"lng":2.815,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":826},
    "Lorient":             {"club_id":"c100","zh_name":"洛里昂","en_name":"FC Lorient","city":"Lorient","region":"Brittany","stadium":"Stade du Moustoir","country":"France","league":"Ligue 1","lat":47.7486,"lng":-3.3694,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":1158},
    "Ludogorets":          {"club_id":"c101","zh_name":"卢多戈雷茨","en_name":"PFC Ludogorets Razgrad","city":"Razgrad","region":"Razgrad Province","stadium":"Huvepharma Arena","country":"Bulgaria","league":"Parva Liga","lat":43.5347,"lng":26.5272,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":31614},
    "M'Gladbach":          {"club_id":"c102","zh_name":"门兴格拉德巴赫","en_name":"Borussia Mönchengladbach","city":"Mönchengladbach","region":"North Rhine-Westphalia","stadium":"Borussia-Park","country":"Germany","league":"Bundesliga","lat":51.1746,"lng":6.3855,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":18},
    "Marseille":           {"club_id":"c103","zh_name":"马赛","en_name":"Olympique de Marseille","city":"Marseille","region":"Provence-Alpes-Côte d'Azur","stadium":"Stade Vélodrome","country":"France","league":"Ligue 1","lat":43.2699,"lng":5.3958,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":244},
    "Nordsjaelland":       {"club_id":"c104","zh_name":"北西兰","en_name":"FC Nordsjaelland","city":"Farum","region":"Capital Region","stadium":"Right to Dream Park","country":"Denmark","league":"Superliga","lat":55.8158,"lng":12.3981,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":2778},
    "Nottingham Forest":   {"club_id":"c105","zh_name":"诺丁汉森林","en_name":"Nottingham Forest","city":"West Bridgford","region":"Nottinghamshire","stadium":"City Ground","country":"England","league":"Premier League","lat":52.9399,"lng":-1.1328,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":703},
    "PSV":                 {"club_id":"c106","zh_name":"埃因霍温","en_name":"PSV Eindhoven","city":"Eindhoven","region":"North Brabant","stadium":"Philips Stadion","country":"Netherlands","league":"Eredivisie","lat":51.4417,"lng":5.4675,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":383},
    "Preston":             {"club_id":"c107","zh_name":"普雷斯顿","en_name":"Preston North End","city":"Preston","region":"Lancashire","stadium":"Deepdale","country":"England","league":"Championship","lat":53.7722,"lng":-2.6883,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":466},
    "QPR":                 {"club_id":"c108","zh_name":"女王公园巡游者","en_name":"Queens Park Rangers","city":"London","region":"Greater London","stadium":"Loftus Road","country":"England","league":"Championship","lat":51.5092,"lng":-0.2322,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":1039},
    "RKC Waalwijk":        {"club_id":"c109","zh_name":"瓦尔韦克","en_name":"RKC Waalwijk","city":"Waalwijk","region":"North Brabant","stadium":"Mandemakers Stadion","country":"Netherlands","league":"Eredivisie","lat":51.6869,"lng":5.0889,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":235},
    "Radomiak Radom":      {"club_id":"c110","zh_name":"拉多米亚克","en_name":"Radomiak Radom","city":"Radom","region":"Masovian","stadium":"Stadion im. Braci Czachorów","country":"Poland","league":"Ekstraklasa","lat":51.3969,"lng":21.1567,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":7154},
    "Roda JC":             {"club_id":"c111","zh_name":"罗达JC","en_name":"Roda JC Kerkrade","city":"Kerkrade","region":"Limburg","stadium":"Parkstad Limburg Stadion","country":"Netherlands","league":"Eerste Divisie","lat":50.8572,"lng":6.0058,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":192},
    "Sevilla":             {"club_id":"c112","zh_name":"塞维利亚","en_name":"Sevilla FC","city":"Seville","region":"Andalusia","stadium":"Ramón Sánchez-Pizjuán","country":"Spain","league":"LaLiga","lat":37.384,"lng":-5.9706,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":368},
    "Sheffield United":    {"club_id":"c113","zh_name":"谢菲尔德联","en_name":"Sheffield United","city":"Sheffield","region":"South Yorkshire","stadium":"Bramall Lane","country":"England","league":"Championship","lat":53.3703,"lng":-1.4708,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":350},
    "Sochaux":             {"club_id":"c114","zh_name":"索肖","en_name":"FC Sochaux-Montbéliard","city":"Montbéliard","region":"Bourgogne-Franche-Comté","stadium":"Stade Auguste Bonal","country":"France","league":"Ligue 2","lat":47.5126,"lng":6.8113,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":750},
    "St. Pauli":           {"club_id":"c115","zh_name":"圣保利","en_name":"FC St. Pauli","city":"Hamburg","region":"Hamburg","stadium":"Millerntor-Stadion","country":"Germany","league":"Bundesliga","lat":53.5546,"lng":9.9676,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":35},
    "Sturm Graz":          {"club_id":"c116","zh_name":"格拉茨风暴","en_name":"SK Sturm Graz","city":"Graz","region":"Styria","stadium":"Merkur-Arena","country":"Austria","league":"Austrian Bundesliga","lat":47.0464,"lng":15.4545,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":122},
    "Stuttgart":           {"club_id":"c117","zh_name":"斯图加特","en_name":"VfB Stuttgart","city":"Stuttgart","region":"Baden-Württemberg","stadium":"MHPArena","country":"Germany","league":"Bundesliga","lat":48.7923,"lng":9.232,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":79},
    "Swansea":             {"club_id":"c118","zh_name":"斯旺西","en_name":"Swansea City","city":"Swansea","region":"Wales","stadium":"Swansea.com Stadium","country":"Wales","league":"Championship","lat":51.6427,"lng":-3.9347,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":2288},
    "Talleres":            {"club_id":"c119","zh_name":"塔列雷斯","en_name":"CA Talleres","city":"Córdoba","region":"Córdoba Province","stadium":"Estadio Mario Alberto Kempes","country":"Argentina","league":"Primera Div.","lat":-31.369,"lng":-64.2461,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":3938},
    "Tigre":               {"club_id":"c120","zh_name":"蒂格雷","en_name":"Club Atlético Tigre","city":"Victoria","region":"Buenos Aires Province","stadium":"Estadio José Dellagiovanna","country":"Argentina","league":"Primera Div.","lat":-34.4497,"lng":-58.5421,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":11831},
    "Toulouse":            {"club_id":"c121","zh_name":"图卢兹","en_name":"FC Toulouse","city":"Toulouse","region":"Occitanie","stadium":"Stadium de Toulouse","country":"France","league":"Ligue 1","lat":43.5832,"lng":1.4342,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":415},
    "Union Berlin":        {"club_id":"c122","zh_name":"柏林联合","en_name":"1. FC Union Berlin","city":"Berlin","region":"Berlin","stadium":"Stadion An der Alten Försterei","country":"Germany","league":"Bundesliga","lat":52.4572,"lng":13.568,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":89},
    "Valencia":            {"club_id":"c123","zh_name":"瓦伦西亚","en_name":"Valencia CF","city":"Valencia","region":"Valencian Community","stadium":"Mestalla","country":"Spain","league":"LaLiga","lat":39.4747,"lng":-0.3583,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":1049},
    "Vasco da Gama":       {"club_id":"c124","zh_name":"瓦斯科达伽马","en_name":"CR Vasco da Gama","city":"Rio de Janeiro","region":"Rio de Janeiro","stadium":"São Januário","country":"Brazil","league":"Série A","lat":-22.8911,"lng":-43.2281,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":978},
    "Volendam":            {"club_id":"c125","zh_name":"福伦丹","en_name":"FC Volendam","city":"Volendam","region":"North Holland","stadium":"Kras Stadion","country":"Netherlands","league":"Eredivisie","lat":52.4944,"lng":5.0731,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":724},
    "Westerlo":            {"club_id":"c126","zh_name":"韦斯特洛","en_name":"KVC Westerlo","city":"Westerlo","region":"Antwerp Province","stadium":"Het Kuipje","country":"Belgium","league":"Pro League","lat":51.0897,"lng":4.9172,"sportsapi_team_id":None,"fclogo_url":None,"transfermarkt_club_id":968},
}

# Derived lookups (backward-compatible views over the master table)

LOGOS = {name: c["fclogo_url"] for name, c in CLUBS.items() if c["fclogo_url"]}

# 生涯/身价记录里出现、但不在 CLUBS 主表（不进地图与俱乐部总览）的俱乐部：
# 只补联赛与队徽，供生涯/身价表格使用。transfermarkt_club_id 已逐条校验（wappen 200 image/png）。
EXTRA_CLUBS = {
    "1.FC Köln":                 {"league": "Bundesliga", "transfermarkt_club_id": 3},
    "AA Argentinos Juniors":     {"league": "Liga Profesional", "transfermarkt_club_id": 1030},
    "Ascoli Picchio":            {"league": "Serie B", "transfermarkt_club_id": 408},
    "Barranquilla FC":           {"league": "Primera B", "transfermarkt_club_id": 18127},
    "CA Boca Juniors":           {"league": "Liga Profesional", "transfermarkt_club_id": 189},
    "Cagliari Calcio":           {"league": "Serie A", "transfermarkt_club_id": 1390},
    "Club Athletico Paranaense": {"league": "Série A", "transfermarkt_club_id": 679},
    "EA Guingamp":               {"league": "Ligue 1", "transfermarkt_club_id": 855},
    "FC Empoli":                 {"league": "Serie A", "transfermarkt_club_id": 749},
    "FC Girondins Bordeaux":     {"league": "Ligue 1", "transfermarkt_club_id": 40},
    "FC Sion":                   {"league": "Swiss Super League", "transfermarkt_club_id": 321},
    "Girona FC":                 {"league": "LaLiga", "transfermarkt_club_id": 12321},
    "Holstein Kiel":             {"league": "Bundesliga", "transfermarkt_club_id": 269},
    "IF Brommapojkarna":         {"league": "Allsvenskan", "transfermarkt_club_id": 1092},
    "Junior FC":                 {"league": "Primera A", "transfermarkt_club_id": 11854},
    "PEC Zwolle":                {"league": "Eredivisie", "transfermarkt_club_id": 1269},
    "Parma Calcio 1913":         {"league": "Serie A", "transfermarkt_club_id": 130},
    "SC Braga":                  {"league": "Liga Portugal", "transfermarkt_club_id": 1075},
    "SC Heerenveen":             {"league": "Eredivisie", "transfermarkt_club_id": 306},
    "SD Eibar":                  {"league": "LaLiga", "transfermarkt_club_id": 1533},
    "SS Lazio":                  {"league": "Serie A", "transfermarkt_club_id": 398},
    "Schalke 04":                {"league": "Bundesliga", "transfermarkt_club_id": 33},
    "Shakhtar Donetsk":          {"league": "Ukrainian Premier League", "transfermarkt_club_id": 660},
    "Strømsgodset IF":           {"league": "Eliteserien", "transfermarkt_club_id": 2817},
    "Sunderland":                {"league": "Premier League", "transfermarkt_club_id": 289},
    "Udinese":                   {"league": "Serie A", "transfermarkt_club_id": 410},
    "Vitesse Arnhem":            {"league": "Eredivisie", "transfermarkt_club_id": 499},
    "Vitória Guimarães SC":      {"league": "Liga Portugal", "transfermarkt_club_id": 2420},
    "Wadi Degla FC":             {"league": "Egyptian Premier League", "transfermarkt_club_id": 18234},
    "Wigan Athletic":            {"league": "Premier League", "transfermarkt_club_id": 1071},
}
_CLUB_BY_ID = {c["club_id"]: name for name, c in CLUBS.items()}


def club_meta(club):
    """CLUBS 主表优先，其次 EXTRA_CLUBS（仅生涯记录用），都没有则空字典。"""
    return CLUBS.get(club) or EXTRA_CLUBS.get(club) or {}


def league_for(club, raw=None):
    """联赛名：数据集原始值优先，其次主表/补充表。"""
    return raw or club_meta(club).get("league") or ""


def logo_for(club):
    """Resolve a club badge URL with 3-tier fallback:
    SportsAPI Pro V1 image -> Transfermarkt wappen -> fclogo.top CDN -> None (frontend placeholder).

    fclogo.top (aka.doubaocdn.com) 目前对所有请求返回 403，已降为末位兜底；
    若该 CDN 恢复，可调整顺序把 fclogo_url 提到最前。"""
    c = club_meta(club)
    if not c:
        return None
    tid = c.get("sportsapi_team_id")
    if tid:
        return f"https://api.sportsapipro.com/v1/football/images/competitors/{tid}?imageVersion=8"
    tm = c.get("transfermarkt_club_id")
    if tm:
        return f"https://tmssl.akamaized.net/images/wappen/head/{tm}.png"
    if c.get("fclogo_url"):
        return c["fclogo_url"]
    return None


def club_by_id(club_id):
    """Return club name by internal club_id, or None."""
    return _CLUB_BY_ID.get(club_id)


def club_id_for(club_name):
    """Return internal club_id for a club name, or None."""
    c = CLUBS.get(club_name)
    return c["club_id"] if c else None


def recent_signings_by_club(year_from=2020):
    """Return dict {club_name: [signing_records]} for transfers from year_from onwards.

    A signing record = {player_id, player_name, period, prev_club, current_value_m_eur, club_logo}
    """
    out = {}
    for p in PLAYERS:
        hist = p["career_history"]
        for i, c in enumerate(hist):
            start = period_start(c["period"])
            if start < year_from:
                continue
            prev_club = hist[i-1]["club"] if i > 0 else "(青训 / 学徒)"
            rec = {
                "player_id": p["id"],
                "player_name": p["name"],
                "player_name_zh": p.get("name_zh") or p["name"],
                "player_position": p["position"],
                "player_position_zh": POSITION_ZH.get(p["position"], p["position"]),
                "player_nationality": p["nationality"],
                "player_nationality_zh": NATION_ZH.get(p["nationality"], p["nationality"]),
                "club_id": club_id_for(c["club"]),
                "period": c["period"],
                "prev_club": prev_club,
                "prev_club_zh": CLUBS.get(prev_club, {}).get("zh_name") or (
                    "青训 / 学徒" if prev_club == "(青训 / 学徒)"
                    else CLUB_NAME_ZH.get(prev_club) or prev_club),
                "prev_club_id": club_id_for(prev_club),
                "current_value_m_eur": p["market_value_history"][-1]["value_m_eur"],
                "club_logo": logo_for(c["club"]),
            }
            out.setdefault(c["club"], []).append(rec)
    return out


def clubs_with_geo_and_signings(year_from=2020):
    """Combine CLUBS master table + recent_signings_by_club into a single list."""
    signings = recent_signings_by_club(year_from)
    out = []
    for club, c in CLUBS.items():
        out.append({
            "club_id": c["club_id"],
            "club": club,
            "zh_name": c["zh_name"],
            "en_name": c["en_name"],
            "city": c["city"],
            "region": c["region"],
            "stadium": c["stadium"],
            "country": c["country"],
            "league": c["league"],
            "lat": c["lat"],
            "lng": c["lng"],
            "club_logo": logo_for(club),
            "recent_signings": signings.get(club, []),
            "signings_count": len(signings.get(club, [])),
        })
    # sort: clubs with signings first, then alphabetical
    out.sort(key=lambda x: (-x["signings_count"], x["club"]))
    return out


