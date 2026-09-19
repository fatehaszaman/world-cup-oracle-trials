"""Exploratory bracket, market-agreement and xG diagnostics, not accuracy.

The market target is P(home wins in regulation | no regulation draw), NOT
P(home advances). Squared distance to another probability is market MSE,
not an outcome Brier score or a calibration estimate. The model probability
is a pre-noise strength proxy, not the full simulator's advancement rate.
The 40/30/30 blend is a chosen diagnostic index, not a validated skill score.
"""
from __future__ import annotations

from math import isclose, isfinite
import config
from data.wc2018_market_data import WC2018_KNOCKOUT_MARKET as RECORDS
from oracle.var_noise import implied_win_prob


def market_agreement_score(scores: dict[str, float]) -> dict:
    rows = []
    for m in RECORDS:
        p = float(implied_win_prob(m.home, m.away, scores))
        target = m.home_win_prob / (m.home_win_prob + m.away_win_prob)
        rows.append({
            "match": f"{m.home} vs {m.away}", "stage": m.stage,
            "model_probability_proxy": p, "market_conditional_probability": target,
            "squared_error": (p - target) ** 2,
            "flat_baseline_squared_error": (0.5 - target) ** 2,
        })
    if not rows:
        raise ValueError("No market records")
    mse = sum(r["squared_error"] for r in rows) / len(rows)
    baseline = sum(r["flat_baseline_squared_error"] for r in rows) / len(rows)
    return {
        "avg_mse": mse, "score": 1.0 - mse, "n_matches": len(rows),
        "flat_baseline_mse": baseline,
        "mse_skill_vs_flat": 1.0 - mse / baseline if baseline > 0 else None,
        "per_match": rows,
    }


def xg_alignment_score(scores: dict[str, float]) -> dict:
    """Exclude tied recorded xG; award half credit to an indifferent model."""
    credit, eligible, ties = 0.0, 0, 0
    rows = []
    for m in RECORDS:
        p = float(implied_win_prob(m.home, m.away, scores))
        tied = isclose(m.home_xg, m.away_xg, abs_tol=1e-12)
        if tied:
            match_credit = None
            ties += 1
        else:
            eligible += 1
            match_credit = (
                0.5 if isclose(p, 0.5, abs_tol=1e-12)
                else float((p > 0.5) == (m.home_xg > m.away_xg))
            )
            credit += match_credit
        rows.append({
            "match": f"{m.home} vs {m.away}",
            "home_xg": m.home_xg, "away_xg": m.away_xg,
            "excluded_xg_tie": tied, "agreement_credit": match_credit,
        })
    if not eligible:
        raise ValueError("No non-tied xG records")
    return {
        "agreement_rate": credit / eligible, "score": credit / eligible,
        "agreement_credit": credit, "n_matches": eligible,
        "n_total_matches": len(RECORDS), "n_ties_excluded": ties,
        "per_match": rows,
    }


def blended_score(bracket_fraction: float, scores: dict[str, float]) -> dict:
    weights = config.EVALUATION_WEIGHTS_2018
    if not isfinite(bracket_fraction) or not 0 <= bracket_fraction <= 1:
        raise ValueError("bracket_fraction must be finite and in [0, 1]")
    if (set(weights) != {"bracket", "market_agreement", "xg_alignment"}
            or any(not isfinite(w) or w < 0 for w in weights.values())
            or not isclose(sum(weights.values()), 1.0, abs_tol=1e-9)):
        raise ValueError("Evaluation weights must be nonnegative and sum to one")
    teams = {t for m in RECORDS for t in (m.home, m.away)}
    if not teams <= scores.keys():
        raise ValueError("Missing team strengths for evaluation records")
    if any(not isfinite(scores[t]) or not 0 <= scores[t] <= 1 for t in teams):
        raise ValueError("Team strengths must be finite and in [0, 1]")
    market, xg = market_agreement_score(scores), xg_alignment_score(scores)
    return {
        "bracket_fraction": bracket_fraction, "market_agreement": market,
        "xg_alignment": xg, "weights": dict(weights),
        "blended_score": (weights["bracket"] * bracket_fraction
                          + weights["market_agreement"] * market["score"]
                          + weights["xg_alignment"] * xg["score"]),
        "interpretation": "Exploratory in-sample index, not predictive accuracy",
    }
