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

The full follow-up recomputed all five published 50,000-simulation replays;
their numeric results match the table and stored record. The only record
difference was unordered missed-team lists in v2's 2018 report. Those lists
now sort deterministically; no scores or predicted outcomes changed.

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

Latest full check: Python 3.14.3, 2026-09-19. Each project is run in its own
process so identically named `config`, `oracle`, and `backtest` modules do
not leak between folders. Full logs, JUnit XML, command return codes, and
machine-readable counts are under [audit/checks](audit/checks).

| Suite | Passed | Failed | Collection errors |
|---|---:|---:|---:|
| Original | 34 | 8 | 0 |
| v2 | 34 | 8 | 0 |
| Trials 2018 | 41 | 4 | 0 |
| Trials 2022 | 47 | 4 | 0 |
| Trials 2026 | 37 | 4 | 0 |

Total: 193 passed, 28 failed, no skipped tests. Seven separate root publication
checks pass, giving 200 passing checks when those are included. The 22 focused
evaluation/referee tests from the first audit are included in these counts,
not additional to them. The project is still not all green.

All 105 discovered modules in `oracle`, `data`, and `backtest` import
successfully. Compilation succeeds in all five folders. Each folder's
prediction, backtest, and benchmark script executes successfully with a
16-simulation smoke sample, 15 script checks total. The 2026 backtest-named
compatibility script explicitly runs a static scenario, not a historical
2026 evaluation. Smoke results are not replacements for the 50,000-run table.
Live third-party APIs and every possible configuration are not covered.

Remaining failures:

- Three checks in each folder require Qatar in the generic scorer. Its static
  input table has 32 teams and no Qatar, whereas generic scenario groups have
  48. Missing-team defaults are now shown consistently and disclosed in the
  example, but they are not verified team data. Inventing a Qatar rating just
  to make assertions pass would not resolve this input limitation.
- One check in each folder expects Brazil in the top three historical scores;
  the implemented recent-editions score ranks Brazil fourth. The expectation
  is retained rather than adjusting the scoring model to satisfy it.
- Four extra checks in each of v1/v2 fail their original France/Australia,
  Brazil/South Korea, Portugal/Switzerland, and Saudi Arabia/Argentina
  probability bounds. Those bounds were not relaxed or described as validated.

For comparison, before the initial focused tests and follow-up repairs,
v1/v2 each had 9 passes and 26 failures; trials 2018/2026 each had 22 failures
plus a collection error; trials 2022 had 12 passes and 23 failures. Counts
are not directly comparable as evidence of model improvement: obsolete API
tests were migrated and invalid cross-folder tests were replaced.

## Follow-up repairs and test migration

- Replaced nonexistent `MonteCarloSimulator` calls and score-object fields
  with the implemented `TournamentSimulator` API and numeric scorer output.
  The known input key is `United States`, not the obsolete `USA` alias.
- Replaced copied 2022 regression files in the 2018 and 2026 folders with
  local replay/scenario invariants. Those 2022 tests were never applicable
  there; this is explicitly not a claim that they became passing calibrations.
- Preserved the bottom-three probability cutoff while including ties. Qatar
  and four other teams had zero simulated title probability in the 2022 test;
  insertion order had incorrectly excluded Qatar.
- Added the missing 2018 match-simulation constant. Repaired examples and the
  benchmark API, removed fabricated forecast tables/intervals, and corrected
  benchmark bytes-to-MiB conversion. Runtime is measured, not guaranteed.
- Fixed generic knockout completion: the old fixed four-round loop could stop
  with two survivors and assign a winner without a final. The engine now plays
  exactly n-minus-one eliminations, grants first-round byes where needed, and
  records rounds reached rather than rounds won. Tests cover 2, 3, 8, 16, 24,
  and 32 entrants and ensure that the last match determines the champion.
- Brought generic simulator repairs into both older trial folders, including
  unique pairings, accurate output labels, and referee draw-mass preservation.
  The 0.35 referee dampening remains specific to the 2026 generic module.
- Withdrew unsupported live-data, coach, retirement, ranking, universal runtime,
  and simulation-accuracy narratives. No newly invented facts replace them.
- Removed README MIT-license labels from the three World Cup repositories
  because no corresponding license file is committed; no new license grant
  was introduced. The profile repository's separate license is unchanged.

The generic engine still advances only two teams from each synthetic group:
24 knockout entrants with byes, not an official 2026 bracket. It is distinct
from the dedicated 48-to-32 scenario and from the scored historical engines.
These generic repairs do not tune the historical backtest probability models.

## Authorship and publication

The checked GitHub contributor lists for v1, v2, trials, and the profile
repository contain only `fatehaszaman`. GitHub displays the account name,
not an email address, in its contributor interface. The requested
`fateha.szaman@gmail.com` is the account's verified primary email and the
author/committer identity for these maintenance commits. Earlier linked
identities remain in history; no force-push or authorship rewrite was performed.

## Reproduce and prevent drift

From the trials root, `python scripts/verify_consistency.py` recomputes both
default trial results. `--baselines` adds sibling v1/v2 clones;
`--seed-grid` adds seeds 0-9 and takes longer. Save output as
`audit/results.json` when intentionally refreshing the published record.
Run each folder's focused test command from its README.

`python scripts/check_all.py --baselines` runs every full suite, imports,
compilation, and executable smoke test described above. Omit `--baselines`
when the sibling repositories are absent. `python -m pytest -q audit_tests`
runs the separate publication checks. The full-check command correctly exits
nonzero while any suite fails; it does not skip or relabel those failures.

All current READMEs distinguish original, v2, and trials rather than claiming
identical scores across different model versions. Historical unsupported
figures appear only as withdrawn claims. See [CHANGELOG.md](CHANGELOG.md)
for the personal acknowledgment and correction sequence.
