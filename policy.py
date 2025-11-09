from config import CFG
from pricing.ev import ev_of_bet

def approve_leg(p: float, odds: float):
    ev = ev_of_bet(p, odds)
    return ev >= CFG["MIN_EV_EDGE_LEG"], ev

