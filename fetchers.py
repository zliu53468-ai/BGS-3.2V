import time, requests
from typing import List, Dict, Tuple
from config import CFG
from normalize import abbr3, season_from_date  # 扁平匯入

APIFOOTBALL_KEY = CFG["APIFOOTBALL_KEY"]
ODDS_API_KEY = CFG["ODDS_API_KEY"]

def _get_json(url: str, headers=None, params=None, timeout=15, retry=2, backoff=0.6):
    err = None
    for i in range(retry + 1):
        try:
            r = requests.get(url, headers=headers or {}, params=params or {}, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            err = e
            if i < retry:
                time.sleep(backoff * (i + 1))
    raise err

_odds_cache: Dict[str, Dict] = {}
_scores_cache: Dict[Tuple[str,str], Dict] = {}

def _get_cached(cache: Dict, key, ttl: int):
    now = time.time()
    item = cache.get(key)
    if item and now - item["t"] < ttl:
        return item["data"]
    return None

def _set_cache(cache: Dict, key, data):
    cache[key] = {"t": time.time(), "data": data}

def fetch_epl_fixtures_results(date_iso: str) -> Dict:
    key = ("EPL", date_iso)
    hit = _get_cached(_scores_cache, key, CFG["CACHE_SEC_SCORES"])
    if hit is not None:
        return hit
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": APIFOOTBALL_KEY} if APIFOOTBALL_KEY else {}
    params = {"date": date_iso, "league": 39}
    data = _get_json(url, headers=headers, params=params)
    sched, results = [], []
    for g in data.get("response", []):
        fx = g["fixture"]; tm = g["teams"]; gl = g["goals"]
        gid = _mk_gid("EPL", fx["date"], tm["home"]["name"], tm["away"]["name"])
        sched.append({
            "game_id": gid, "date": fx["date"][:10], "start_time_utc": fx["date"],
            "league": "EPL", "season": season_from_date("EPL", fx["date"]),
            "home_team": tm["home"]["name"], "away_team": tm["away"]["name"],
            "venue": (fx.get("venue") or {}).get("name","")
        })
        if gl["home"] is not None and gl["away"] is not None:
            winner = "home" if gl["home"]>gl["away"] else ("away" if gl["home"]<gl["away"] else "draw")
            results.append({
                "game_id": gid, "home_points": gl["home"], "away_points": gl["away"],
                "winner": winner, "total_points": gl["home"] + gl["away"]
            })
    out = {"schedule": sched, "results": results}
    _set_cache(_scores_cache, key, out)
    return out

def fetch_odds_raw(league_key: str) -> List[Dict]:
    url = f"https://api.the-odds-api.com/v4/sports/{league_key}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu,uk,us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "decimal",
        "dateFormat": "iso"
    }
    data = _get_json(url, params=params)
    legs = []
    for e in data:
        lg = _league_tag(league_key)
        date_iso = e["commence_time"]
        home = e["home_team"]; away = e["away_team"]
        gid = _mk_gid(lg, date_iso, home, away)
        market_blob = {"moneyline":{}, "spread":{}, "totals":{}}
        for bk in e.get("bookmakers", []):
            bkname = bk["title"]
            for mk in bk.get("markets", []):
                mkey = mk["key"]; ts = mk["last_update"]
                if mkey == "h2h":
                    for o in mk["outcomes"]:
                        side = "home" if o["name"]==home else "away"
                        legs.append({
                            "game_id": gid, "timestamp_utc": ts, "bookmaker": bkname,
                            "market": "moneyline", "side": side, "line": "",
                            "odds_decimal": float(o["price"])
                        })
                        market_blob["moneyline"][side] = float(o["price"])
                elif mkey == "spreads":
                    for o in mk["outcomes"]:
                        side = "home" if o["name"]==home else "away"
                        legs.append({
                            "game_id": gid, "timestamp_utc": ts, "bookmaker": bkname,
                            "market": "spread", "side": side,
                            "line": float(o["point"]), "odds_decimal": float(o["price"])
                        })
                        market_blob["spread"][side] = float(o["point"])
                elif mkey == "totals":
                    for o in mk["outcomes"]:
                        side = "over" if o["name"].lower()=="over" else "under"
                        legs.append({
                            "game_id": gid, "timestamp_utc": ts, "bookmaker": bkname,
                            "market": "totals", "side": side,
                            "line": float(o["point"]), "odds_decimal": float(o["price"])
                        })
                        market_blob["totals"][side] = float(o["point"])
        for L in legs:
            if L["game_id"] == gid:
                L["_cross"] = market_blob
    return legs

