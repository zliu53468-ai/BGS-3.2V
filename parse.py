import re
from datetime import datetime
from datasource.normalize import norm_team

def parse_user_text(t: str):
    txt = (t or "").lower().replace("（"," ").replace("）"," ").strip()
    league = "NBA"
    if any(k in txt for k in ["epl","英超"]): league="EPL"
    if "mlb" in txt: league="MLB"
    if "nba" in txt: league="NBA"

    legs = 3
    m = re.search(r'(\d+)\s*腿', txt) or re.search(r'\b(\d)\b', txt)
    if m: legs = max(2, min(5, int(m.group(1))))

    market="mixed"
    if any(k in txt for k in ["讓分","spread"]): market="spread"
    if any(k in txt for k in ["大小","over","under","totals"]): market="totals"
    if any(k in txt for k in ["獨贏","moneyline","ml"]): market="moneyline"

    profile="一般風險"
    if "保守" in txt: profile="保守風險"
    if "進取" in txt: profile="進取風險"

    channel=None
    if ("熊貓" in txt) or ("panda" in txt): channel = "panda"
    if ("super" in txt): channel = "super"

    dm = re.search(r'(\d{4}-\d{2}-\d{2})', txt)
    date = dm.group(1) if dm else datetime.utcnow().date().isoformat()

    teams=[]
    vs = re.search(r'([a-z\u4e00-\u9fa5\.\s]+)\s*(對|vs)\s*([a-z\u4e00-\u9fa5\.\s]+)', txt)
    if vs:
        a = vs.group(1).strip(); b = vs.group(3).strip()
        teams = [norm_team(league, a), norm_team(league, b)]

    return {"league": league, "legs": legs, "market": market,
            "risk": profile, "channel": channel, "date": date, "teams": teams}
