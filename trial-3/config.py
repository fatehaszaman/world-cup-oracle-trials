"""
config.py — World Cup Oracle v3 configuration.

Trial 3 root-cause fixes after Trial 2 failed both 2022 (40/64) and 2018 (25/64):

  Root cause 1 — Age-decay on squad value
    Germany in 2018 had a composite score of 0.87 (defending champions, high
    Transfermarkt values). But Lahm, Schweinsteiger had retired; Müller/Boateng
    were 28-29 and past peak for their positions. The model had no mechanism to
    penalise an aging squad. Added: AGE_DECAY_FACTOR per position, applied to
    squad composite to produce an age-adjusted base score.

  Root cause 2 — Shootout-specialist coefficient
    Croatia 2018: won 3 consecutive penalty shootouts (vs Denmark R16, Russia QF,
    England SF) to reach the final. The model gave Croatia only 3.7% championship
    probability. Without a shootout signal, any team with an elite penalty
    goalkeeper and disciplined takers gets systematically undervalued in knockout
    sims. Added: SHOOTOUT_RATING per team (0-1), applied as a tiebreaker boost
    in knockout draw simulations.

  Root cause 3 — Physical model fully wired in
    oracle/physical_condition_model.py was added in Trial 2 but only ran as a
    standalone demo. Trial 3 applies physical adjustments directly to the base
    composite scores before simulation.

Weight changes vs Trial 2:
  squad_value      0.26 → 0.22  (further reduced — age-decay now part of this signal)
  positional_power 0.30 → 0.32  (tactical organisation most predictive signal)
  country_resources 0.13 → 0.12
  historical       0.22 → 0.24  (pedigree more reliable cross-tournament)
  commercial       0.09 → 0.10
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Composite strength score dimension weights (must sum to 1.0)
# ---------------------------------------------------------------------------
DIMENSION_WEIGHTS: dict[str, float] = {
    "squad_value":        0.22,
    "positional_power":   0.32,
    "country_resources":  0.12,
    "historical":         0.24,
    "commercial":         0.10,
}

assert abs(sum(DIMENSION_WEIGHTS.values()) - 1.0) < 1e-9

# ---------------------------------------------------------------------------
# Age-decay configuration (ROOT CAUSE FIX 1)
# ---------------------------------------------------------------------------
# Applied to squad composite score: score *= (1 - age_decay_penalty)
# Penalty computed from average squad age vs position peak age.
# Source: FIFA 2018 anthropometry data + positional peak literature.

# Position peak ages — above this age, player quality starts declining
POSITION_PEAK_AGE: dict[str, int] = {
    "GK":  33,
    "CB":  30,
    "FB":  28,
    "CM":  29,
    "AM":  28,
    "FW":  27,
    "DMF": 30,
    "WB":  28,
}

# Per year ABOVE peak age, deduct this fraction from positional contribution
AGE_DECAY_RATE: float = 0.025   # 2.5% per year past peak

# Per year BELOW development age (23), slight under-development penalty
AGE_DEVELOP_PENALTY: float = 0.015  # 1.5% per year below 23

# ---------------------------------------------------------------------------
# Shootout specialist ratings (ROOT CAUSE FIX 2)
# ---------------------------------------------------------------------------
# Penalty shootout conversion + goalkeeper save rate composite (0-1).
# Applied in knockout draw resolution: winner = rng < 0.5 + SHOOTOUT_BOOST
# where SHOOTOUT_BOOST = (rating_a - rating_b) * SHOOTOUT_WEIGHT
#
# Data sources:
#   - Croatia 2018: Subašić saved 3 pens across 3 shootouts (vs Denmark, Russia, England)
#   - Argentina historically: Romero era strong; Dibu Martínez 2021-2022 elite
#   - Germany: historically excellent (5/6 WC shootouts won before 2016 loss to Italy)
#   - England: historically poor (lost 6 of 7 WC/Euro shootouts before 2018)
#   - France: moderate (lost vs Switzerland Euro 2020 pens)
#   - Spain: very poor in shootouts (beat Russia 2018 by pens but lost others)
#
# Scale: 0.0 (historically terrible) → 1.0 (dominant shootout specialists)
SHOOTOUT_RATINGS: dict[str, float] = {
    # Elite shootout nations
    "Croatia":      0.88,   # Subašić 2018: 3 shootout wins; Livaković 2022: beat Brazil, Japan
    "Argentina":    0.85,   # Dibu Martínez 2022: EURO final + WC final pen saves
    "Germany":      0.80,   # 5/6 WC shootout wins historically (lost 2016 Euros)
    "Portugal":     0.72,
    "Brazil":       0.70,
    "Netherlands":  0.68,
    "Switzerland":  0.67,   # Beat France Euro 2020 pens; beat Serbia 2022 group
    "France":       0.62,   # Lost Switzerland Euro 2020; won vs Spain 2021
    "Uruguay":      0.65,
    "Belgium":      0.64,
    "England":      0.58,   # Improved post-2018: Southgate shootout training regime
    "Spain":        0.52,   # Historically weak (lost to Russia 2018 pens)
    "USA":          0.55,
    "Mexico":       0.53,
    "Colombia":     0.54,
    "Japan":        0.60,   # Beat Colombia 2014 pens; lost to Croatia 2022
    "Morocco":      0.63,   # Beat Spain 2022 pens
    "Denmark":      0.59,
    "Senegal":      0.56,
    "South Korea":  0.50,
    "Poland":       0.51,
    "Serbia":       0.52,
    "Iran":         0.45,
    "Saudi Arabia": 0.44,
    "Tunisia":      0.46,
    "Ghana":        0.48,
    "Cameroon":     0.47,
    "Ecuador":      0.49,
    "Australia":    0.50,
    "Wales":        0.50,
    "Canada":       0.51,
    "Qatar":        0.38,
    "Costa Rica":   0.48,
    "Iceland":      0.52,
    "Nigeria":      0.48,
    "Russia":       0.56,   # Beat Spain 2018 pens (home advantage + Akinfeev)
    "Sweden":       0.55,
    "Peru":         0.50,
    "Egypt":        0.48,
    "Panama":       0.38,
}

# How much shootout rating shifts the draw-resolution probability
SHOOTOUT_WEIGHT: float = 0.18   # ±18% max swing in extra-time/pens coin flip

# ---------------------------------------------------------------------------
# Physical condition integration weights (ROOT CAUSE FIX 3)
# ---------------------------------------------------------------------------
# Physical condition score (0-100) from physical_condition_model.py is
# normalised to 0-1 and blended into the base composite score.
PHYSICAL_BLEND_WEIGHT: float = 0.08   # 8% of final composite comes from physical model

# ---------------------------------------------------------------------------
# Position weights
# ---------------------------------------------------------------------------
POSITION_WEIGHTS: dict[str, float] = {
    "GK":  0.15,
    "CB":  0.20,
    "FB":  0.10,
    "CM":  0.25,
    "AM":  0.15,
    "FW":  0.15,
}
assert abs(sum(POSITION_WEIGHTS.values()) - 1.0) < 1e-9

# ---------------------------------------------------------------------------
# Historical performance scoring
# ---------------------------------------------------------------------------
HISTORICAL_POINTS: dict[str, float] = {
    "winner":           3.0,
    "runner_up":        2.0,
    "semi_finalist":    1.0,
    "quarter_finalist": 0.5,
    "round_of_16":      0.1,
    "group_stage":      0.0,
}
HISTORICAL_MAX_POINTS: float = 5 * HISTORICAL_POINTS["winner"]

# ---------------------------------------------------------------------------
# Country resources
# ---------------------------------------------------------------------------
RESOURCE_WEIGHTS: dict[str, float] = {
    "gdp_per_capita": 0.35,
    "population":     0.20,
    "fifa_budget":    0.30,
    "primary_sport":  0.15,
}
GDP_NORMALIZATION_CEILING: float = 80_000.0
POPULATION_LOG_MIN: float = 6.0
POPULATION_LOG_MAX: float = 9.1

# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------
MC_DEFAULT_RUNS: int = 50_000
MC_RANDOM_SEED: int = 42
POISSON_BASE_LAMBDA: float = 1.35
POISSON_STRENGTH_SCALE: float = 0.6
EXTRA_TIME_STRONGER_TEAM_BIAS: float = 0.55

# ---------------------------------------------------------------------------
# API / cache
# ---------------------------------------------------------------------------
RAPIDAPI_HOST: str = "api-football-v1.p.rapidapi.com"
API_FOOTBALL_BASE_URL: str = f"https://{RAPIDAPI_HOST}"
API_FOOTBALL_SEASON: int = 2024
WORLD_BANK_BASE_URL: str = "https://api.worldbank.org/v2"
WORLD_BANK_FORMAT: str = "json"
CACHE_TTL_SECONDS: int = 86_400
HTTP_MAX_RETRIES: int = 4
HTTP_BACKOFF_BASE: float = 1.5
SQUAD_VALUE_CEILING: float = 1_300.0
SHIRT_DEAL_CEILING_EUR_M: float = 65.0
KIT_DEAL_CEILING_EUR_M: float = 100.0
FED_REVENUE_CEILING_EUR_M: float = 250.0
SOCIAL_FOLLOWERS_CEILING_M: float = 150.0
FANBASE_INDEX_CEILING: float = 10.0

# ---------------------------------------------------------------------------
# Psychological readiness
# ---------------------------------------------------------------------------
PSYCH_WEIGHT:    float = 1.0
PHYSICAL_WEIGHT: float = 1.5
READINESS_TOTAL_WEIGHT: float = PSYCH_WEIGHT + PHYSICAL_WEIGHT
PSYCH_MC_BASE:  float = 0.70
PSYCH_MC_SCALE: float = 0.30
PSYCH_BASELINE:            float = 100.0
PSYCH_MIN_SCORE:           float = 20.0
PSYCH_MAX_SCORE:           float = 120.0

PSYCH_SENSITIVITY: dict[str, float] = {
    "GK":  0.80,
    "CB":  1.00,
    "FB":  0.85,
    "CM":  1.30,
    "AM":  1.20,
    "FW":  1.10,
}

TABLE_WIDTH: int = 88
PROBABILITY_DECIMAL_PLACES: int = 1
