"""Dedicated scenario invariants, not copied 2022 calibration assertions."""
import pytest
from backtest.wc2026_forecast import WC2026Forecast, ALL_2026_TEAMS, _SQUAD_SCORES_2026


@pytest.fixture(scope="module")
def results():
    return WC2026Forecast(n_simulations=256, seed=2026).run()


@pytest.mark.parametrize("key,total", [
    ("r32_probs", 32), ("r16_probs", 16), ("qf_probs", 8),
    ("sf_probs", 4), ("finalist_probs", 2), ("champion_probs", 1),
])
def test_round_probability_mass(results, key, total):
    assert set(results[key]) == set(ALL_2026_TEAMS)
    assert sum(results[key].values()) == pytest.approx(total)
    assert all(0 <= p <= 1 for p in results[key].values())


def test_unique_participants_and_complete_strengths():
    assert len(ALL_2026_TEAMS) == len(set(ALL_2026_TEAMS)) == 48
    assert set(ALL_2026_TEAMS) <= _SQUAD_SCORES_2026.keys()


def test_seed_reproducibility(results):
    assert results == WC2026Forecast(n_simulations=256, seed=2026).run()
