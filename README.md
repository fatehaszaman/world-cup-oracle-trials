# World Cup Oracle: Trials

An experimental football simulation project with explicit failure history.
The current folders are maintained code, not immutable snapshots. Earlier
versions remain in Git history. These are exploratory replays, not validated
out-of-sample forecasts.

## Acknowledging my testing mistake

I published passing backtest scores before checking that the committed code
reproduced them. The earlier 2022 claims of **51/64 on all seeds** and **48/64**
were unsupported and inconsistent. I should have verified the executable
results and evaluation assumptions before presenting those claims.

The first correction also overstated what had been fixed: the 2022 form-boost
table was added in commit `2585839`, not merely reconnected to existing code.
Its outcome-informed adjustments introduce hindsight. Reproducing a higher
score with those adjustments does not validate the original claim.

See [AUDIT.md](AUDIT.md) for the current results, limitations, test status,
and corrections. [CHANGELOG.md](CHANGELOG.md) preserves the explanation rather
than silently replacing the earlier claims.

## Current results

Settings: 50,000 simulations; seed 42 for 2022, seed 2018 for 2018.
The historical BPS threshold is 45/64, not a statistical validation test.

| Folder | BPS | Historical threshold | Predicted champion | Interpretation |
|---|---:|---|---|---|
| `2022-backtest` | 50/64 | Above threshold | Argentina | Hindsight-adjusted replay; not held-out accuracy |
| `2018-backtest` | 47/64 | Above threshold | France | Includes 16 points for actual R16 qualifiers supplied as inputs |
| `2026-prediction` | Not evaluated | Not applicable | No current verified claim | Static scenario inputs, not a live data feed |

The 2018 knockout-only contribution is **31/48**. Its 47/64 score must not be
compared as if all 64 points were independently predicted. Seed sensitivity
must be measured at a specified simulation count; no all-seeds guarantee is made.

## Requested methodology changes

- **Mixed evaluation:** 40% bracket fraction, 30% market agreement index,
  and 30% xG agreement. These weights are assumptions, not fitted or validated.
- **Betting-market comparison:** Mean squared distance to de-vigged regulation
  odds conditioned on no draw. This is not outcome Brier score, calibration,
  or a direct comparison with betting odds to advance.
- **xG evaluation:** Compares the model's favored side with higher recorded
  xG across knockout matches, excluding the third-place game. Tied recorded
  xG is excluded; an indifferent model receives half credit.
- **Referee dampening:** `REFEREE_BIAS_WEIGHT_2026 = 0.35` in the optional
  `TournamentSimulator.simulate_match()` referee path. It preserves draw
  probability. The weight is a heuristic, not an estimated VAR effect.
  The separate `WC2026Forecast` engine has no referee-assignment input.

The previous 2018 blend of 83.2% incorrectly treated tied xG as favoring the
away side. With the tie excluded, its exploratory index is **84.9%**
(12/14 eligible matches agree). The 2022 index is **85.0%** (12/15 agree).
Neither percentage is predictive accuracy. See the raw MSE and baseline
comparison in [audit/results.json](audit/results.json).

## Run and verify

```bash
git clone https://github.com/fatehaszaman/world-cup-oracle-trials.git
cd world-cup-oracle-trials
python -m pip install -r 2022-backtest/requirements.txt pytest
python scripts/verify_consistency.py
# Optional, slower seed sensitivity:
python scripts/verify_consistency.py --seed-grid
# Also compare v1/v2 if their clones are sibling directories:
python scripts/verify_consistency.py --baselines
```

Each folder's README gives its own runnable entry point. Focused audit tests
pass, and the full suites now collect without errors. Across the three trial
folders, 125 tests pass and 12 fail; none are skipped. The remaining failures
are disclosed in [AUDIT.md](AUDIT.md), not hidden with relaxed thresholds.
This repository does not claim an all-green suite or production readiness.

For full isolated tests, module imports, compilation, and executable smoke
checks, run `python scripts/check_all.py`. Add `--baselines` to include sibling
v1/v2 clones. This command intentionally exits nonzero while failures remain;
it writes evidence under `audit/checks/`. Smoke examples use 16 simulations
to check execution only, not to substantiate the published 50,000-run scores.

## Related repositories

- [Original baseline](https://github.com/fatehaszaman/world-cup-oracle):
  2022 BPS 40/64 at 50,000 simulations, seed 42.
- [v2 experiment](https://github.com/fatehaszaman/world-cup-oracle-v2):
  2022 BPS 40/64; 2018 BPS 25/64 at their documented settings.
  Its proposed dimension reweighting is not used by its fixed-score 2022 backtest.

Maintained by [fatehaszaman](https://github.com/fatehaszaman).
