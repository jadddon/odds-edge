"""Event matching between Vegas and Kalshi platforms."""

from typing import List, Dict, Tuple
from rapidfuzz import fuzz

# City prefixes to remove for normalization
CITY_PREFIXES = [
    'los angeles', 'la', 'new york', 'ny', 'san francisco', 'sf',
    'tampa bay', 'tb', 'golden state', 'gs', 'san antonio', 'sa',
    'oklahoma city', 'okc', 'new orleans', 'no', 'green bay', 'gb',
    'kansas city', 'kc', 'las vegas', 'lv', 'new england', 'ne',
    'san diego', 'sd', 'san jose', 'sj', 'st louis', 'stl',
    'salt lake', 'sl', 'twin cities', 'minnesota', 'mn',
    'washington', 'dc', 'miami', 'denver', 'phoenix', 'seattle',
    'boston', 'chicago', 'detroit', 'houston', 'dallas', 'atlanta',
    'philadelphia', 'baltimore', 'cleveland', 'indianapolis',
    'jacksonville', 'cincinnati', 'pittsburgh', 'carolina',
    'arizona', 'tennessee', 'buffalo', 'milwaukee', 'orlando',
    'memphis', 'portland', 'sacramento', 'utah', 'toronto',
    'brooklyn', 'colorado', 'florida', 'anaheim', 'columbus',
    'edmonton', 'calgary', 'vancouver', 'ottawa', 'montreal',
    'winnipeg', 'nashville', 'new jersey',
]

# Team nickname to Kalshi abbreviation
NICKNAME_TO_ABBREV = {
    # NBA
    'hawks': 'atl', 'celtics': 'bos', 'nets': 'bkn', 'hornets': 'cha',
    'bulls': 'chi', 'cavaliers': 'cle', 'cavs': 'cle', 'mavericks': 'dal',
    'mavs': 'dal', 'nuggets': 'den', 'pistons': 'det', 'warriors': 'gsw',
    'rockets': 'hou', 'pacers': 'ind', 'clippers': 'lac', 'lakers': 'lal',
    'grizzlies': 'mem', 'heat': 'mia', 'bucks': 'mil', 'timberwolves': 'min',
    'wolves': 'min', 'pelicans': 'nop', 'knicks': 'nyk', 'thunder': 'okc',
    'magic': 'orl', '76ers': 'phi', 'sixers': 'phi', 'suns': 'phx',
    'trail blazers': 'por', 'blazers': 'por', 'kings': 'sac', 'spurs': 'sas',
    'raptors': 'tor', 'jazz': 'uta', 'wizards': 'was',
    # NFL
    'cardinals': 'ari', 'falcons': 'atl', 'ravens': 'bal', 'bills': 'buf',
    'panthers': 'car', 'bears': 'chi', 'bengals': 'cin', 'browns': 'cle',
    'cowboys': 'dal', 'broncos': 'den', 'lions': 'det', 'packers': 'gb',
    'texans': 'hou', 'colts': 'ind', 'jaguars': 'jax', 'chiefs': 'kc',
    'raiders': 'lv', 'chargers': 'lac', 'rams': 'lar', 'dolphins': 'mia',
    'vikings': 'min', 'patriots': 'ne', 'pats': 'ne', 'saints': 'no',
    'giants': 'nyg', 'jets': 'nyj', 'eagles': 'phi', 'steelers': 'pit',
    '49ers': 'sf', 'niners': 'sf', 'seahawks': 'sea', 'buccaneers': 'tb',
    'bucs': 'tb', 'titans': 'ten', 'commanders': 'was',
    # NHL
    'ducks': 'ana', 'coyotes': 'ari', 'bruins': 'bos', 'sabres': 'buf',
    'flames': 'cgy', 'hurricanes': 'car', 'blackhawks': 'chi', 'avalanche': 'col',
    'blue jackets': 'cbj', 'stars': 'dal', 'red wings': 'det', 'oilers': 'edm',
    'panthers': 'fla', 'kings': 'la', 'wild': 'min', 'canadiens': 'mtl',
    'habs': 'mtl', 'predators': 'nsh', 'preds': 'nsh', 'devils': 'njd',
    'islanders': 'nyi', 'rangers': 'nyr', 'senators': 'ott', 'sens': 'ott',
    'flyers': 'phi', 'penguins': 'pit', 'pens': 'pit', 'sharks': 'sjs',
    'kraken': 'sea', 'blues': 'stl', 'lightning': 'tbl', 'bolts': 'tbl',
    'maple leafs': 'tor', 'leafs': 'tor', 'canucks': 'van',
    'golden knights': 'vgk', 'knights': 'vgk', 'capitals': 'wsh', 'caps': 'wsh',
    'jets': 'wpg',
    # MLB
    'diamondbacks': 'ari', 'd-backs': 'ari', 'braves': 'atl', 'orioles': 'bal',
    'red sox': 'bos', 'cubs': 'chc', 'white sox': 'cws', 'reds': 'cin',
    'guardians': 'cle', 'rockies': 'col', 'tigers': 'det', 'astros': 'hou',
    'royals': 'kc', 'angels': 'laa', 'dodgers': 'lad', 'marlins': 'mia',
    'brewers': 'mil', 'twins': 'min', 'mets': 'nym', 'yankees': 'nyy',
    'athletics': 'ath', "a's": 'ath', 'phillies': 'phi', 'pirates': 'pit',
    'padres': 'sd', 'giants': 'sf', 'mariners': 'sea', 'cardinals': 'stl',
    'rays': 'tb', 'rangers': 'tex', 'blue jays': 'tor', 'jays': 'tor',
    'nationals': 'wsh', 'nats': 'wsh',
}

