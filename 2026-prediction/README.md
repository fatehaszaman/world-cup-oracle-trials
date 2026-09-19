# World Cup Oracle: 2026 Scenario

This folder is experimental simulation code with static inputs. It is not a
live forecast or an up-to-date verified feed of squads, coaches, groups, or
results. Earlier README statements implying current data or validated
championship accuracy are withdrawn.

## Two distinct simulation paths

- **`backtest/wc2026_forecast.py`:** A 48-team scenario using hand-set strengths,
  simplified third-place selection, and a simplified bracket. It does not
  consume referee assignments or call `TournamentSimulator.simulate_match()`.
  Its static assumptions require verification before real-world use.
- **`oracle/monte_carlo.py`:** The generic `TournamentSimulator` includes an
  optional referee adjustment in `simulate_match()`. This is the path changed
  by the referee-dampening request. It is not evidence that the separate
  48-team scenario now incorporates referees.

## Referee change

`REFEREE_BIAS_WEIGHT_2026 = 0.35` scales the optional adjustment within the
decisive-outcome probability mass, preserving draw probability. A neutral
referee must leave all probabilities unchanged. The value is a modeling
assumption, not an empirically estimated effect of VAR.

```bash
# From this folder:
python -m pytest -q tests/test_referee_audit.py
python -m backtest.wc2026_forecast
```

The forecast command runs a static scenario; its output should not be
advertised as a current real-world prediction. Focused referee tests pass;
the legacy suite has failures and a collection error. No tests-passing badge,
model-accuracy guarantee, or production-readiness claim is made.

See the root [audit](../AUDIT.md), [results](../audit/results.json), and
[correction history](../CHANGELOG.md).
