# server.py  — flat layout ready for Render + LINE router
from fastapi import FastAPI, Query
from config import CFG
from fetchers import fetch_odds_cached
from prob_maps import prob_for_leg
from policy import approve_leg
from picker import pick_best_parlays

app = FastAPI(title="Sports Parlay API")

BOOKMAKER_ALIAS = {
    "panda": {"熊貓體育", "Panda", "PandaBet", "PANDA", "panda"},
    "super": {"Super 體育", "Super", "SuperBet", "SUPER", "super"},
}

def detect_sport_from_league(league: str) -> str:
    league = (league or "").upper()
    if league in ["NBA","CBA","WNBA"]: return "basketball"
    if league in ["EPL","UCL","LALIGA","SERIEA","BUNDES","LIGUE1","J1","K1"]: return "football"
    if league in ["MLB","NPB","KBO"]: return "baseball"
    return "basketball"

def filter_channel(legs, channel):
    if not channel: return legs
    alias = BOOKMAKER_ALIAS.get(channel.lower())
    if not alias: return legs
    return [x for x in legs if x.get("bookmaker") in alias]

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/parlay")
def parlay_api(league: str = Query("NBA"),
               date: str = Query(None),    # date 目前只當展示用
               legs: int = Query(3),
               market_filter: str = Query("mixed"),
               channel: str = Query(None)):
    lkey = {"EPL": "soccer_epl", "NBA": "basketball_nba", "MLB": "baseball_mlb"}.get(league.upper(), "basketball_nba")
    odds_rows = fetch_odds_cached(lkey)

    cands = []
    for r in odds_rows:
        if market_filter != "mixed" and r["market"] != market_filter:
            continue
        cands.append({
            "sport": detect_sport_from_league(league),
            "league": league,
            "game_id": r["game_id"],
            "market": r["market"],
            "side": r["side"],
            "line": (None if r["line"]=="" else r["line"]),
            "odds": float(r["odds_decimal"]),
            "bookmaker": r["bookmaker"],
            "_cross": r.get("_cross")
        })

    use_channel = channel or CFG["DEFAULT_CHANNEL"]
    cands = filter_channel(cands, use_channel)

    pool=[]
    for leg in cands:
        p = prob_for_leg(leg)
        ok, ev = approve_leg(p, float(leg["odds"]))
        if ok:
            pool.append({**leg, "p": p, "ev": ev})

    picks = pick_best_parlays(pool, max_legs=legs, topk=3)
    return {"league": league, "date": date, "channel": use_channel, "parlays": picks}

# ---- LINE router (mounted) ----
try:
    # 修正點：根目錄版，從 app.py 匯入 router
    from app import router as line_router
    app.include_router(line_router)   # /callback 對外開放
except Exception:
    # 若還沒設定好 LINE 金鑰，先讓 API 起來；之後再重啟
    pass