# Full team name to abbreviation
FULL_NAME_TO_ABBREV = {
    # NBA
    'atlanta hawks': 'atl', 'boston celtics': 'bos', 'brooklyn nets': 'bkn',
    'charlotte hornets': 'cha', 'chicago bulls': 'chi', 'cleveland cavaliers': 'cle',
    'dallas mavericks': 'dal', 'denver nuggets': 'den', 'detroit pistons': 'det',
    'golden state warriors': 'gsw', 'houston rockets': 'hou', 'indiana pacers': 'ind',
    'los angeles clippers': 'lac', 'la clippers': 'lac', 'los angeles lakers': 'lal',
    'la lakers': 'lal', 'memphis grizzlies': 'mem', 'miami heat': 'mia',
    'milwaukee bucks': 'mil', 'minnesota timberwolves': 'min',
    'new orleans pelicans': 'nop', 'new york knicks': 'nyk',
    'oklahoma city thunder': 'okc', 'orlando magic': 'orl',
    'philadelphia 76ers': 'phi', 'phoenix suns': 'phx',
    'portland trail blazers': 'por', 'sacramento kings': 'sac',
    'san antonio spurs': 'sas', 'toronto raptors': 'tor',
    'utah jazz': 'uta', 'washington wizards': 'was',
    # NFL
    'arizona cardinals': 'ari', 'atlanta falcons': 'atl', 'baltimore ravens': 'bal',
    'buffalo bills': 'buf', 'carolina panthers': 'car', 'chicago bears': 'chi',
    'cincinnati bengals': 'cin', 'cleveland browns': 'cle', 'dallas cowboys': 'dal',
    'denver broncos': 'den', 'detroit lions': 'det', 'green bay packers': 'gb',
    'houston texans': 'hou', 'indianapolis colts': 'ind', 'jacksonville jaguars': 'jax',
    'kansas city chiefs': 'kc', 'las vegas raiders': 'lv',
    'los angeles chargers': 'lac', 'la chargers': 'lac',
    'los angeles rams': 'lar', 'la rams': 'lar', 'miami dolphins': 'mia',
    'minnesota vikings': 'min', 'new england patriots': 'ne',
    'new orleans saints': 'no', 'new york giants': 'nyg', 'new york jets': 'nyj',
    'philadelphia eagles': 'phi', 'pittsburgh steelers': 'pit',
    'san francisco 49ers': 'sf', 'seattle seahawks': 'sea',
    'tampa bay buccaneers': 'tb', 'tennessee titans': 'ten',
    'washington commanders': 'was',
    # NHL
    'anaheim ducks': 'ana', 'arizona coyotes': 'ari', 'boston bruins': 'bos',
    'buffalo sabres': 'buf', 'calgary flames': 'cgy', 'carolina hurricanes': 'car',
    'chicago blackhawks': 'chi', 'colorado avalanche': 'col',
    'columbus blue jackets': 'cbj', 'dallas stars': 'dal', 'detroit red wings': 'det',
    'edmonton oilers': 'edm', 'florida panthers': 'fla', 'los angeles kings': 'la',
    'la kings': 'la', 'minnesota wild': 'min', 'montreal canadiens': 'mtl',
    'nashville predators': 'nsh', 'new jersey devils': 'njd',
    'new york islanders': 'nyi', 'new york rangers': 'nyr', 'ottawa senators': 'ott',
    'philadelphia flyers': 'phi', 'pittsburgh penguins': 'pit',
    'san jose sharks': 'sjs', 'seattle kraken': 'sea', 'st louis blues': 'stl',
    'st. louis blues': 'stl', 'tampa bay lightning': 'tbl',
    'toronto maple leafs': 'tor', 'utah hockey club': 'uta',
    'vancouver canucks': 'van', 'vegas golden knights': 'vgk',
    'washington capitals': 'wsh', 'winnipeg jets': 'wpg',
    # MLB
    'arizona diamondbacks': 'ari', 'atlanta braves': 'atl', 'baltimore orioles': 'bal',
    'boston red sox': 'bos', 'chicago cubs': 'chc', 'chicago white sox': 'cws',
    'cincinnati reds': 'cin', 'cleveland guardians': 'cle', 'colorado rockies': 'col',
    'detroit tigers': 'det', 'houston astros': 'hou', 'kansas city royals': 'kc',
    'los angeles angels': 'laa', 'la angels': 'laa', 'los angeles dodgers': 'lad',
    'la dodgers': 'lad', 'miami marlins': 'mia', 'milwaukee brewers': 'mil',
    'minnesota twins': 'min', 'new york mets': 'nym', 'new york yankees': 'nyy',
    'oakland athletics': 'ath', 'philadelphia phillies': 'phi',
    'pittsburgh pirates': 'pit', 'san diego padres': 'sd', 'san francisco giants': 'sf',
    'seattle mariners': 'sea', 'st louis cardinals': 'stl', 'st. louis cardinals': 'stl',
    'tampa bay rays': 'tb', 'texas rangers': 'tex', 'toronto blue jays': 'tor',
    'washington nationals': 'wsh',
}

