"""
oracle/blended_evaluation.py — Mixed real-outcome / market / xG evaluation.

Added 2026-09-19, extending the same methodology change made to
2022-backtest/oracle/blended_evaluation.py to this repo. See that module's
docstring for full rationale: bracket-progression scoring (BPS) alone is
noisy, so this blends it with betting-market calibration (Brier score) and
xG-based match-dominance agreement. Data sourced in
data/wc2018_market_data.py.

Note: unlike the 2022 backtest, this repo's classic BPS (47/64) was already
independently verified accurate before this change — this is a methodology
improvement layered on top of a correct baseline, not a correction.
"""

from __future__ import annotations

from data.wc2018_market_data import WC2018_KNOCKOUT_MARKET
from oracle.var_noise import implied_win_prob

import config


def market_calibration_score(scores: dict[str, float]) -> dict:
    """Brier-score calibration of model win probability vs betting-market
    implied probability, renormalized to 2-way (home vs away), across all
    15 real 2018 knockout matches."""
    briers: list[float] = []
    per_match: list[dict] = []

    for m in WC2018_KNOCKOUT_MARKET:
        model_p_home = implied_win_prob(m.home, m.away, scores)
        market_p_home_2way = m.home_win_prob / (m.home_win_prob + m.away_win_prob)
        brier = (model_p_home - market_p_home_2way) ** 2
        briers.append(brier)
        per_match.append({
            "stage": m.stage,
            "match": f"{m.home} vs {m.away}",
            "model_p_home": round(model_p_home, 3),
            "market_p_home": round(market_p_home_2way, 3),
            "brier": round(brier, 4),
        })

    avg_brier = sum(briers) / len(briers)
    return {
        "avg_brier": avg_brier,
        "score": 1.0 - avg_brier,
        "n_matches": len(briers),
        "per_match": per_match,
    }


def xg_alignment_score(scores: dict[str, float]) -> dict:
    """Fraction of knockout matches where the model's favored team matches
    the team with the higher actual xG."""
    agreements = 0
    per_match: list[dict] = []

    for m in WC2018_KNOCKOUT_MARKET:
        model_p_home = implied_win_prob(m.home, m.away, scores)
        model_favors_home = model_p_home > 0.5
        xg_favors_home = m.home_xg > m.away_xg
        agree = model_favors_home == xg_favors_home
        agreements += int(agree)
        per_match.append({
            "stage": m.stage,
            "match": f"{m.home} vs {m.away}",
            "model_favors": m.home if model_favors_home else m.away,
            "xg_favors": m.home if xg_favors_home else m.away,
            "xg": f"{m.home_xg}-{m.away_xg}",
            "agree": agree,
        })

    n = len(WC2018_KNOCKOUT_MARKET)
    return {
        "agreement_rate": agreements / n,
        "score": agreements / n,
        "n_matches": n,
        "per_match": per_match,
    }


def blended_score(bracket_fraction: float, scores: dict[str, float]) -> dict:
    """Combine bracket-outcome, market-calibration, and xG-alignment scores
    per config.EVALUATION_WEIGHTS_2018."""
    market = market_calibration_score(scores)
    xg = xg_alignment_score(scores)
    weights = config.EVALUATION_WEIGHTS_2018

    blended = (
        weights["bracket"] * bracket_fraction
        + weights["market_calibration"] * market["score"]
        + weights["xg_alignment"] * xg["score"]
    )

    return {
        "bracket_fraction": bracket_fraction,
        "market_calibration": market,
        "xg_alignment": xg,
        "weights": weights,
        "blended_score": blended,
    }
