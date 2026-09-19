"""
oracle/blended_evaluation.py — Mixed real-outcome / market / xG evaluation.

Added 2026-09-19 in response to a direct methodology critique: scoring a
single-elimination bracket purely on "how far each team went"
(bracket_progression_score / BPS) is noisy — one shootout or one deflected
goal flips a team's entire bracket outcome regardless of how good the
underlying win-probability estimate was. This module adds two lower-variance,
independently-sourced signals and blends all three into one score:

  1. bracket   — the original BPS (real tournament outcomes), kept because
                 actually predicting the right outcome still matters.
  2. market    — Brier-score calibration of the model's implied win
                 probability against real pre-match betting-market implied
                 probabilities (data/wc2022_market_data.py). Lower Brier is
                 better; reported here as (1 - Brier) so higher = better,
                 consistent with the other two components.
  3. xg        — agreement rate between the model's per-match favorite and
                 the team with the higher actual post-match Expected Goals
                 (xG), a better proxy for match dominance than the final
                 scoreline (e.g. France beat Poland 3-1 in the R16 but had
                 LOWER xG, 1.4 vs 1.7 — the scoreline flatters France).

Weights are configurable via config.EVALUATION_WEIGHTS_2022 (default: equal
thirds). This does NOT replace bracket_progression_score()/
print_validation_report() — it is an additional, more robust view alongside
the classic BPS, and both are reported together.
"""

from __future__ import annotations

from data.wc2022_market_data import WC2022_KNOCKOUT_MARKET
from oracle.var_noise import implied_win_prob

import config


def market_calibration_score(scores: dict[str, float]) -> dict:
    """
    Brier-score calibration of the model's deterministic win probability
    against real betting-market implied probabilities, for every knockout
    match. Market's 3-way (home/draw/away) probability is renormalized to a
    2-way home-vs-away probability (draws don't exist as a final knockout
    outcome), matching the model's own knockout resolution.
    """
    briers: list[float] = []
    per_match: list[dict] = []

    for m in WC2022_KNOCKOUT_MARKET:
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
        "score": 1.0 - avg_brier,   # higher = better, in [0, 1]-ish range
        "n_matches": len(briers),
        "per_match": per_match,
    }


def xg_alignment_score(scores: dict[str, float]) -> dict:
    """
    Fraction of knockout matches where the model's favored team (implied
    win probability > 0.5) matches the team with the higher actual xG —
    i.e. did the model correctly identify who actually dominated the match,
    independent of the noisy scoreline/shootout result.
    """
    agreements = 0
    per_match: list[dict] = []

    for m in WC2022_KNOCKOUT_MARKET:
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

    n = len(WC2022_KNOCKOUT_MARKET)
    return {
        "agreement_rate": agreements / n,
        "score": agreements / n,
        "n_matches": n,
        "per_match": per_match,
    }


def blended_score(bracket_fraction: float, scores: dict[str, float]) -> dict:
    """
    Combine bracket-outcome, market-calibration, and xG-alignment scores
    into one weighted blend, per config.EVALUATION_WEIGHTS_2022.

    Parameters
    ----------
    bracket_fraction : float
        The classic BPS total, expressed as a fraction of 64 (e.g. 50/64 ->
        0.781), so all three components are on a comparable 0-1 scale.
    scores : dict[str, float]
        Final (form + coach adjusted) team-strength scores used for the run.
    """
    market = market_calibration_score(scores)
    xg = xg_alignment_score(scores)
    weights = config.EVALUATION_WEIGHTS_2022

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
