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
  48-team scenario now incorporates referees. Its older synthetic groups advance
  only 24 teams into a knockout with byes, not the official 32-team stage.

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
advertised as a current real-world prediction. The full suite now records
37 passes and 4 failures, with no collection errors or skipped tests.
The failures are three expectations needing absent Qatar inputs in the generic
scorer, and Brazil's legacy top-three historical-rank hypothesis.
Imports, compilation, and executable smoke checks pass. The copied 2022 tests
were replaced by local scenario invariants, not empirical calibration tests.

`python examples/run_prediction.py --simulations 1000` computes the dedicated
scenario rather than printing invented probability tables or confidence
intervals. `examples/run_backtest.py` explicitly redirects to that scenario:
there is no implemented historical 2026 outcome backtest. Unsupported coach,
retirement, and ranking narratives were removed, not silently replaced by
new unverified claims. No model-accuracy or production-readiness guarantee is made.

See the root [audit](../AUDIT.md), [results](../audit/results.json), and
[correction history](../CHANGELOG.md).