# College mascots to remove for normalization
COLLEGE_MASCOTS = [
    'wildcats', 'bulldogs', 'tigers', 'eagles', 'bears', 'lions', 'panthers',
    'hawks', 'huskies', 'cardinals', 'knights', 'bearcats', 'buckeyes',
    'wolverines', 'spartans', 'gophers', 'badgers', 'hawkeyes', 'cyclones',
    'jayhawks', 'sooners', 'longhorns', 'aggies', 'razorbacks', 'rebels',
    'volunteers', 'commodores', 'gamecocks', 'gators', 'seminoles', 'hurricanes',
    'cavaliers', 'hokies', 'wolfpack', 'tar heels', 'blue devils', 'demon deacons',
    'orange', 'yellow jackets', 'fighting irish', 'trojans', 'bruins', 'ducks',
    'beavers', 'cougars', 'utes', 'buffaloes', 'sun devils', 'golden bears',
    'cardinal', 'mountaineers', 'red raiders', 'horned frogs', 'mustangs',
    'owls', 'bobcats', 'roadrunners', 'miners', 'lobos', 'aztecs',
    'falcons', 'rams', 'broncos', 'cowboys', 'cornhuskers', 'bluejays',
    'shockers', 'pirates', 'billikens', 'musketeers', 'hoyas',
    'friars', 'red storm', 'peacocks', 'gaels', 'toreros', 'dons', 'waves',
    'anteaters', 'matadors', 'titans', 'highlanders', 'hornets',
    'braves', 'jaguars', 'golden lions', 'bison', 'midshipmen', 'black knights',
    'scarlet knights', 'nittany lions', 'terrapins', 'hoosiers', 'boilermakers',
    'fighting illini', 'golden flashes', 'redhawks', 'rockets', 'chippewas',
    'bulls', 'zips', 'penguins', 'thundering herd', 'flames',
]

