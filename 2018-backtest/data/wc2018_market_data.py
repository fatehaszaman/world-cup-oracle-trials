"""
data/wc2018_market_data.py — Real market data for 2018 World Cup knockout matches.

Added 2026-09-19 alongside the equivalent 2022-backtest module, extending the
same mixed real-outcome / betting-market / xG evaluation methodology to the
2018 backtest (see oracle/blended_evaluation.py). The 2018 backtest's classic
bracket-progression score (BPS) was independently verified accurate (47/64,
matching the README) before this change — this addition is a methodology
improvement, not a correction of a wrong number.

Sources:
  xG — FBref match logs:
    https://fbref.com/en/comps/1/2018/schedule/2018-World-Cup-Scores-and-Fixtures
    (retrieved 2026-09-19)
  Betting odds — American moneyline odds (home/draw/away), de-vigged and
  normalized to probabilities. Retrieved 2026-09-19 from:
    R16 France-Argentina:     CBS Sports, https://www.cbssports.com/soccer/news/world-cup-2018-argentina-vs-france-odds-lines-expert-picks-and-top-insider-predictions/
    R16 Uruguay-Portugal:     CBS Sports, https://www.cbssports.com/soccer/news/world-cup-2018-portugal-vs-uruguay-odds-lines-expert-picks-and-insider-predictions/
    R16 Spain-Russia:         CBS Sports, https://www.cbssports.com/soccer/news/world-cup-2018-spain-vs-russia-odds-lines-expert-picks-and-insider-predictions/
    R16 Croatia-Denmark:      CBS Sports, https://www.cbssports.com/soccer/news/world-cup-2018-denmark-vs-croatia-odds-lines-expert-picks-and-top-insider-predictions/
    R16 Brazil-Mexico:        CBS Sports, https://www.cbssports.com/soccer/news/2018-world-cup-mexico-vs-brazil-odds-lines-expert-picks-and-insider-predictions/
    R16 Belgium-Japan:        Get More Sports, https://www.getmoresports.com/2018-world-cup-odds-belgium-vs-japan-betting-preview-free-pick/
    R16 Sweden-Switzerland:   Action Network, https://www.actionnetwork.com/soccer/world-cup-public-betting-tuesday-switzerland-sweden-england-colombia
    R16 England-Colombia:     Action Network, https://www.actionnetwork.com/soccer/world-cup-public-betting-tuesday-switzerland-sweden-england-colombia
    QF  Uruguay-France:       CBS Sports, https://www.cbssports.com/soccer/news/world-cup-2018-odds-lines-in-quarterfinals-brazil-the-one-to-beat-england-huge-favorite-to-advance/
    QF  Brazil-Belgium:       CBS Sports, https://www.cbssports.com/soccer/news/world-cup-2018-belgium-vs-brazil-odds-lines-expert-picks-and-top-insider-predictions/
    QF  Sweden-England:       CBS Sports, https://www.cbssports.com/soccer/news/world-cup-2018-odds-lines-in-quarterfinals-brazil-the-one-to-beat-england-huge-favorite-to-advance/
    QF  Russia-Croatia:       CBS Sports, https://www.cbssports.com/soccer/news/world-cup-2018-croatia-vs-russia-odds-lines-expert-picks-and-insider-predictions/
    SF  France-Belgium:       CBS Sports, https://www.cbssports.com/soccer/world-cup/news/world-cup-odds-lines-france-the-favorite-to-win-it-all-england-favored-to-beat-croatia/
    SF  Croatia-England:      CBS Sports, https://www.cbssports.com/soccer/world-cup/news/world-cup-odds-lines-france-the-favorite-to-win-it-all-england-favored-to-beat-croatia/
    Final France-Croatia:     CBS Sports, https://www.cbssports.com/soccer/news/2018-world-cup-final-croatia-vs-france-odds-betting-lines-expert-picks-insider-predictions/
"""

from __future__ import annotations

from typing import NamedTuple


class KnockoutMarketRecord(NamedTuple):
    stage: str
    home: str
    away: str
    home_xg: float
    away_xg: float
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    actual_winner: str


WC2018_KNOCKOUT_MARKET: list[KnockoutMarketRecord] = [
    # --- Round of 16 ---
    KnockoutMarketRecord("r16", "France",  "Argentina",   2.2, 0.8, 0.3991, 0.3192, 0.2817, "France"),
    KnockoutMarketRecord("r16", "Uruguay", "Portugal",    0.6, 1.0, 0.3392, 0.3333, 0.3275, "Uruguay"),
    KnockoutMarketRecord("r16", "Spain",   "Russia",      1.8, 1.0, 0.6041, 0.2498, 0.1461, "Russia"),
    KnockoutMarketRecord("r16", "Croatia", "Denmark",     2.5, 0.9, 0.5179, 0.2922, 0.1899, "Croatia"),
    KnockoutMarketRecord("r16", "Brazil",  "Mexico",      2.7, 0.7, 0.6404, 0.2315, 0.1281, "Brazil"),
    KnockoutMarketRecord("r16", "Belgium", "Japan",       2.5, 0.7, 0.6970, 0.2054, 0.0976, "Belgium"),
    KnockoutMarketRecord("r16", "Sweden",  "Switzerland", 1.3, 0.7, 0.3090, 0.3321, 0.3589, "Sweden"),
    KnockoutMarketRecord("r16", "England", "Colombia",    2.1, 0.6, 0.4533, 0.2999, 0.2468, "England"),
    # --- Quarter-finals ---
    KnockoutMarketRecord("qf", "Uruguay", "France",   0.9, 0.5, 0.2113, 0.3018, 0.4869, "France"),
    KnockoutMarketRecord("qf", "Brazil",  "Belgium",  2.8, 0.5, 0.4560, 0.2816, 0.2624, "Belgium"),
    KnockoutMarketRecord("qf", "Sweden",  "England",  0.5, 1.0, 0.2005, 0.2801, 0.5194, "England"),
    KnockoutMarketRecord("qf", "Russia",  "Croatia",  1.0, 1.7, 0.2580, 0.3121, 0.4300, "Croatia"),
    # --- Semi-finals ---
    KnockoutMarketRecord("sf", "France",   "Belgium", 1.7, 0.4, 0.3807, 0.3021, 0.3172, "France"),
    KnockoutMarketRecord("sf", "Croatia",  "England", 1.7, 0.6, 0.3002, 0.2911, 0.4087, "Croatia"),
    # --- Final ---
    KnockoutMarketRecord("final", "France", "Croatia", 1.1, 1.1, 0.4993, 0.2889, 0.2118, "France"),
]


def get_matches_by_stage(stage: str) -> list[KnockoutMarketRecord]:
    """Return all knockout market records for a given stage."""
    return [m for m in WC2018_KNOCKOUT_MARKET if m.stage == stage]
