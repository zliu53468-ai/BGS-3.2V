from datetime import datetime
import difflib

TEAM_ALIAS_NBA = {
    "湖人":"LAL","lal":"LAL","los angeles lakers":"LAL","l.a. lakers":"LAL",
    "勇士":"GSW","gsw":"GSW","golden state warriors":"GSW",
    "塞爾提克":"BOS","boston celtics":"BOS","bos":"BOS",
    "熱火":"MIA","miami heat":"MIA","mia":"MIA",
}
TEAM_ALIAS_EPL = {
    "曼城":"MCI","manchester city":"MCI","man city":"MCI","mci":"MCI",
    "曼聯":"MUN","manchester united":"MUN","man united":"MUN","mun":"MUN",
    "切爾西":"CHE","chelsea":"CHE","che":"CHE",
    "利物浦":"LIV","liverpool":"LIV","liv":"LIV",
}
TEAM_ALIAS_MLB = {
    "洋基":"NYY","new york yankees":"NYY","yankees":"NYY","nyy":"NYY",
    "紅襪":"BOS","boston red sox":"BOS","red sox":"BOS","bos":"BOS",
}

def _dict_for(league: str):
    lg = (league or "").upper()
    if lg == "NBA": return TEAM_ALIAS_NBA
    if lg == "EPL": return TEAM_ALIAS_EPL
    if lg == "MLB": return TEAM_ALIAS_MLB
    return {}

def norm_team(league: str, name: str) -> str:
    if not name: return ""
    key = name.strip().lower()
    d = _dict_for(league)
    if key in d: return d[key]
    # 模糊比對
    cand = difflib.get_close_matches(key, d.keys(), n=1, cutoff=0.78)
    if cand: return d[cand[0]]
    return name[:3].upper()

def season_from_date(league: str, date_iso: str) -> str:
    d = datetime.fromisoformat(date_iso.replace("Z",""))
    y, m = d.year, d.month
    lg = (league or "").upper()
    if lg in ["NBA","EPL"]:
        start = y if m >= 7 else y - 1
        return f"{start}-{(start+1)%100:02d}"
    if lg == "MLB":
        return str(y)
    return str(y)

def abbr3(name: str) -> str:
    return (name or "")[:3].upper()