# College abbreviation mappings
COLLEGE_ABBREV_MAP = {
    'usc': ['southern california', 'usc trojans', 'trojans'],
    'ucla': ['ucla', 'ucla bruins', 'bruins'],
    'osu': ['ohio state', 'ohio st', 'buckeyes'],
    'mich': ['michigan', 'wolverines'],
    'msu': ['michigan state', 'michigan st', 'spartans'],
    'psu': ['penn state', 'penn st', 'nittany lions'],
    'okla': ['oklahoma', 'sooners'],
    'tex': ['texas', 'longhorns'],
    'tamu': ['texas a&m', 'texas am', 'aggies'],
    'tcu': ['tcu', 'horned frogs'],
    'bay': ['baylor', 'bears'],
    'ttu': ['texas tech', 'red raiders'],
    'ku': ['kansas', 'jayhawks'],
    'ksu': ['kansas state', 'kansas st', 'wildcats'],
    'isu': ['iowa state', 'iowa st', 'cyclones'],
    'iowa': ['iowa', 'hawkeyes'],
    'neb': ['nebraska', 'cornhuskers'],
    'wisc': ['wisconsin', 'badgers'],
    'minn': ['minnesota', 'golden gophers', 'gophers'],
    'ill': ['illinois', 'fighting illini'],
    'ind': ['indiana', 'hoosiers'],
    'pur': ['purdue', 'boilermakers'],
    'nw': ['northwestern', 'wildcats'],
    'rut': ['rutgers', 'scarlet knights'],
    'md': ['maryland', 'terrapins', 'terps'],
    'unc': ['north carolina', 'tar heels'],
    'duke': ['duke', 'blue devils'],
    'ncsu': ['nc state', 'north carolina state', 'wolfpack'],
    'wake': ['wake forest', 'demon deacons'],
    'uva': ['virginia', 'cavaliers', 'wahoos'],
    'vt': ['virginia tech', 'hokies'],
    'clem': ['clemson', 'tigers'],
    'lou': ['louisville', 'cardinals'],
    'pitt': ['pittsburgh', 'pitt', 'panthers'],
    'syr': ['syracuse', 'orange'],
    'bc': ['boston college', 'eagles'],
    'nd': ['notre dame', 'fighting irish'],
    'fsu': ['florida state', 'florida st', 'seminoles'],
    'fla': ['florida', 'gators'],
    'uga': ['georgia', 'bulldogs'],
    'aub': ['auburn', 'tigers'],
    'bama': ['alabama', 'crimson tide'],
    'lsu': ['lsu', 'louisiana state', 'tigers'],
    'miss': ['ole miss', 'mississippi', 'rebels'],
    'msst': ['mississippi state', 'mississippi st', 'bulldogs'],
    'ark': ['arkansas', 'razorbacks'],
    'mizzou': ['missouri', 'tigers'],
    'uk': ['kentucky', 'wildcats'],
    'tenn': ['tennessee', 'volunteers', 'vols'],
    'van': ['vanderbilt', 'commodores'],
    'scar': ['south carolina', 'gamecocks'],
    'ore': ['oregon', 'ducks'],
    'orst': ['oregon state', 'oregon st', 'beavers'],
    'wash': ['washington', 'huskies'],
    'wsu': ['washington state', 'washington st', 'cougars'],
    'stan': ['stanford', 'cardinal'],
    'cal': ['california', 'cal', 'golden bears'],
    'ariz': ['arizona', 'wildcats'],
    'asu': ['arizona state', 'arizona st', 'sun devils'],
    'utah': ['utah', 'utes'],
    'colo': ['colorado', 'buffaloes', 'buffs'],
    'byu': ['byu', 'brigham young', 'cougars'],
    'ucf': ['ucf', 'central florida', 'knights'],
    'cin': ['cincinnati', 'bearcats'],
    'hou': ['houston', 'cougars'],
    'wvu': ['west virginia', 'mountaineers'],
    'unlv': ['unlv', 'rebels'],
    'sdsu': ['san diego state', 'san diego st', 'aztecs'],
    'bsu': ['boise state', 'boise st', 'broncos'],
    'fres': ['fresno state', 'fresno st', 'bulldogs'],
    'sjsu': ['san jose state', 'san jose st', 'spartans'],
    'csu': ['colorado state', 'colorado st', 'rams'],
    'wyo': ['wyoming', 'cowboys'],
    'unm': ['new mexico', 'lobos'],
    'afa': ['air force', 'falcons'],
    'navy': ['navy', 'midshipmen'],
    'army': ['army', 'black knights'],
    'smc': ['saint marys', "saint mary's", 'gaels'],
    'sf': ['san francisco', 'dons'],
    'gonz': ['gonzaga', 'bulldogs', 'zags'],
    'creigh': ['creighton', 'bluejays'],
    'marq': ['marquette', 'golden eagles'],
    'nova': ['villanova', 'wildcats'],
    'gtown': ['georgetown', 'hoyas'],
    'shu': ['seton hall', 'pirates'],
    'prov': ['providence', 'friars'],
    'xav': ['xavier', 'musketeers'],
    'but': ['butler', 'bulldogs'],
    'conn': ['connecticut', 'uconn', 'huskies'],
    'mem': ['memphis', 'tigers'],
    'smu': ['smu', 'southern methodist', 'mustangs'],
    'tulsa': ['tulsa', 'golden hurricane'],
    'tulane': ['tulane', 'green wave'],
}


