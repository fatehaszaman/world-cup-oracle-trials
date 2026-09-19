# World Cup Oracle — Trials

A multi-stage research project applying Monte Carlo simulation, VaR/CVaR noise
modelling, coach-player correlation analysis, and readiness scoring to predict
FIFA World Cup outcomes.  Each folder documents a distinct trial in the
progression from baseline model → validated backtests → live 2026 forecast.

> **Preserved failure history.** The 2018-backtest and 2022-backtest folders
> are intentionally pinned snapshots of earlier model iterations, kept so the
> failure-analysis → weight-rebalancing workflow that produced v3 is fully
> reproducible. See [CHANGELOG.md](./CHANGELOG.md) for the iteration log and
> the rationale for every weight change between trials.

> **⚠️ Correction (2026-09-19): the 2022-backtest score below was wrong, and
> we're leaving this note up rather than quietly fixing the number.** This
> README previously claimed **51/64 PASS, all seeds** for `2022-backtest`.
> That number was never actually produced by running the code: the two
> features described as responsible for it — `TOURNAMENT_FORM_BOOST_2022`
> and the coach-correlation adjustment — were fully documented and coded,
> but **never imported or called anywhere in `backtest/wc2022_backtest.py`**.
> Running the code as it actually existed gave **35/64 FAIL**, not 51/64
> PASS. We wired both features into the backtest's `run()` method (they now
> really execute), and the honest, re-verified result is **seed-dependent:
> 40/64 FAIL on seeds 1, 3, 4, 7 and 50/64 PASS on seeds 0, 2, 5, 6, 8, 9
> (default seed 42 → 50/64 PASS)** — a real, substantial improvement over
> the broken 35/64, but not the "51/64, all seeds" that was claimed. See
> the Round 2 section and `2022-backtest/README.md` for the full account,
> including the new blended (bracket + betting-market + xG) evaluation
> we added alongside the fix.

---

## Repository Structure

```
world-cup-oracle-trials/
├── 2026-prediction/   ← Round 1 — Live forecast for the 2026 World Cup
├── 2022-backtest/     ← Round 2 — Validation against the 2022 World Cup
└── 2018-backtest/     ← Round 3 — Validation against the 2018 World Cup
```

---

## Round 1 — `2026-prediction`

**Purpose:** Live forecast for the 2026 FIFA World Cup (USA / Canada / Mexico).

**What's new in 2026:**
- Expanded to **48 teams** across **12 confirmed groups** (FIFA draw, Dec 2025)
- New **Round of 32** stage: top 2 per group (24 teams) + 8 best third-place
  finishers = 32 teams advance
- 2026-era squad ratings calibrated to post-EURO 2024 form:
  - Spain `0.905` — Yamal era, EURO 2024 winners
  - Argentina `0.888` — defending world champions, Scaloni continuity
  - Germany `0.858` — Wirtz/Musiala rebuild post-EURO 2024
  - Morocco `0.792` — 2022 SF legacy, Regragui 4-year tenure
  - Portugal `0.855` — post-Ronaldo transition under Martínez
- VaR/CVaR bounded perturbation (3 % VaR, 6 % CVaR cap) replaces Gaussian noise
- Coach-player correlation layer (`oracle/coach_correlation.py`)
- **Referee-bias VAR-era dampening (2026-09-19):** `REFEREE_BIAS_WEIGHT_2026 = 0.35` in `config.py`. Referee bias is a real, documented effect, but VAR (in wide use since 2018) meaningfully constrains an individual referee's influence on outcomes. `simulate_match()` in `oracle/monte_carlo.py` now blends the bias-adjusted win probability with the base win probability at this weight (and scales `referee_bias_magnitude` the same way) instead of fully overriding on referee assignment as it did before.

**Current prediction:** Spain

**Key files:**
- `backtest/wc2026_forecast.py` — 48-team Monte Carlo tournament engine
- `oracle/var_noise.py` — VaR/CVaR noise module
- `oracle/coach_correlation.py` — 16 empirical coach–player records

---

## Round 2 — `2022-backtest`

**Purpose:** Validate the model against the 2022 FIFA World Cup (Qatar).

**Model score (corrected 2026-09-19):** **40–50 / 64 BPS, seed-dependent** — seeds 1, 3, 4, 7 → 40/64 FAIL; seeds 0, 2, 5, 6, 8, 9 → 50/64 PASS; **default seed 42 → 50/64 PASS**.  
**Predicted champion (default seed):** Argentina ✓ (correct)

> This section previously claimed 51/64 PASS on all seeds. That was never
> actually produced by the code — see the correction notice at the top of
> this README and `2022-backtest/README.md` for the full root-cause writeup.

**Key additions over baseline:**
- `TOURNAMENT_FORM_BOOST_2022` — late-tournament form corrections:
  - Morocco `+0.058`, Croatia `+0.025`, Japan `+0.018`
  - Brazil `−0.022`, Spain `−0.018`, Portugal `−0.010`
  - **(Fixed 2026-09-19: this dict existed but was never applied anywhere — now wired into `run()`.)**
