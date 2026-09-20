# Algorithm guide

This guide covers selected shared mechanics, not every experiment or forecast.
The three folders are maintained variants; they are not immutable historical
artifacts, and their existence does not establish predictive validation.

## Where to read

- [2018 generic simulator](../2018-backtest/oracle/monte_carlo.py)
- [2022 generic simulator](../2022-backtest/oracle/monte_carlo.py)
- [2026 generic simulator](../2026-prediction/oracle/monte_carlo.py)

The cards below apply to `simulate_match` and `run_tournament` in these files.
They do not describe the separate `WC2026Forecast` format-specific engine.

## Match sampling

```text
# Match Monte Carlo / Poisson Sampling
# Input: scores for two teams and P simulations
# Output: win/draw probabilities, mean goals, referee-adjustment metadata
# Time: expected O(P), excluding optional referee work
# Memory: O(P) temporary arrays; O(1) result

LOOK UP scores with the 0.50 fallback
CLIP strength difference and calculate floored goal rates
DRAW two P-element Poisson goal vectors
COUNT each win outcome and draws; normalize by P
OPTIONALLY adjust decisive probabilities while preserving draw mass
RETURN rounded summary
```

This model assumes bounded rate parameters and fixed-width operations.
P must be positive. Goal arrays and comparison masks are allocated;
vectorization does not remove their memory costs.

## Tournament aggregation

```text
# Tournament Summary / Store Then Average
# Input: R runs, T teams, K=6 recorded stages
# Output: team probabilities sorted by champion probability
# Time: O(R*(C_run + T*K) + T*log T)
# Memory: O(R*T*K + T*K) plus simulator and one-run workspace
# C_run = cost of the selected implementation's _single_tournament_run

SORT unique teams
ALLOCATE reach[R, T, K] using float32
FOR each seeded run:
    outcome = SIMULATE tournament
    COPY team-stage indicators into that run's slice
AVERAGE over runs
FORMAT team rows; SORT descending by champion probability
RETURN table
```

The reach tensor uses `4*R*T*K` bytes. Configured-team Cholesky state adds
O(T_config²) memory, and its setup factorization costs O(T_config³).
`memory_usage_mb()` reports only the Cholesky factor. It is not a peak-memory
measurement, and the full run loop is sequential.

## Review boundaries

Do not use these shared cards as evidence that all trial folders use identical
format rules, source data, or evaluation paths. Follow each folder's README and
backtest entry point. A generic 24-team-with-byes knockout and the separate
48-to-32 scenario are different implementations. Preserve failed/revised
experiments and distinguish sampling error from model error.