def extract_college_school_name(vegas_name: str) -> str:
    """Extract school name from Vegas college team name (removes mascot)."""
    if not vegas_name:
        return ''
    name_lower = vegas_name.lower().strip()
    for mascot in sorted(COLLEGE_MASCOTS, key=len, reverse=True):
        if name_lower.endswith(' ' + mascot):
            name_lower = name_lower[:-len(mascot)-1].strip()
            break
    name_lower = name_lower.replace('st.', 'st').replace('state', 'st')
    name_lower = name_lower.replace("'s", 's').replace("'", '')
    return name_lower.strip()


def get_college_abbrev(team_name: str) -> str:
    """Get Kalshi abbreviation for a college team."""
    school = extract_college_school_name(team_name)
    for abbrev, names in COLLEGE_ABBREV_MAP.items():
        for name in names:
            if school == name.lower() or school.startswith(name.lower()) or name.lower() in school:
                return abbrev
    words = school.split()
    if len(words) == 1:
        return school[:3] if len(school) >= 3 else school
    return ''.join(w[0] for w in words if w)


def match_college_teams(vegas_home: str, vegas_away: str, kalshi_title: str) -> Tuple[bool, float]:
    """Match college teams between Vegas and Kalshi."""
    home_school = extract_college_school_name(vegas_home)
    away_school = extract_college_school_name(vegas_away)
    title_lower = kalshi_title.lower().replace('st.', 'st').replace("'s", 's').replace("'", '')

    home_in_title = home_school in title_lower or any(
        name.lower() in title_lower
        for name in COLLEGE_ABBREV_MAP.get(get_college_abbrev(vegas_home), [])
    )
    away_in_title = away_school in title_lower or any(
        name.lower() in title_lower
        for name in COLLEGE_ABBREV_MAP.get(get_college_abbrev(vegas_away), [])
    )

    home_score = fuzz.partial_ratio(home_school, title_lower)
    away_score = fuzz.partial_ratio(away_school, title_lower)

    if home_in_title and away_in_title:
        return True, 100.0
    elif home_score >= 80 and away_score >= 80:
        return True, (home_score + away_score) / 2
    elif (home_in_title or home_score >= 85) and (away_in_title or away_score >= 85):
        return True, max(home_score, away_score)
    return False, 0.0


def get_team_abbrev(team_name: str) -> str:
    """Get Kalshi abbreviation for a pro team name."""
    team_lower = team_name.lower().strip()
    if team_lower in FULL_NAME_TO_ABBREV:
        return FULL_NAME_TO_ABBREV[team_lower]
    normalized = normalize_team_name(team_name)
    if normalized in NICKNAME_TO_ABBREV:
        return NICKNAME_TO_ABBREV[normalized]
    return ''


def normalize_team_name(name: str) -> str:
    """Normalize team name by removing city prefixes."""
    if not name:
        return ''
    normalized = name.strip().lower()
    for prefix in sorted(CITY_PREFIXES, key=len, reverse=True):
        if normalized.startswith(prefix + ' '):
            normalized = normalized[len(prefix):].strip()
            break
    return ' '.join(normalized.split())


