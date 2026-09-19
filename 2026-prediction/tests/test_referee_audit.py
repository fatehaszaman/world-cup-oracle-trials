from unittest.mock import patch
import numpy as np
import pytest
import oracle.monte_carlo as mc


class Bias:
    def __init__(self, delta):
        self.delta = delta

    def get_match_bias_factor(self, *args, base_prob_a, **kwargs):
        p = base_prob_a + self.delta
        return {"adjusted_prob_a": p, "adjusted_prob_b": 1 - p,
                "bias_magnitude": abs(self.delta)}


def simulate(delta, weight, referee=True):
    sim = mc.TournamentSimulator()
    sim._referee_bias_analyzer = Bias(delta)
    with patch.object(mc, "REFEREE_BIAS_WEIGHT_2026", weight):
        return sim.simulate_match(
            "France", "Argentina", {"France": 0.8, "Argentina": 0.7},
            n_simulations=10000, referee="fixture" if referee else None,
            rng=np.random.default_rng(42),
        )


def test_neutral_referee_preserves_all_probabilities():
    base, neutral = simulate(0, 0, False), simulate(0, 0.35)
    assert neutral["referee_adjusted"]
    for key in ("win_prob_a", "win_prob_b", "draw_prob"):
        assert neutral[key] == base[key]


@pytest.mark.parametrize("weight", [0, 0.35, 1])
def test_dampening_preserves_draw_mass_and_scales_adjustment(weight):
    base, adjusted = simulate(0, 0, False), simulate(0.1, weight)
    assert adjusted["draw_prob"] == base["draw_prob"]
    assert adjusted["win_prob_a"] - base["win_prob_a"] == pytest.approx(
        (1 - base["draw_prob"]) * 0.1 * weight, abs=1e-6
    )
    assert sum(adjusted[k] for k in ("win_prob_a", "win_prob_b", "draw_prob")) == pytest.approx(1)
    assert adjusted["referee_bias_magnitude"] == pytest.approx(0.1 * weight)