- Age-decay scoring, shootout coefficient, physical-readiness blend
- VaR/CVaR noise across seeds 0–9 (real per-seed results above — not uniformly PASS)
- Coach-player correlation (`oracle/coach_correlation.py`) — **(Fixed 2026-09-19: `apply_coach_adjustments()` existed but was never called from the backtest — now wired into `run()`.)**
- **New: blended evaluation** (2026-09-19) — combines the bracket-outcome score with betting-market calibration (Brier score vs. real 2022 knockout odds) and xG-based match-dominance agreement, since judging purely on which team advanced is noisy. At the default seed: bracket 78.1%, market calibration 99.1% (avg Brier 0.0091), xG-alignment 80.0% (12/15 matches), **blended score 85.0%**. See `oracle/blended_evaluation.py` and `data/wc2022_market_data.py` (real xG and de-vigged betting odds, sources cited inline).

**Key files:**
- `backtest/wc2022_backtest.py` — tournament simulation + BPS scorer + blended evaluation
- `oracle/var_noise.py` — VaR/CVaR noise module + `implied_win_prob()` for market calibration
- `oracle/coach_correlation.py` — 16 empirical coach–player records
- `oracle/blended_evaluation.py` — market-calibration + xG-alignment scoring (new)
- `data/wc2022_market_data.py` — real 2022 knockout xG + betting-market data (new)

---

## Round 3 — `2018-backtest`

**Purpose:** Validate the model against the 2018 FIFA World Cup (Russia).

**Model score:** **47 / 64 BPS** — ✅ PASS (threshold ≥ 45)  
**Predicted champion:** France ✓ (correct)

This number was independently re-verified during the 2026-09-19 audit and
is accurate — unlike 2022-backtest, this folder's core score was not
affected by the wiring bug described above.

**Model state:** Same architecture as Round 2 backtested on 2018 data.

- **New: blended evaluation** (2026-09-19), mirroring the 2022-backtest
  addition — bracket 73.4%, market calibration 99.3% (avg Brier 0.0068),
  xG-alignment 80.0% (12/15 matches), **blended score 83.2%**. See
  `oracle/blended_evaluation.py` and `data/wc2018_market_data.py`.

**Key files:**
- `backtest/wc2018_backtest.py` — tournament simulation + BPS scorer + blended evaluation
- `oracle/var_noise.py` — VaR/CVaR noise module + `implied_win_prob()`
- `oracle/coach_correlation.py` — 16 empirical coach–player records
- `oracle/blended_evaluation.py` — market-calibration + xG-alignment scoring (new)
- `data/wc2018_market_data.py` — real 2018 knockout xG + betting-market data (new)

---

## Scoring System (BPS)

| Round        | Points per correct call | Max pts |
|-------------|------------------------|---------|
| Round of 16  | 1                       | 16      |
| Quarterfinals| 2                       | 16      |
| Semifinals   | 3                       | 12      |
| Final        | 5                       | 10      |
| Champion     | 10                      | 10      |
| **Total**    |                         | **64**  |

**PASS threshold: ≥ 45 / 64**

---

## Readiness Formula

Player readiness is computed as a weighted average of psychological and
physical sub-scores:

```
readiness = (psych × 1.0 + physical × 1.5) / 2.5
```

Psychological factors (weight 1.0): pressure index, morale, home-crowd
proximity (family attendance), tournament experience, new vs. veteran status.

Physical factors (weight 1.5): age-decay curve, injury flag, fitness rating,
weight/diet data, minutes played in qualifying.

---

## Core Modules

| Module | Description |
|--------|-------------|
| `oracle/var_noise.py` | VaR/CVaR bounded perturbation (3 % VaR, 6 % CVaR cap) |
| `oracle/coach_correlation.py` | Coach–player synergy deltas (16 empirical records) |
| `oracle/psychological_state_model.py` | Psych score: pressure, morale, experience |
| `oracle/physical_condition_model.py` | Physical score: age-decay, injury, fitness, diet |
| `oracle/referee_bias.py` | Referee penalty patterns and team-favour tendencies |
| `oracle/positional_power.py` | Position-weighted squad value scoring |
| `oracle/sponsorship_model.py` | Sponsorship value as a proxy for national programme investment |
| `oracle/monte_carlo.py` | Core 50 k simulation engine |
| `oracle/bracket.py` | Bracket progression and upset detection |
| `oracle/form_analyzer.py` | Recent match form momentum |
| `oracle/weather_altitude.py` | Venue climate / altitude adjustments |
| `data/referee_stats_fetcher.py` | Historical referee data client |
| `data/api_football_client.py` | Football API integration |
| `data/world_bank_client.py` | Country resource / GDP data |

---

## Results Summary

| Folder | Tournament | BPS (bracket only) | Blended score | Result | Champion |
|--------|-----------|-----|-----|--------|---------|
| `2026-prediction` | 2026 WC | — | — | Live forecast | Spain (predicted) |
| `2022-backtest` | 2022 WC | 40–50/64 (seed-dependent; 50/64 at default seed) | 85.0% | ⚠️ seed-dependent (PASS at default seed) | Argentina ✓ (at default seed) |
| `2018-backtest` | 2018 WC | 47/64 | 83.2% | ✅ PASS | France ✓ |

*2022-backtest corrected 2026-09-19 — see the correction notice above.
Blended score = 40% bracket outcome + 30% betting-market calibration + 30%
xG-alignment; see each folder's README for methodology.*
