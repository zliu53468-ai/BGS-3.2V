import os

def env(key, default=None, cast=str):
    v = os.getenv(key, default)
    if cast and v is not None:
        try:
            if cast == bool:
                return str(v).lower() in ["1","true","yes","y","t"]
            if cast == list:
                return [x.strip() for x in str(v).split(",") if x.strip()]
            return cast(v)
        except Exception:
            return default
    return v

CFG = {
    "SPORTS": env("SPORTS", "football,basketball,baseball", list),
    "LEAGUES": env("LEAGUES", "EPL,NBA,MLB", list),
    "DECISION_MODE": env("DECISION_MODE", "hybrid"),
    "MIN_EV_EDGE_LEG": env("MIN_EV_EDGE_LEG", 0.02, float),
    "P_MIN_PARLAY": env("P_MIN_PARLAY", 0.18, float),
    "MAX_LEGS": env("MAX_LEGS", 3, int),
    "COPULA_RHO_SAMEGAME": env("COPULA_RHO_SAMEGAME", 0.35, float),
    "COPULA_RHO_XGAME": env("COPULA_RHO_XGAME", 0.05, float),
    "MC_SIMS": env("MC_SIMS", 50000, int),

    "BANKROLL": env("BANKROLL", 10000.0, float),
    "KELLY_FRACTION_PARLAY": env("KELLY_FRACTION_PARLAY", 0.15, float),
    "MAX_BET_PCT_PARLAY": env("MAX_BET_PCT_PARLAY", 0.01, float),
    "DAILY_STOP_LOSS_PCT": env("DAILY_STOP_LOSS_PCT", 0.06, float),
    "SHOW_ONLY_IF_BET": env("SHOW_ONLY_IF_BET", 1, int),

    "PORT": env("PORT", 8000, int),
    "LINE_CHANNEL_SECRET": env("LINE_CHANNEL_SECRET", ""),
    "LINE_CHANNEL_ACCESS_TOKEN": env("LINE_CHANNEL_ACCESS_TOKEN", ""),
    "DEFAULT_CHANNEL": env("DEFAULT_CHANNEL", "panda"),

    "APIFOOTBALL_KEY": env("APIFOOTBALL_KEY", ""),
    "ODDS_API_KEY": env("ODDS_API_KEY", ""),

    "CACHE_SEC_ODDS": env("CACHE_SEC_ODDS", 60, int),
    "STALE_SEC_ODDS": env("STALE_SEC_ODDS", 600, int),
    "CACHE_SEC_SCORES": env("CACHE_SEC_SCORES", 300, int),
}
