"""
backtest/wc2026_forecast.py — 2026 FIFA World Cup Tournament Forecast

This is a STATIC SCENARIO, not a live forecast or an outcome validation.
The inputs and narrative assumptions below have not been independently
refreshed. Do not present this file as a current verified tournament feed.
See the repository-root AUDIT.md for limitations.

Tournament format change: 48 teams → 12 groups of 4 → top 2 per group + 8 best
third-place teams advance → Round of 32 (new stage) → R16 → QF → SF → Final.

The prior coach/retirement narratives and exact-ranking claims were not
verified and have been withdrawn. The numeric scenario inputs are retained
for reproducibility, not represented as empirically sourced current ratings.

Match format notes:
  - 48 teams, 12 groups (Groups A–L)
  - Top 2 from each group (24 teams) + 8 best third-place = 32 teams advance
  - Round of 32 → R16 → QF → SF → Final (max 8 games per team)
  - This sim uses the Round of 32 stage then standard knockout from R16 onward
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from oracle.var_noise import simulate_match_var, simulate_group_var, VAR_BOUND, VAR_CONFIDENCE, _SIGMA

# ---------------------------------------------------------------------------
# Static group assumptions. Official status has not been independently verified.
# ---------------------------------------------------------------------------
WC2026_GROUPS: dict[str, list[str]] = {
    "A": ["Mexico",        "South Africa",  "South Korea",  "Czech Republic"],
    "B": ["Canada",        "Bosnia",        "Qatar",        "Switzerland"],
    "C": ["Brazil",        "Morocco",       "Haiti",        "Scotland"],
    "D": ["United States", "Paraguay",      "Australia",    "Turkey"],
    "E": ["Germany",       "Curacao",       "Ivory Coast",  "Ecuador"],
    "F": ["Netherlands",   "Japan",         "Sweden",       "Tunisia"],
    "G": ["Belgium",       "Egypt",         "Iran",         "New Zealand"],
    "H": ["Spain",         "Cape Verde",    "Saudi Arabia", "Uruguay"],
    "I": ["France",        "Senegal",       "Iraq",         "Norway"],
    "J": ["Argentina",     "Algeria",       "Austria",      "Jordan"],
    "K": ["Portugal",      "DR Congo",      "Uzbekistan",   "Colombia"],
    "L": ["England",       "Croatia",       "Ghana",        "Panama"],
}

ALL_2026_TEAMS: list[str] = [t for teams in WC2026_GROUPS.values() for t in teams]

# ---------------------------------------------------------------------------
# 2026-era composite squad scores (0–1 scale)
# ---------------------------------------------------------------------------
# Manually assigned scenario scores, not verified current rankings or valuations.
# Unsupported coach, retirement, and dated-form rationales were withdrawn.
# ---------------------------------------------------------------------------
_SQUAD_SCORES_2026: dict[str, float] = {

    "Spain":          0.905,
    "Argentina":      0.888,
    "France":         0.880,
    "England":        0.872,
    "Brazil":         0.868,
    "Portugal":       0.855,
    "Netherlands":    0.848,
    "Germany":        0.858,

    "Belgium":        0.800,
    "Morocco":        0.792,
    "Croatia":        0.762,
    "Colombia":       0.778,
    "Uruguay":        0.748,
    "Switzerland":    0.738,
    "Japan":          0.730,
    "Senegal":        0.722,
    "Iran":           0.690,
    "South Korea":    0.710,
    "Ecuador":        0.695,
    "Austria":        0.688,
    "Australia":      0.672,
    "Mexico":         0.668,
    "Norway":         0.665,
    "Canada":         0.658,
    "Panama":         0.620,
    "Egypt":          0.618,
    "Algeria":        0.615,
    "Scotland":       0.608,
    "Paraguay":       0.605,
    "Tunisia":        0.598,
    "Ivory Coast":    0.595,
    "Sweden":         0.590,
    "Turkey":         0.585,
    "United States":  0.660,
    "Saudi Arabia":   0.570,
    "South Africa":   0.558,
    "Uzbekistan":     0.520,
    "Qatar":          0.500,
    "Cape Verde":     0.512,
    "DR Congo":       0.518,
    "Ghana":          0.510,
    "Jordan":         0.490,
    "Haiti":          0.478,
    "New Zealand":    0.462,
    "Curacao":        0.445,
    "Bosnia":         0.552,
    "Czech Republic": 0.568,
    "Iraq":           0.498,
}

# ---------------------------------------------------------------------------
# Shootout ratings — 2026 era
# ---------------------------------------------------------------------------
SHOOTOUT_RATINGS_2026: dict[str, float] = {
    "Argentina":    0.88,   # Emiliano Martínez; PK culture post-2022
    "Croatia":      0.86,   # Livaković; 2022 PK specialist
    "France":       0.72,
    "England":      0.60,   # historically weak; improving under Tuchel
    "Spain":        0.70,
    "Germany":      0.78,
    "Brazil":       0.68,
    "Portugal":     0.72,
    "Morocco":      0.75,   # Bounou; proven 2022 specialist
    "Netherlands":  0.68,
    "Switzerland":  0.67,
    "Japan":        0.62,
    "Colombia":     0.63,
    "Uruguay":      0.65,
    "Norway":       0.60,
    "Mexico":       0.55,
    "United States":0.55,
    "Senegal":      0.58,
    "South Korea":  0.55,
    "Belgium":      0.64,
    "Denmark":      0.61,
    "Egypt":        0.52,
}
SHOOTOUT_WEIGHT_2026: float = 0.18

# ---------------------------------------------------------------------------
# Simulation helpers
# ---------------------------------------------------------------------------

def _simulate_match(
    team_a: str,
    team_b: str,
    scores: dict[str, float],
    rng: np.random.Generator,
    knockout: bool = False,
) -> str:
    """Single match via VaR/CVaR bounded noise. Always returns a team name."""
    return simulate_match_var(
        team_a, team_b, scores, rng,
        shootout_ratings=SHOOTOUT_RATINGS_2026,
        shootout_weight=SHOOTOUT_WEIGHT_2026,
        knockout=knockout,
    )


def _simulate_group(
    group_teams: list[str],
    scores: dict[str, float],
    rng: np.random.Generator,
) -> list[str]:
    """Simulate a 4-team group; return all 4 sorted by points/GD."""
    points: dict[str, int]   = {t: 0 for t in group_teams}
    gd:     dict[str, float] = {t: 0.0 for t in group_teams}

    for i, ta in enumerate(group_teams):
        for tb in group_teams[i + 1:]:
            result = simulate_match_var(ta, tb, scores, rng, knockout=False)
            if result == ta:
                points[ta] += 3; gd[ta] += rng.uniform(0.5, 2.0); gd[tb] -= rng.uniform(0.5, 1.5)
            elif result == tb:
                points[tb] += 3; gd[tb] += rng.uniform(0.5, 2.0); gd[ta] -= rng.uniform(0.5, 1.5)
            else:
                points[ta] += 1; points[tb] += 1

    # Return all 4 sorted — caller selects top 2 (and tracks 3rd for best-of-8)
    return sorted(group_teams, key=lambda t: (points[t], gd[t]), reverse=True)


# ---------------------------------------------------------------------------
# Main forecast class
# ---------------------------------------------------------------------------

@dataclass
class WC2026Forecast:
    """
    2026 FIFA World Cup forward-looking tournament simulation.

    Simulates the full 48-team, 12-group tournament using:
      - Static group assumptions (not independently verified)
      - Manually assigned scenario strengths
      - VaR/CVaR bounded match noise (3% VaR, σ≈0.016)
      - Shootout specialist ratings
      - Round of 32 stage (new in 2026 format)

    Outputs scenario probabilities, not a verified live prediction.
    This engine has no referee-assignment input.
    """

    n_simulations: int = 50_000
    seed: int = 2026
    _results: Optional[dict] = field(default=None, repr=False)

    def run(self) -> dict:
        rng    = np.random.default_rng(self.seed)
        scores = _SQUAD_SCORES_2026.copy()
        n      = self.n_simulations

        # Count trackers
        r32_counts:     dict[str, int] = {t: 0 for t in ALL_2026_TEAMS}
        r16_counts:     dict[str, int] = {t: 0 for t in ALL_2026_TEAMS}
        qf_counts:      dict[str, int] = {t: 0 for t in ALL_2026_TEAMS}
        sf_counts:      dict[str, int] = {t: 0 for t in ALL_2026_TEAMS}
        fin_counts:     dict[str, int] = {t: 0 for t in ALL_2026_TEAMS}
        champion_counts:dict[str, int] = {t: 0 for t in ALL_2026_TEAMS}

        for _ in range(n):
            # ── Group stage ────────────────────────────────────────────────
            group_standings: dict[str, list[str]] = {}  # group → [1st, 2nd, 3rd, 4th]
            third_place_teams: list[tuple[float, str]] = []  # (pts_score, team)

            for grp, teams in WC2026_GROUPS.items():
                standing = _simulate_group(teams, scores, rng)
                group_standings[grp] = standing
                # Track 3rd place for best-of-8 selection
                # Approximate points via position; actual sim tracks in-group ranking
                third_place_teams.append((0.0, standing[2]))  # placeholder score

            # Top 2 per group → 24 automatic qualifiers
            r32_auto: list[str] = []
            for grp in "ABCDEFGHIJKL":
                r32_auto.append(group_standings[grp][0])  # group winner
                r32_auto.append(group_standings[grp][1])  # runner-up

            # Best 8 third-place teams → simplified: pick 8 random from 12
            # (In reality based on points, but without tracking exact points
            # in this sim we use the model's strength as a proxy)
            thirds = [group_standings[grp][2] for grp in "ABCDEFGHIJKL"]
            # Score-rank the 12 third-place teams, take top 8
            thirds_ranked = sorted(thirds, key=lambda t: scores.get(t, 0.5), reverse=True)[:8]

            r32_teams = r32_auto + thirds_ranked  # 32 teams total

            for t in r32_teams:
                r32_counts[t] = r32_counts.get(t, 0) + 1

            # ── Round of 32 (16 matches) ───────────────────────────────────
            # Bracket: group winners vs third-place; runners-up vs third-place
            # Simplified sequential pairing for simulation
            r32_bracket = list(r32_teams)
            rng.shuffle(r32_bracket)

            r16_teams: list[str] = []
            for i in range(0, 32, 2):
                if i + 1 < len(r32_bracket):
                    w = _simulate_match(r32_bracket[i], r32_bracket[i+1], scores, rng, knockout=True)
                    r16_teams.append(w)

            for t in r16_teams:
                r16_counts[t] = r16_counts.get(t, 0) + 1

            # ── R16 → QF ───────────────────────────────────────────────────
            qf_teams: list[str] = []
            for i in range(0, len(r16_teams), 2):
                if i + 1 < len(r16_teams):
                    w = _simulate_match(r16_teams[i], r16_teams[i+1], scores, rng, knockout=True)
                    qf_teams.append(w)

            for t in qf_teams:
                qf_counts[t] = qf_counts.get(t, 0) + 1

            # ── QF → SF ────────────────────────────────────────────────────
            sf_teams: list[str] = []
            for i in range(0, len(qf_teams), 2):
                if i + 1 < len(qf_teams):
                    w = _simulate_match(qf_teams[i], qf_teams[i+1], scores, rng, knockout=True)
                    sf_teams.append(w)

            for t in sf_teams:
                sf_counts[t] = sf_counts.get(t, 0) + 1

            # ── SF → Final ─────────────────────────────────────────────────
            finalists: list[str] = []
            for i in range(0, len(sf_teams), 2):
                if i + 1 < len(sf_teams):
                    w = _simulate_match(sf_teams[i], sf_teams[i+1], scores, rng, knockout=True)
                    finalists.append(w)

            for t in finalists:
                fin_counts[t] = fin_counts.get(t, 0) + 1

            # ── Final ──────────────────────────────────────────────────────
            if len(finalists) >= 2:
                champ = _simulate_match(finalists[0], finalists[1], scores, rng, knockout=True)
                champion_counts[champ] = champion_counts.get(champ, 0) + 1

        self._results = {
            "r32_probs":      {t: r32_counts.get(t, 0) / n    for t in ALL_2026_TEAMS},
            "r16_probs":      {t: r16_counts.get(t, 0) / n    for t in ALL_2026_TEAMS},
            "qf_probs":       {t: qf_counts.get(t, 0) / n     for t in ALL_2026_TEAMS},
            "sf_probs":       {t: sf_counts.get(t, 0) / n     for t in ALL_2026_TEAMS},
            "finalist_probs": {t: fin_counts.get(t, 0) / n    for t in ALL_2026_TEAMS},
            "champion_probs": {t: champion_counts.get(t, 0)/n for t in ALL_2026_TEAMS},
        }
        return self._results

    def print_forecast(self) -> None:
        """Print a ranked championship probability table."""
        if self._results is None:
            self.run()

        r = self._results
        print("\n" + "=" * 70)
        print("  2026 FIFA World Cup — Tournament Forecast")
        print("  Model: VaR/CVaR noise; static, unverified scenario inputs")
        print(f"  Simulations: {self.n_simulations:,}  |  Seed: {self.seed}")
        print("=" * 70)
        print(f"\n  {'Team':<22} {'R32%':>5} {'R16%':>5} {'QF%':>5} {'SF%':>5} {'Final%':>6} {'Win%':>5}")
        print("  " + "-" * 58)

        top = sorted(r["champion_probs"], key=lambda t: r["champion_probs"][t], reverse=True)
        for i, team in enumerate(top[:20], 1):
            r32  = r["r32_probs"][team]   * 100
            r16  = r["r16_probs"][team]   * 100
            qf   = r["qf_probs"][team]    * 100
            sf   = r["sf_probs"][team]    * 100
            fin  = r["finalist_probs"][team] * 100
            win  = r["champion_probs"][team] * 100
            bar  = "█" * int(win / 1.5)
            print(f"  {i:2}. {team:<19} {r32:5.1f} {r16:5.1f} {qf:5.1f} {sf:5.1f} {fin:6.1f} {win:5.1f}%  {bar}")

        pred_winner = max(r["champion_probs"], key=lambda t: r["champion_probs"][t])
        print(f"\n  ► Predicted champion: {pred_winner}")
        print("  Static scenario only; not a live forecast or validated accuracy.")
        print("=" * 70 + "\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    fc = WC2026Forecast(n_simulations=50_000, seed=2026)
    fc.print_forecast()
