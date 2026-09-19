# World Cup Oracle: Correction History

Git history preserves prior versions. The working folders are maintained
experiments, not frozen failure snapshots. The current source of truth is
[AUDIT.md](AUDIT.md) plus the reproducible [results file](audit/results.json).

## 2026-09-19: Consistency audit

I take responsibility for publishing score claims before verifying the
committed code and for presenting in-sample replays too strongly. The
correction should be visible, not hidden by deleting the failure history.

- Withdrew the inconsistent 2022 claims of 51/64 on all seeds and 48/64.
- Corrected the earlier repair explanation: commit `2585839` ADDED the
  `TOURNAMENT_FORM_BOOST_2022` table. It was not an existing table merely
  waiting to be imported. Coach adjustment code did exist but was not called
  by that backtest. The new form boosts are hindsight-informed.
- Retained the reproducible 2022 default BPS of 50/64 and 2018 BPS of 47/64,
  but removed the implication that these prove forecasting accuracy.
- Disclosed that the 2018 replay supplies all actual R16 qualifiers and
  automatically receives 16 BPS points. Its knockout contribution is 31/48.
- Renamed the probability-distance metric to market MSE/agreement, not
  calibration or outcome Brier score. Conditional regulation probabilities
  are not probabilities of advancing.
- Fixed tied-xG treatment. The 2018 exploratory index changed from 83.2%
  to 84.9% because a tied recorded final is excluded, not assigned to Croatia.
  This change is not a forecasting improvement.
- Cached 2018 run results so one report uses one simulation sample.
- Fixed the 2018 example's import of a nonexistent 2022 module.
- Fixed the referee adjustment to preserve draw mass and neutral-referee
  invariance. Its 0.35 weight remains a heuristic, not a fitted VAR effect.
- Clarified that this referee path is separate from `WC2026Forecast`.
- Replaced stale live-forecast and all-tests-passing claims with explicit
  limitations. Added focused regression tests and a result-generation script.

## Earlier iterations

- Original `world-cup-oracle`: 2022 BPS 40/64, below the historical threshold.
- `world-cup-oracle-v2`: 2022 BPS 40/64 and 2018 BPS 25/64. The proposed
  dimension reweighting is not used by its fixed-score 2022 backtest.
  Its prior 48/64 badge, hand-derived 57-point table, and hardcoded PASS
  display were not verified results.
- Trials prior to `2585839`: the original score claims were unsupported.
  The earlier audit reported a 35/64 result for the pre-fix code; that is a
  historical observation, not a current run or a claim about every seed.
- Trials at `2585839`: introduced blended diagnostics and form/coach
  adjustments, but the first documentation correction still contained
  overclaims and inconsistent snapshot language. This audit corrects those too.

Replaying an old version requires checking out its exact Git commit. Running
today's folder cannot reproduce an old version simply because its name is unchanged.
