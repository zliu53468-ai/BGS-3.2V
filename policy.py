from config import CFG

def ev_of_bet(p: float, odds: float) -> float:
    """
    以本金1為基準的預期值：
    EV = p*(odds-1) - (1-p)*1
    回傳值 > 0 代表正期望
    """
    return p * (odds - 1.0) - (1.0 - p)

def approve_leg(p: float, odds: float):
    ev = ev_of_bet(p, odds)
    return ev >= CFG["MIN_EV_EDGE_LEG"], ev
