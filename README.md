# world-cup-oracle-trials

**Multi-factor FIFA World Cup prediction engine — full trial & error history.**

This repository documents the complete iterative development of a World Cup outcome
prediction model across three trials. Each trial is preserved exactly as it ran —
including all failures — to show the full engineering process: hypothesis, test,
diagnose, iterate.

---

## Repository Structure

```
world-cup-oracle-trials/
├── trial-1/    # First model — v1 weights, 2022 WC backtest → 40/64 FAIL
├── trial-2/    # Second model — position-weighted psych, physical condition model,
│               # 2022 WC backtest → 40/64 FAIL, 2018 WC backtest → 25/64 FAIL
└── trial-3/    # Third model — age-decay curves, shootout coefficient, full
                # physical integration (in progress)
```

---

## Trial Results

| Trial | Key Changes | Tournament | BPS | /64 | Result |
|-------|-------------|------------|-----|-----|--------|
| Trial 1 | Baseline model: squad value, positional power, country resources, historical data, commercial signal, referee bias, psychological state (life events, family attendance, rookie/veteran) | 2022 WC | 40 | 64 | ✗ FAIL |
| Trial 2 | + Position-weighted psych sensitivity (CM=1.30, AM=1.20, FW=1.10, CB=1.00, FB=0.85, GK=0.80)<br>+ Physical condition model (BMI, body fat %, diet discipline, age-peak curve, injury load)<br>+ 2018 cross-tournament validation | 2022 WC | 40 | 64 | ✗ FAIL |
| Trial 2 | Same model, cross-tournament test | 2018 WC | 25 | 64 | ✗ FAIL |
| Trial 3 | + Age-decay on squad value<br>+ Shootout-specialist coefficient<br>+ Full physical condition integration into simulation loop | TBD | — | 64 | 🔄 In Progress |

**Pass threshold: 45/64**

---

## Signal Architecture

All three trials share the same core signal dimensions. Each trial adjusts weights
and adds new sub-signals based on what the previous backtest revealed.

### Dimension 1 — Squad Value & Positional Power
Raw transfer market value (Transfermarkt) weighted by position importance.
Positional power weight increased from 0.25 (Trial 1) to 0.30 (Trial 2) after
Japan's 5-4-1 low-block dismantled Germany and Spain in 2022.

### Dimension 2 — Country Resources
World Bank API: GDP per capita, population, football federation budget proxy.
Captures the infrastructure gap between football superpowers and emerging nations.

### Dimension 3 — Historical Performance
Tournament pedigree (World Cup finals appearances, win rate, recent momentum).
Weight: 0.20 → 0.22 across trials.

### Dimension 4 — Commercial Signal
FIFA ranking points, sponsorship index, broadcast reach. Proxy for institutional
investment and global scouting network depth.

### Dimension 5 — Referee Bias
Named referee statistics per match: yellow cards/game, penalty award rate,
historical team favouritism. Real data from 2018/2022 World Cups and
UEFA Champions League:

| Referee | Penalty Rate | YC/Game | Notable |
|---------|-------------|---------|---------|
| Szymon Marciniak | 0.44 | 4.07 | 2022 WC Final, 2023 UCL Final |
| Clément Turpin | 0.53 | 3.25 | Record 31 pens in 58 UCL matches |
| Daniele Orsato | 0.26 | 4.69 | Modrić: "one of the worst" (2022 WC SF) |
| Felix Zwayer | 0.31 | 4.12 | Match-fixing suspension 2005 |

### Dimension 6 — Psychological State
Point-based add/deduct system per player:

| Event | Delta |
|-------|-------|
| Recent bereavement (≤8 weeks) | −15 |
| New parent | −5 |
| Family illness | −8 |
| Divorce/separation | −7 |
| Public controversy | −6 |
| Fallout with manager | −8 |
| Dressing room conflict | −5 |
| Wants transfer out | −6 |
| History of referee confrontation | up to −10 |
| Legacy/farewell tournament | +10 |
| Captain responsibility | up to +8 |
| Recent trophy momentum | +7 |
| Revenge motivation | +8 |
| Pressure performance = "rises" | +6 |

