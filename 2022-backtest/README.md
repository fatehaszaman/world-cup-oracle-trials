# World Cup Oracle: 2022 Replay

This folder contains the current exploratory replay, not a pinned v2 snapshot.
Earlier failures remain in Git history and the root [CHANGELOG](../CHANGELOG.md).

## Current executable result

At 50,000 simulations and seed 42, BPS is **50/64**, with Argentina selected
as champion. The stage points are 12 + 12 + 6 + 10 + 10. This exceeds the
historical 45/64 threshold but does not establish out-of-sample skill.

The prior 51/64 all-seeds claim was unsupported. The added
`TOURNAMENT_FORM_BOOST_2022` table and coach adjustments change the model;
the form boosts reflect knowledge of tournament performance. These are
hindsight experiments, not proof that the original test passed.

## Evaluation

The exploratory 40/30/30 bracket/market/xG index is 85.0% at these settings,
not 85.0% prediction accuracy. Market comparison uses probability-distance
MSE, not calibration or outcome Brier score. The target conditions regulation
odds on no draw and is not a bookmaker advancement probability.
Recorded xG agreement is 12/15 knockout matches, excluding the third-place game.

Source URLs are recorded in `data/wc2022_market_data.py`; the fixture is a
manual transcription, not a reproducible raw-odds ingestion pipeline.
See [AUDIT.md](../AUDIT.md) for provenance and comparability limitations.

## Run

From this folder:

```bash
python -m backtest.wc2022_backtest
python -m pytest -q tests/test_evaluation_audit.py
```

For the seed grid and cross-repository comparison, use the root
`scripts/verify_consistency.py`. Legacy tests still fail; the focused
evaluation tests do not certify the rest of the model.
