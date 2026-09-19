# World Cup Oracle: 2018 Knockout Replay

This is a maintained, hindsight-informed knockout replay, not an untouched
historical snapshot or a held-out full-tournament forecast.

## Current executable result

At 50,000 simulations and seed 2018, the historical BPS is **47/64**:
16 R16 points + 10 QF + 6 SF + 5 finalist + 10 champion.
France is the predicted champion. **The 16 R16 points are supplied by actual
qualifiers, not predicted by the model.** The simulated knockout contribution
is therefore 31/48. Crossing the old 45/64 threshold is not independent validation.

## Correction and methodology

I previously described both tournaments as passing without verifying the
2022 claim. That claim is withdrawn; see the root [CHANGELOG](../CHANGELOG.md).
I also overstated comparability by omitting the supplied-qualifier limitation.

The old 83.2% blend treated the recorded France-Croatia final xG tie
(1.1 versus 1.1) as away-team dominance. Tied recorded xG is now excluded:
12/14 eligible matches agree, and the 40/30/30 exploratory index is **84.9%**.
This is not accuracy, calibration, or evidence of generalization.
Market agreement is MSE against regulation odds conditioned on no draw,
not a Brier score against actual outcomes or a probability of advancing.

The simulation result is cached so one report does not silently run multiple
different random samples. Source-linked manual data is in
`data/wc2018_market_data.py`; full caveats are in [AUDIT.md](../AUDIT.md).

## Run

From this folder:

```bash
python -m backtest.wc2018_backtest
python examples/run_backtest.py
python -m pytest -q tests/test_evaluation_audit.py
```

The example now invokes the 2018 module rather than a missing 2022 module.
The full suite now records 41 passes and 4 failures, with no collection errors
or skipped tests. The failures are three expectations needing absent Qatar
inputs in the generic scorer, and Brazil's legacy top-three historical-rank
hypothesis. Imports, compilation, and executable smoke checks pass. The copied
2022 regression file was replaced with local 2018 mechanical invariants,
not represented as 2022 tests suddenly passing. See [AUDIT.md](../AUDIT.md).
