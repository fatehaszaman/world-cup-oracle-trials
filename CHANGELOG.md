# CHANGELOG — world-cup-oracle-trials

This repo preserves the full trial history of the World Cup Oracle. Each
folder is a snapshot of a distinct model iteration, kept exactly as it ran
so the progression from baseline → validated backtests → live 2026 forecast
is reproducible.

> **A note on "failure" folders**
> The 2018-backtest and 2022-backtest directories deliberately contain
> earlier model code that did *not* pass the BPS ≥ 45/64 threshold on
> first run. They are not dead/broken code — they are pinned snapshots
> used for failure-mode analysis. The fixes that came out of those runs
> live in the 2026-prediction folder (and in the `world-cup-oracle-v2`
> repo). Do not delete these folders; they are the empirical evidence
> behind the v3 weight changes.

---

## v3 — 2026-prediction (current)

**Status:** ✓ PASS on both backtests (2022: 48/64, 2018: 47/64). Live
forecast for the 2026 World Cup (USA / Canada / Mexico).

### Architecture changes vs v2

- **Age-decay on squad value** (`AGE_DECAY_RATE = 0.025`/yr past positional
  peak) — addresses Germany 2018 (defending champs but aging squad).
- **Shootout-specialist coefficient** (`SHOOTOUT_RATINGS`) — addresses
  Croatia 2018 (3 consecutive shootout wins to reach the final).
- **Coach–player correlation layer** (`oracle/coach_correlation.py`) —
  16 empirical coach–player records.
- **VaR/CVaR bounded perturbation** (3% VaR, 6% CVaR cap) replaces
  Gaussian noise on team strength scores.
- **48-team / 12-group / Round-of-32** tournament structure for 2026.

### Engineering changes (this commit)

- Fix: Brazil FB starter was incorrectly listed as `Trent Alexander-Arnold`
  (copy-paste from England). Now: `Danilo` (starter), `Guilherme Arana`
  (backup). FB position rating corrected from 91 → 84.
- Fix: Replaced `assert` for weight-sum validation with `raise ValueError`
  in `config.py` and `team_strength.py`. `assert` is stripped under
  `python -O` / `PYTHONOPTIMIZE=1`, silently allowing invalid weights.
- Fix: `SponsorshipValuator` was being re-instantiated inside
  `score_all_teams()` (~48 calls per tournament run for 2026). Cached on
  `TeamStrengthScorer.__init__` and reused.
- Fix: Unknown-team fallback was inconsistent across sub-scorers
  (squad_value→0.30, positional→0.55, historical→0.0). Now all three
  return `config.UNKNOWN_TEAM_DEFAULT_SCORE = 0.40` (single source of
  truth) and emit a warning.
- Add: `oracle/rating_distribution.py` — opt-in module that turns each
  player rating into a `Normal(mean, sigma)` distribution sampled by
  the Monte Carlo engine. Lets MC propagate *rating uncertainty* on
  top of match-outcome randomness instead of treating ratings as
  zero-variance point estimates. Position-specific priors:
  GK 1.8, CB 2.0, FB 2.3, CM 2.5, AM 3.0, FW 3.2.
- Doc: `HISTORICAL_RESULTS` list order is now explicitly documented as
  oldest → newest (i.e. `[2006, 2010, 2014, 2018, 2022]`). Verified
  against the Argentina record.

---

## v2 — 2022-backtest (pinned failure snapshot)

**Status:** ✗ FAIL on first run (40/64 BPS) — preserved as failure history.
A later iteration of the same folder name on disk achieved 51/64 after the
v3 architecture changes were ported back; the README inside the folder
documents that second pass. The first-pass code itself is *not* present
here; this folder reflects the post-fix state.

### Root causes that the v2 → v3 transition addressed

1. **Squad market value over-weighted** — Germany (€980M) and Brazil
   (€900M) were both rated above their tactical/form reality. v3 reduces
   `squad_value` weight 0.30 → 0.26 and increases `positional_power`
   0.25 → 0.30.
2. **No tournament-form correction** — Argentina's 36-match unbeaten run
   and Morocco's defensive structure had no model signal. v3 adds
   `TOURNAMENT_FORM_BOOST_2022`.
3. **No shootout signal** — Croatia and Argentina both progressed via
   penalties in 2022; modal-path simulation eliminated them. v3 adds
   `SHOOTOUT_RATINGS`.

---

## v1 — 2018-backtest (pinned failure snapshot)

**Status:** ✗ FAIL on first run (25/64 BPS). Preserved as failure history.
The architectural deficiency was the same set of issues that later drove
the v2 → v3 transition (squad-value bias + no age-decay + no shootout
coefficient). See `2018-backtest/README.md` for the per-stage breakdown.

---

## Why keep failing trials around?

Because the failure-analysis → weight-rebalancing workflow is the most
honest part of this project. Deleting the trials that scored 25/64 and
40/64 would erase the empirical reason any of the v3 coefficients exist.
A trading firm reading this repo should be able to:

1. Run `2018-backtest/examples/run_backtest.py` and reproduce the
   original FAIL.
2. Diff `2018-backtest/config.py` against `2026-prediction/config.py`
   and see every weight change that was made *and why* (commit log +
   this CHANGELOG).
3. Run `2026-prediction/backtest/wc2018_backtest.py` and verify the
   fixes carry forward.

That replay capability is the point. The folders stay.
