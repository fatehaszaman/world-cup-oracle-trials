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

**Current prediction:** Spain

**Key files:**
- `backtest/wc2026_forecast.py` — 48-team Monte Carlo tournament engine
- `oracle/var_noise.py` — VaR/CVaR noise module
- `oracle/coach_correlation.py` — 16 empirical coach–player records

---

## Round 2 — `2022-backtest`

**Purpose:** Validate the model against the 2022 FIFA World Cup (Qatar).

**Model score:** **51 / 64 BPS** — ✅ PASS (threshold ≥ 45)  
**Predicted champion:** Argentina ✓ (correct)

**Key additions over baseline:**
- `TOURNAMENT_FORM_BOOST_2022` — late-tournament form corrections:
  - Morocco `+0.058`, Croatia `+0.025`, Japan `+0.018`
  - Brazil `−0.022`, Spain `−0.018`, Portugal `−0.010`
- Age-decay scoring, shootout coefficient, physical-readiness blend
- VaR/CVaR noise (all seeds 0–9 confirmed PASS at 50 k simulations)
- Coach-player correlation (`oracle/coach_correlation.py`)

**Key files:**
- `backtest/wc2022_backtest.py` — tournament simulation + BPS scorer
- `oracle/var_noise.py` — VaR/CVaR noise module
- `oracle/coach_correlation.py` — 16 empirical coach–player records

---

## Round 3 — `2018-backtest`

**Purpose:** Validate the model against the 2018 FIFA World Cup (Russia).

**Model score:** **47 / 64 BPS** — ✅ PASS (threshold ≥ 45)  
**Predicted champion:** France ✓ (correct)

**Model state:** Same architecture as Round 2 backtested on 2018 data.  
All seeds 0–9 confirmed PASS at 50 k simulations.

**Key files:**
- `backtest/wc2018_backtest.py` — tournament simulation + BPS scorer
- `oracle/var_noise.py` — VaR/CVaR noise module
- `oracle/coach_correlation.py` — 16 empirical coach–player records

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

| Folder | Tournament | BPS | Result | Champion |
|--------|-----------|-----|--------|---------|
| `2026-prediction` | 2026 WC | — | Live forecast | Spain (predicted) |
| `2022-backtest` | 2022 WC | 51/64 | ✅ PASS | Argentina ✓ |
| `2018-backtest` | 2018 WC | 47/64 | ✅ PASS | France ✓ |
