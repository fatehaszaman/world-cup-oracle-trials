# Lessons

This file records real mistakes in the World Cup Oracle projects, what caused them, and what changed. The earlier claims remain visible in Git history so the before and after can be checked. Open limitations are tracked in [AUDIT.md](AUDIT.md); this file covers corrections only.

## 1. Published a 2022 score that no run had produced

**What happened.** The [world-cup-oracle-v2](https://github.com/fatehaszaman/world-cup-oracle-v2) README claimed a 2022 result of 48/64 PASS, a separate table summed to 57, and the validation report printed a hardcoded `~48` with a PASS marker. In this repository, 2022 claims of 51/64 on all seeds and 48/64 were also published. None of these figures came from an executable run. The reproducible 2022 result for v2 is 40/64.

**Why it happened.** The figures came from hand-built tables and expected outcomes, not from the code. The v2 backtest's team-strength table was identical to v1 and never used the reweighted dimension weights, so the change v2 was meant to test was never wired into the backtest.

**What I changed.** The claims were withdrawn publicly. The v2 report now computes the 2022 row instead of printing a placeholder, and the proposed outcome table was removed from the v2 README so hand-derived targets do not sit beside actual results.

**How I prevent it now.** [`scripts/verify_consistency.py`](scripts/verify_consistency.py) recomputes the published diagnostics in isolated runs and writes [`audit/results.json`](audit/results.json), which is the source of truth for every figure in the README and AUDIT. [`scripts/check_all.py`](scripts/check_all.py) runs every test suite, import, and example entry point, with logs retained.

**History.** v2 [`f8fc4de`](https://github.com/fatehaszaman/world-cup-oracle-v2/commit/f8fc4de) (fabricated score removed, root cause recorded), v2 [`14637bc`](https://github.com/fatehaszaman/world-cup-oracle-v2/commit/14637bc) (README replaced with actual results), trials [`2f2a447`](https://github.com/fatehaszaman/world-cup-oracle-trials/commit/2f2a447) and [`58720f7`](https://github.com/fatehaszaman/world-cup-oracle-trials/commit/58720f7) (claims aligned with reproducible replays, full check evidence published).

## 2. Described a repair inaccurately

**What happened.** An earlier explanation said commit `2585839` wired in an existing 2022 form-boost table. In fact that commit added the `TOURNAMENT_FORM_BOOST_2022` table, and the table is informed by hindsight.

**Why it happened.** The explanation was written from memory of the intent rather than from the diff.

**What I changed.** The [CHANGELOG](CHANGELOG.md) states what the commit actually did and labels the form boosts as hindsight-informed.

**How I prevent it now.** Repair descriptions are written from the commit diff, not from recollection.

## 3. Presented in-sample replays as forecasting evidence

**What happened.** Historical replays were presented as if they demonstrated forecasting accuracy. The 2018 replay also supplies all actual Round of 16 qualifiers, which automatically awards 16 points.

**Why it happened.** The scoring setup was not separated from the claim being made about it.

**What I changed.** All results are labeled as historical model replays, not held-out accuracy, and the 2018 knockout contribution (31/48) is reported separately. A probability-distance metric was renamed to market agreement because it is not calibration or an outcome Brier score.

**How I prevent it now.** Before reporting a result, I state what the evaluation can and cannot show and whether any outcome information enters the inputs.
