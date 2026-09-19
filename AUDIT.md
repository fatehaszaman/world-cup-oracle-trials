# World Cup Oracle: Consistency Audit

Audit date: 2026-09-19. This document distinguishes executable results from
validation claims. The accompanying [JSON](audit/results.json) was generated
by [verify_consistency.py](scripts/verify_consistency.py), not hand-entered.

## Scope and current results

This audit covers the three World Cup repositories, their top-level and
folder READMEs, GitHub descriptions, and the `fatehaszaman` profile README/bio.
It is not an audit of every unrelated portfolio project.

| Repository / replay | Simulations | Seed | BPS | Predicted champion |
|---|---:|---:|---:|---|
| Original / 2022 | 50,000 | 42 | 40/64 | France |
| v2 / 2022 | 50,000 | 42 | 40/64 | France |
| v2 / 2018 | 50,000 | 2018 | 25/64 | Germany |
| Trials / 2022 | 50,000 | 42 | 50/64 | Argentina |
| Trials / 2018 | 50,000 | 2018 | 47/64 | France |

The old pass threshold was BPS >= 45/64. Crossing it is not statistical
evidence of generalization. BPS sums 16 R16 + 16 QF + 12 SF + 10 finalist
+ 10 champion points, maximum 64.

The trials 2018 replay starts with actual R16 qualifiers and bracket.
It receives 16 points from supplied information; its knockout-only result
is 31/48. The 2022 trial applies retrospective form boosts.
Neither result should be described as leakage-free pre-tournament validation.
The optional seed-grid command is available, but this checked-in audit record
contains the documented default seeds, not an all-seeds guarantee.

## Mixed evaluation: what the numbers mean

| Diagnostic | Trials 2022 | Trials 2018 |
|---|---:|---:|
| Bracket fraction | 50/64 | 47/64, including supplied R16 points |
| Market probability-distance MSE | 0.00910923 | 0.00677659 |
| Flat 0.5 proxy MSE | 0.07912283 | 0.04009728 |
| Market agreement index, 1 minus MSE | 0.99089077 | 0.99322341 |
| xG agreement | 12/15 = 80.0% | 12/14 = 85.7%; one recorded tie excluded |
| 40/30/30 exploratory blend | 0.84976723 | 0.84885988 |

These indices are not accuracy percentages. In particular, 1 minus a small
probability-distance MSE can be near one without demonstrating calibration.
The weights 0.40/0.30/0.30 are chosen, not fitted on a held-out dataset.
No betting-profit, predictive superiority, or uncertainty-interval claim follows.

The market target is `home / (home + away)` from de-vigged regulation odds.
It means regulation victory conditioned on no draw, not advancement after
extra time or penalties. The comparison uses the model's deterministic
strength-probability proxy, not its full simulated advancement probability.
This limitation must be resolved before treating the metric as like-for-like
bookmaker benchmarking.

The xG metric uses 15 knockout fixtures per tournament, excluding third place.
Tied recorded xG is excluded; model indifference receives half credit.
The earlier 2018 blend of 83.2% assigned the tied final to the away team;
84.9% is the corrected index, not an improvement to predictions.
xG is provider-dependent, rounded in these fixtures, and may include extra
time. It is not a regulation-only target aligned perfectly with the market.

## Input provenance and leakage limits

Source URLs are recorded in
[2018 data](2018-backtest/data/wc2018_market_data.py) and
[2022 data](2022-backtest/data/wc2022_market_data.py).
The original xG citations are:

- [FBref 2018 schedule](https://fbref.com/en/comps/1/2018/schedule/2018-World-Cup-Scores-and-Fixtures).
- [FBref 2022 schedule](https://fbref.com/en/comps/1/2022/schedule/2022-World-Cup-Scores-and-Fixtures).

These are manual, source-linked transcriptions. Raw odds, publication-time
snapshots, per-row extraction evidence, and a reproducible conversion pipeline
are not stored. This consistency audit did not independently re-source every
row. Treat the fixtures as provisional research inputs, not fully audited data.
Historical strength, coach, and form features also lack a complete as-of-date
provenance contract. Outcome-informed tuning and future-era information must
be removed before an honest held-out evaluation can be run.

## Referee adjustment

The configurable 0.35 adjustment is implemented only in
`2026-prediction/oracle/monte_carlo.py` for a supplied referee.
The correction preserves draw probability and leaves neutral-referee
probabilities unchanged. The value is an assumption, not a measured VAR effect.

The separate `backtest/wc2026_forecast.py` uses no referee assignments.
Its static inputs, strength-based selection of third-place qualifiers, and
simplified knockout mapping are scenario assumptions, not a verified live
tournament feed. Neither its output nor the historical README's sample
championship probabilities are presented as current verified forecasts.

## Test status

Environment: Python 3.14. Focused audit tests pass: 9 for each historical
evaluation module and 4 for referee invariants, 22 total.
Seven additional checks validate the published result arithmetic and README
claims against the generated record, for 29 targeted checks in total.

Legacy-suite results before adding those focused tests:

| Suite | Passed | Failed | Collection errors |
|---|---:|---:|---:|
| Original | 9 | 26 | 0 |
| v2 | 9 | 26 | 0 |
| Trials 2018 | 0 | 22 | 1 |
| Trials 2022 | 12 | 23 | 0 |
| Trials 2026 | 0 | 22 | 1 |

Command: `python -m pytest -q --continue-on-collection-errors`, separately
inside each folder. These failures remain open, not silently skipped or
relabeled as passing. They include stale simulator/scorer API expectations,
missing imports in legacy folders, and probability assertions.
Focused audit tests do not establish that the whole project works.

## Reproduce and prevent drift

From the trials root, `python scripts/verify_consistency.py` recomputes both
default trial results. `--baselines` adds sibling v1/v2 clones;
`--seed-grid` adds seeds 0-9 and takes longer. Save output as
`audit/results.json` when intentionally refreshing the published record.
Run each folder's focused test command from its README.

All current READMEs distinguish original, v2, and trials rather than claiming
identical scores across different model versions. Historical unsupported
figures appear only as withdrawn claims. See [CHANGELOG.md](CHANGELOG.md)
for the personal acknowledgment and correction sequence.