def calculate_team_match_score(vegas_team: str, kalshi_text: str) -> int:
    """Calculate fuzzy match score between Vegas team and Kalshi text."""
    return fuzz.partial_ratio(normalize_team_name(vegas_team), kalshi_text.lower())


class EventMatcher:
    """Matches events between Vegas and Kalshi platforms."""

    def __init__(self, match_threshold: int = 80):
        self.match_threshold = match_threshold

    def match_game_winner_markets(self, vegas_events: List[Dict],
                                   kalshi_markets: List[Dict]) -> List[Dict]:
        """Match Vegas events to Kalshi game winner markets."""
        # Group Kalshi markets by game_id
        kalshi_games = {}
        for market in kalshi_markets:
            game_id = market.get('_game_id', '')
            if not game_id:
                continue
            if game_id not in kalshi_games:
                kalshi_games[game_id] = {
                    'markets': [],
                    'title': market.get('title', ''),
                    'sport': market.get('_sport', '')
                }
            kalshi_games[game_id]['markets'].append(market)

        matches = []

        for vegas_event in vegas_events:
            vegas_home = vegas_event.get('home_team', '')
            vegas_away = vegas_event.get('away_team', '')
            sport_key = vegas_event.get('sport_key', '')
            is_college = 'ncaa' in sport_key.lower()

            if is_college:
                home_abbrev = get_college_abbrev(vegas_home)
                away_abbrev = get_college_abbrev(vegas_away)
                home_school = extract_college_school_name(vegas_home)
                away_school = extract_college_school_name(vegas_away)
            else:
                home_abbrev = get_team_abbrev(vegas_home)
                away_abbrev = get_team_abbrev(vegas_away)
                home_school = normalize_team_name(vegas_home)
                away_school = normalize_team_name(vegas_away)

            best_match = None
            best_score = 0

            for game_id, game_data in kalshi_games.items():
                title = game_data['title']
                markets = game_data['markets']
                title_lower = title.lower()

                if is_college:
                    is_match, match_confidence = match_college_teams(vegas_home, vegas_away, title)
                    if is_match:
                        combined_score = match_confidence * 2
                        if combined_score > best_score:
                            home_market, away_market = None, None
                            for m in markets:
                                team_code = m.get('_team_code', '').lower()
                                if team_code == home_abbrev:
                                    home_market = m
                                elif team_code == away_abbrev:
                                    away_market = m
                                elif fuzz.ratio(team_code, home_abbrev) >= 80 or home_school.startswith(team_code):
                                    home_market = m
                                elif fuzz.ratio(team_code, away_abbrev) >= 80 or away_school.startswith(team_code):
                                    away_market = m
                            if home_market or away_market:
                                best_score = combined_score
                                best_match = {'game_id': game_id, 'home_market': home_market,
                                            'away_market': away_market, 'title': title}
                else:
                    home_in_title = (home_school in title_lower or
                                    home_abbrev in title_lower.replace(' ', '') or
                                    (home_school.split()[-1] if home_school else '') in title_lower)
                    away_in_title = (away_school in title_lower or
                                    away_abbrev in title_lower.replace(' ', '') or
                                    (away_school.split()[-1] if away_school else '') in title_lower)

                    home_score = calculate_team_match_score(vegas_home, title)
                    away_score = calculate_team_match_score(vegas_away, title)

                    if (home_in_title and away_in_title) or (home_score >= 60 and away_score >= 60):
                        combined_score = home_score + away_score + (50 if home_in_title else 0) + (50 if away_in_title else 0)
                        if combined_score > best_score:
                            home_market, away_market = None, None
                            for m in markets:
                                team_code = m.get('_team_code', '').lower()
                                if team_code == home_abbrev:
                                    home_market = m
                                elif team_code == away_abbrev:
                                    away_market = m
                            if home_market or away_market:
                                best_score = combined_score
                                best_match = {'game_id': game_id, 'home_market': home_market,
                                            'away_market': away_market, 'title': title}

            if best_match:
                matches.append({
                    'vegas_event': vegas_event,
                    'kalshi_home_market': best_match['home_market'],
                    'kalshi_away_market': best_match['away_market'],
                    'game_id': best_match['game_id']
                })

        return matches
