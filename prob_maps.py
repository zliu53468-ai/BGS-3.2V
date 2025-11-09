# prob_maps.py  — flat import version

def _get_cross_line(leg, kind: str, side_hint=None):
    c = leg.get("_cross") or {}
    if kind == "spread":
        sp = c.get("spread") or {}
        if side_hint in ("home","away") and side_hint in sp:
            return float(sp[side_hint])
        return float(sp.get("home") or sp.get("away") or 0.0)
    if kind == "totals":
        tot = c.get("totals") or {}
        return float(tot.get("over") or tot.get("under") or 0.0)
    return None

def prob_for_leg(leg):
    sport = leg["sport"]
    market = leg["market"]
    side = leg.get("side","home")

    if sport == "basketball":
        from basketball_normal import BasketballNormal
        spread_line = float(leg["line"]) if market=="spread" and leg.get("line") is not None else _get_cross_line(leg,"spread",side_hint=side)
        total_line  = float(leg["line"]) if market=="totals" and leg.get("line") is not None else _get_cross_line(leg,"totals")
        m = BasketballNormal.from_market(spread_line=spread_line, total_line=total_line)
        if market == "moneyline":
            return m.p_moneyline_home() if side=="home" else 1-m.p_moneyline_home()
        if market == "spread":
            line = float(leg["line"])
            return m.p_cover_home(line) if side=="home" else 1-m.p_cover_home(-line)
        if market == "totals":
            line = float(leg["line"])
            return m.p_total_over(line) if side=="over" else 1-m.p_total_over(line)

    if sport == "football":
        from soccer_dc_poisson import SoccerDCPoisson
        totals_line = float(leg["line"]) if market=="totals" and leg.get("line") is not None else _get_cross_line(leg,"totals")
        tot_mu = totals_line if totals_line else 2.55
        hmu = 0.55 * tot_mu
        amu = 0.45 * tot_mu
        s = SoccerDCPoisson(home_mu=hmu, away_mu=amu, rho=0.05, maxg=10)
        if market == "moneyline":
            ph, pd, pa = s.prob_moneyline()
            return ph if side=="home" else (pa if side=="away" else pd)
        if market == "spread":
            line = float(leg["line"])
            return s.prob_handicap_home(line) if side=="home" else 1 - s.prob_handicap_home(-line)
        if market == "totals":
            line = float(leg["line"])
            over = s.prob_total_over(line)
            return over if side=="over" else 1 - over

    if sport == "baseball":
        from baseball_nb import BaseballNB
        totals_line = float(leg["line"]) if market=="totals" and leg.get("line") is not None else _get_cross_line(leg,"totals")
        b = BaseballNB.from_total(totals_line)
        if market == "moneyline":
            p = b.p_home_win()
            return p if side=="home" else 1-p
        if market == "totals":
            line = float(leg["line"])
            over = b.p_total_over(line)
            return over if side=="over" else 1-over
        if market == "spread":
            line = float(leg.get("line",-1.5))
            if side=="home":
                return b.p_runline_home(line)
            return 1 - b.p_runline_home(-line)

    return 0.5
