"""
data/wc2022_market_data.py — Real market data for 2022 World Cup knockout matches.

Added 2026-09-19 in response to the methodology critique that bracket-progression
scoring alone (bracket_progression_score / BPS) is noisy: a single-elimination
bracket has huge variance, so "how far a team went" is a weak signal of whether
the underlying win-probability model was actually well-calibrated. This module
supplies two independent, verifiable signals to evaluate against instead of
(or in addition to) pure bracket outcomes:

  1. HOME_XG / AWAY_XG — post-match Expected Goals, sourced from FBref match
     logs. xG reflects match performance/dominance and is far less noisy than
     the final scoreline (e.g. France beat Poland 3-1 in the Round of 16 but
     had LOWER xG, 1.4 vs Poland's 1.7 — the scoreline flatters France).
     Source: https://fbref.com/en/comps/1/2022/schedule/2022-World-Cup-Scores-and-Fixtures
     (per-match xG pulled directly from FBref's schedule table, retrieved 2026-09-19)

  2. HOME_WIN_PROB / DRAW_PROB / AWAY_WIN_PROB — de-vigged (normalized)
     moneyline implied probabilities from bookmaker pre-match odds, used as
     the "wisdom of the market" baseline the model should be compared against
     rather than just judged on which team happened to win a single-elimination
     coin-flip-adjacent match.
     Sources (moneyline odds converted American/fractional/decimal -> implied
     probability, then normalized to remove vig):
       R16:  PointsBet odds via NBC Los Angeles,
             https://www.nbclosangeles.com/news/sports/world-cup-2022/2022-fifa-world-cup-favorites-entering-knockout-round/3047454/
       QF:   Betfair odds via Betfair Sportsbook,
             https://betting.betfair.com/football/world-cup-2022/world-cup-quarter-final-predictions-what-the-betfair-odds-tell-us-071222-205.html
       SF:   BetMGM odds via Sporting News,
             https://www.sportingnews.com/us/soccer/news/world-cup-semifinal-predictions-odds-final-2022-qatar/sm3meufqdkbe393i7tibw5at
       Final: PointsBet odds via NBC Sports,
             https://www.nbcsports.com/soccer/news/world-cup-2022-odds-favorites-underdogs-winners-semifinal-games-details

All matches keyed as (home_team, away_team) matching the pairing FBref lists
the fixture under (not necessarily "home" in a neutral-site tournament sense —
just the side FBref/bookmakers list first).
"""

from __future__ import annotations

from typing import NamedTuple


class KnockoutMarketRecord(NamedTuple):
    stage: str            # "r16" | "qf" | "sf" | "final"
    home: str
    away: str
    home_xg: float
    away_xg: float
    home_win_prob: float  # de-vigged moneyline implied probability
    draw_prob: float
    away_win_prob: float
    actual_winner: str    # winner after extra time / penalties (bracket outcome)


WC2022_KNOCKOUT_MARKET: list[KnockoutMarketRecord] = [
    # --- Round of 16 ---
    KnockoutMarketRecord("r16", "Netherlands", "USA",          1.7, 1.5, 0.5039, 0.2770, 0.2191, "Netherlands"),
    KnockoutMarketRecord("r16", "Argentina",   "Australia",    1.6, 0.6, 0.7873, 0.1453, 0.0675, "Argentina"),
    KnockoutMarketRecord("r16", "France",      "Poland",       1.4, 1.7, 0.7396, 0.1812, 0.0792, "France"),
    KnockoutMarketRecord("r16", "England",     "Senegal",      0.9, 0.7, 0.6216, 0.2408, 0.1376, "England"),
    KnockoutMarketRecord("r16", "Japan",       "Croatia",      1.2, 1.4, 0.2502, 0.2971, 0.4527, "Croatia"),
    KnockoutMarketRecord("r16", "Brazil",      "South Korea",  3.6, 0.5, 0.7705, 0.1570, 0.0724, "Brazil"),
    KnockoutMarketRecord("r16", "Morocco",     "Spain",        0.7, 1.0, 0.1362, 0.2509, 0.6129, "Morocco"),
    KnockoutMarketRecord("r16", "Portugal",    "Switzerland",  2.3, 1.1, 0.5129, 0.2740, 0.2131, "Portugal"),
    # --- Quarter-finals ---
    KnockoutMarketRecord("qf", "Croatia",      "Brazil",       0.6, 2.5, 0.1014, 0.1925, 0.7061, "Croatia"),
    KnockoutMarketRecord("qf", "Netherlands",  "Argentina",    0.6, 1.9, 0.2634, 0.3058, 0.4309, "Argentina"),
    KnockoutMarketRecord("qf", "Morocco",      "Portugal",     1.4, 0.9, 0.1706, 0.2607, 0.5688, "Morocco"),
    KnockoutMarketRecord("qf", "England",      "France",       2.4, 0.9, 0.3177, 0.2933, 0.3891, "France"),
    # --- Semi-finals ---
    KnockoutMarketRecord("sf", "Argentina",    "Croatia",      2.3, 0.5, 0.5093, 0.2860, 0.2047, "Argentina"),
    KnockoutMarketRecord("sf", "France",       "Morocco",      2.0, 0.9, 0.6128, 0.2421, 0.1452, "France"),
    # --- Final ---
    KnockoutMarketRecord("final", "Argentina", "France",       3.2, 2.2, 0.3409, 0.3182, 0.3409, "Argentina"),
]


def get_matches_by_stage(stage: str) -> list[KnockoutMarketRecord]:
    """Return all knockout market records for a given stage."""
    return [m for m in WC2022_KNOCKOUT_MARKET if m.stage == stage]