**Readiness formula:**
```
readiness = (psych × 1.0 + physical × 1.5) / 2.5
psych_multiplier = 0.7 + 0.3 × (readiness / 100)
adjusted_score = base_composite_score × psych_multiplier
```

**Position-sensitivity (Trial 2+):**
```python
PSYCH_SENSITIVITY = {
    "CM":  1.30,   # box-to-box midfielders most affected by mental state
    "AM":  1.20,
    "FW":  1.10,
    "CB":  1.00,
    "FB":  0.85,
    "GK":  0.80,   # goalkeepers most mentally compartmentalised
}
```

### Dimension 7 — Physical Condition (Trial 2+)
Per-player physical scoring using real anthropometric and nutrition data:

- **BMI deviation** from position-optimal window (FIFA 2018 squad data)
- **Body fat %**: Ronaldo 7% (Chosun Daily Dec 2025) → +4; <8% = exceptional
- **Diet discipline**: Haaland/Ronaldo "very strict" = +8; Mbappe/Messi "strict" = +5
- **Age-peak curve**: FW peaks 24–27, GK holds to 34 — per-position decline penalty
- **Injury load**: ACL/chronic flag, weeks missed, minutes last 12 months
- **Regional carb-deficit**: N. Africa, SE Asia squads −2 (Frontiers in Sports 2024)

### Dimension 8 — Family Attendance & Experience
- Family can attend (2026 USA/Canada/Mexico): asymmetric access by nationality
- Confirmed family present + positive relationship: up to +7
- Estranged / family cannot travel: deduction applied
- Rookie vs. veteran tournament experience: +3 (experience) / −2 (first tournament)

---

## Why Each Trial Failed

### Trial 1 → 40/64
- Over-weighted squad market value (0.30) — favoured expensive squads over
  tactically disciplined ones
- Under-weighted positional power (0.25) — missed Japan/Morocco's defensive blocks
- No age-decay: Germany's aging 2018 squad still carried 2014 prestige scores
- No shootout signal: couldn't model Croatia's 3-pen run in 2018

### Trial 2 → 40/64 (2022), 25/64 (2018)
- Position-weighted psych improved individual scoring but not wired into
  match simulation loop for backtests
- Physical condition model built but not integrated into simulation probabilities
- 2018 test revealed structural cross-tournament weaknesses:
  - Germany still rated too high (no age-decay on squad value)
  - Croatia's 2018 penalty path had ~3.7% championship probability (actual: finalist)
- Both backtests failed — motivating a deeper architectural fix in Trial 3

### Trial 3 (planned)
Addresses both root causes directly — see `trial-3/PLACEHOLDER.md`

---

## Engineering Skills Demonstrated

| Skill | Where |
|-------|-------|
| Monte Carlo simulation | `oracle/monte_carlo.py` — 50,000 bracket runs per backtest |
| ETL pipeline | `data/` — World Bank API, football API, referee stats fetcher |
| Regression testing | `tests/regression/` — weight change impact validation |
| Backtesting framework | `backtest/wc2022_backtest.py`, `backtest/wc2018_backtest.py` |
| Vectorised scoring | `oracle/team_strength.py` — numpy positional arrays |
| Event-driven architecture | `oracle/psychological_state_model.py` — point-delta event system |
| Hyperparameter tuning | `oracle/hyperparameter_tuner.py` — grid search over weight space |
| Schema validation | `oracle/schemas.py` — dataclass-based input validation |
| Cross-tournament validation | Two independent holdout sets (2018, 2022) |
| Physical data integration | `oracle/physical_condition_model.py` — real anthropometry + nutrition |

---

## Related Repositories

- [`world-cup-oracle`](https://github.com/fatehaszaman/world-cup-oracle) — Trial 1 standalone
- [`world-cup-oracle-v2`](https://github.com/fatehaszaman/world-cup-oracle-v2) — Trial 2 standalone
- [`transfer-market-signals`](https://github.com/fatehaszaman/transfer-market-signals) — Transfer intelligence engine
- [`draft-intelligence`](https://github.com/fatehaszaman/draft-intelligence) — NFL Draft predictor
- [`sports-sponsorship-valuator`](https://github.com/fatehaszaman/sports-sponsorship-valuator) — Sponsorship ROI engine