def fetch_odds_cached(league_key: str) -> List[Dict]:
    ttl = CFG["CACHE_SEC_ODDS"]; stale = CFG["STALE_SEC_ODDS"]; now = time.time()
    item = _odds_cache.get(league_key)
    if item and now - item["t"] < ttl:
        return item["data"]
    try:
        data = fetch_odds_raw(league_key)
        _odds_cache[league_key] = {"t": now, "data": data}
        return data
    except Exception:
        item = _odds_cache.get(league_key)
        if item and now - item["t"] < stale:
            return item["data"]
        return []

def fetch_nba_games(date_iso: str) -> Dict:
    key = ("NBA", date_iso)
    hit = _get_cached(_scores_cache, key, CFG["CACHE_SEC_SCORES"])
    if hit is not None: return hit
    url = "https://api.balldontlie.io/v1/games"
    params = {"dates[]": date_iso, "per_page": 100}
    data = _get_json(url, params=params)
    sched, results = [], []
    for g in data.get("data", []):
        gid = _mk_gid("NBA", g["date"], g["home_team"]["full_name"], g["visitor_team"]["full_name"])
        sched.append({
            "game_id": gid, "date": g["date"][:10], "start_time_utc": g["date"],
            "league": "NBA", "season": season_from_date("NBA", g["date"]),
            "home_team": g["home_team"]["full_name"], "away_team": g["visitor_team"]["full_name"], "venue": ""
        })
        if g["status"].lower()=="final":
            winner = "home" if g["home_team_score"]>g["visitor_team_score"] else "away"
            results.append({
                "game_id": gid, "home_points": g["home_team_score"], "away_points": g["visitor_team_score"],
                "winner": winner, "total_points": g["home_team_score"] + g["visitor_team_score"]
            })
    out = {"schedule": sched, "results": results}
    _set_cache(_scores_cache, key, out)
    return out

def fetch_mlb_games(date_iso: str) -> Dict:
    key = ("MLB", date_iso)
    hit = _get_cached(_scores_cache, key, CFG["CACHE_SEC_SCORES"])
    if hit is not None: return hit
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_iso}&language=en"
    data = _get_json(url)
    sched, results = [], []
    for d in data.get("dates", []):
        for g in d.get("games", []):
            home = g["teams"]["home"]["team"]["name"]; away = g["teams"]["away"]["team"]["name"]
            gid = _mk_gid("MLB", g["gameDate"], home, away)
            sched.append({
                "game_id": gid, "date": date_iso, "start_time_utc": g["gameDate"],
                "league": "MLB", "season": str(g.get("season","")),
                "home_team": home, "away_team": away, "venue": g.get("venue", {}).get("name","")
            })
            if g["status"]["abstractGameState"].lower() == "final":
                ls = g.get("linescore", {})
                hp = (ls.get("teams", {}).get("home", {}) or {}).get("runs")
                ap = (ls.get("teams", {}).get("away", {}) or {}).get("runs")
                if hp is not None and ap is not None:
                    results.append({
                        "game_id": gid, "home_points": hp, "away_points": ap,
                        "winner": "home" if hp>ap else ("away" if ap>hp else "draw"),
                        "total_points": hp+ap
                    })
    out = {"schedule": sched, "results": results}
    _set_cache(_scores_cache, key, out)
    return out

def _league_tag(league_key: str) -> str:
    return {"soccer_epl":"EPL","basketball_nba":"NBA","baseball_mlb":"MLB"}.get(league_key, "LG")

def _mk_gid(league_tag: str, date_iso: str, home_name: str, away_name: str) -> str:
    return f'{league_tag}{date_iso[:10].replace("-","")}_{abbr3(home_name)}_{abbr3(away_name)}'
