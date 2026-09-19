"""Local replay invariants, replacing copied tests of a nonexistent 2022 module.

These checks validate mechanics, not predictive calibration or held-out skill.
"""
import pytest
from backtest.wc2018_backtest import WC2018BacktestV3, WC2018_R16_QUALIFIERS


@pytest.fixture(scope="module")
def replay():
    return WC2018BacktestV3(n_simulations=256, seed=2018)


@pytest.mark.parametrize("key,total", [
    ("r16_probs", 16), ("qf_probs", 8), ("sf_probs", 4),
    ("fin_probs", 2), ("champion_probs", 1),
])
def test_round_probability_mass(replay, key, total):
    assert sum(replay.run()[key].values()) == pytest.approx(total)
    assert all(0 <= p <= 1 for p in replay.run()[key].values())


def test_r16_is_supplied_not_predicted(replay):
    assert {t for t, p in replay.run()["r16_probs"].items() if p == 1} == WC2018_R16_QUALIFIERS


def test_seed_reproducible_and_report_uses_cached_sample(replay):
    result = replay.run()
    assert replay.run() is result
    assert result == WC2018BacktestV3(n_simulations=256, seed=2018).run()
