# Trial 3 — In Progress

Root cause fixes from Trial 2 failures:

1. **Age-decay curves** — Germany's 2014 squad carried inflated squad-value scores
   despite key retirements. Trial 3 applies per-player age-decay to historical
   squad value so past champions don't benefit from stale prestige.

2. **Shootout-specialist coefficient** — Croatia won 3 consecutive penalty shootouts
   en route to the 2018 final (Denmark R16, Russia QF, England SF). The simulation
   currently has no shootout-clutch signal. Trial 3 adds a dedicated coefficient
   drawn from national team penalty record (attempts, conversion rate, goalkeeper
   save rate in shootouts).

3. **Physical condition model integration** — `oracle/physical_condition_model.py`
   was added in Trial 2 but not yet wired into the backtest simulation loop.
   Trial 3 fully integrates weight/BMI/diet/age-curve scoring into match
   probability calculations.

Coming soon.
