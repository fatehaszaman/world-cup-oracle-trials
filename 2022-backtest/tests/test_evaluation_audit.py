"""Focused correctness tests; not a claim that the legacy suite passes."""
import math
from unittest.mock import patch
import pytest
import oracle.blended_evaluation as evaluation


def strengths():
    return {t: 0.5 for m in evaluation.RECORDS for t in (m.home, m.away)}


def test_conditional_market_probability_and_mse():
    row = evaluation.RECORDS[0]
    with patch.object(evaluation, "RECORDS", [row]):
        result = evaluation.market_agreement_score(strengths())
    target = row.home_win_prob / (row.home_win_prob + row.away_win_prob)
    assert result["avg_mse"] == pytest.approx((0.5 - target) ** 2)
    assert result["mse_skill_vs_flat"] == pytest.approx(0)


def test_tied_xg_is_excluded_not_an_away_win():
    row = evaluation.RECORDS[0]
    records = [row._replace(home_xg=1, away_xg=1),
               row._replace(home_xg=2, away_xg=1)]
    with patch.object(evaluation, "RECORDS", records):
        result = evaluation.xg_alignment_score(strengths())
    assert result["n_ties_excluded"] == 1
    assert result["n_matches"] == 1
    assert result["score"] == 0.5  # indifferent model, not away preference


def test_only_tied_xg_is_not_a_perfect_score():
    with patch.object(evaluation, "RECORDS", [
        evaluation.RECORDS[0]._replace(home_xg=1, away_xg=1)
    ]):
        with pytest.raises(ValueError):
            evaluation.xg_alignment_score(strengths())


def test_blend_matches_formula():
    result = evaluation.blended_score(0.5, strengths())
    assert result["blended_score"] == pytest.approx(
        0.4 * 0.5 + 0.3 * result["market_agreement"]["score"]
        + 0.3 * result["xg_alignment"]["score"]
    )
    assert result["weights"] == {
        "bracket": 0.4, "market_agreement": 0.3, "xg_alignment": 0.3
    }


@pytest.mark.parametrize("value", [-1, 2, math.nan])
def test_invalid_bracket_rejected(value):
    with pytest.raises(ValueError):
        evaluation.blended_score(value, strengths())


def test_missing_scores_are_not_silent_defaults():
    with pytest.raises(ValueError):
        evaluation.blended_score(0.5, {})


def test_fixture_integrity():
    assert len(evaluation.RECORDS) == 15
    assert len({(m.home, m.away) for m in evaluation.RECORDS}) == 15
    for m in evaluation.RECORDS:
        assert m.home_xg >= 0 and m.away_xg >= 0
        assert abs(m.home_win_prob + m.draw_prob + m.away_win_prob - 1) < 0.0003
        assert m.actual_winner in (m.home, m.away)
