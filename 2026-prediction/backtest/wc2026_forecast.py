"""
backtest/wc2026_forecast.py — 2026 FIFA World Cup Tournament Forecast

This is a FORWARD-LOOKING prediction, not a backtest. There is no known winner
to validate against — this is the model's live forecast for the 2026 tournament
hosted across USA, Canada, and Mexico (June–July 2026).

Tournament format change: 48 teams → 12 groups of 4 → top 2 per group + 8 best
third-place teams advance → Round of 32 (new stage) → R16 → QF → SF → Final.

Groups confirmed: FIFA draw held December 5, 2025 at the Kennedy Center, DC.
Sources: FIFA.com draw results, NBC Sports, ESPN, Wikipedia

2026 WC Key storylines feeding model signals:
  Argentina  — defending champions; Messi retirement after 2026 (announced);
               post-2022 squad integration ongoing; Scaloni continuity
  France     — Mbappé-led peak generation; Deschamps stepped down Nov 2024;
               new coach Luis Enrique (from PSG) brings tactical shift
  England    — Bellingham/Saka/Foden prime window; new manager after Southgate
               resigned post-Euro 2024; Thomas Tuchel appointed Jan 2025
  Spain      — EURO 2024 winners; Yamal/Pedri/Morata generation at full peak;
               strong squad continuity
  Germany    — EURO 2024 hosts (SF exit); Nagelsmann-led rebuild with younger
               squad (Wirtz/Musiala at prime); home territory advantage (CONCACAF
               host USA adjacent)
  Brazil     — New manager Dorival Júnior; Vinicius/Rodrygo/Endrick core;
               redemption after 2022 QF exit
  Morocco    — Regragui continuity; Hakimi/Amrabat leadership; 2022 SF legacy
               motivates record-attempt
  Portugal   — Post-Ronaldo era under Roberto Martínez; Ramos/Félix/Conceição
               new generation; Ronaldo retired from international after 2026 draw

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
# 2026 WC Groups — confirmed by FIFA draw, December 5 2025
# Source: FIFA.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/final-draw-results
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
# Sources:
#   Squad market values: Transfermarkt Jan 2026 national team valuations
#   FIFA rankings: Dec 2025 official rankings (draw seedings)
#   Form signals: EURO 2024, Copa América 2024, Nations League 2024-25
#   Coach continuity: updated post-2022 (Enrique→France, Tuchel→England,
#                     Dorival→Brazil, Martínez→Portugal)
#
# Adjustment rationale per key team:
#   Spain      +0.015  EURO 2024 winners; Yamal 17yo peak; Pedri/Gavi fit
#   Germany    +0.018  EURO 2024 SF run; Wirtz/Musiala both in prime;
#                      Nagelsmann full rebuild complete
#   England    +0.010  Bellingham/Saka/Foden all 22-24, peaking; Tuchel system
#   Argentina  -0.010  Post-Messi era begins; Di María retired; some squad
#                      transition but Scaloni continuity maintains floor
#   Brazil     +0.012  Vinicius/Rodrygo/Endrick top-3 club form; Dorival
#                      tactical stability post-Tite reset
#   France     -0.008  Luis Enrique new (less than 2yr by tournament);
#                      Mbappé club pressure (Real Madrid contract situation)
#   Portugal   -0.015  Ronaldo retired; Martínez new manager; rebuilding
#                      around Ramos/Félix/B.Fernandes but deeper drop
#   Morocco    +0.020  2022 SF legacy; Regragui 4yr tenure by 2026;
#                      Hakimi/Amrabat/Bounou all at confirmed elite level
#   Colombia   +0.015  Copa América 2024 runners-up; James/Díaz/Arias peak
#   Netherlands +0.008 Post-Van Gaal rebuild under De Boer 2.0; Gakpo/Van Dijk
#   Croatia    -0.015  Modrić retired; post-golden-gen transition
#   Belgium    -0.020  Golden gen retired (Hazard, Lukaku reduced); De Bruyne 33
# ---------------------------------------------------------------------------
_SQUAD_SCORES_2026: dict[str, float] = {
    # ── Tier 1: title contenders ──────────────────────────────────────────
    "Spain":          0.905,   # FIFA #1; EURO 2024 winners; Yamal era
    "Argentina":      0.888,   # FIFA #2; defending champions; Scaloni system
    "France":         0.880,   # FIFA #3; Mbappé + depth; new manager discount
    "England":        0.872,   # FIFA #4; EURO 2024 final; Bellingham prime
    "Brazil":         0.868,   # FIFA #5; Vinicius/Rodrygo/Endrick; reset
    "Portugal":       0.855,   # FIFA #6; Ramos-led; post-Ronaldo adjustment
    "Netherlands":    0.848,   # FIFA #7; Gakpo/Van Dijk; growing cohesion
    "Germany":        0.858,   # FIFA #9; Wirtz/Musiala; EURO 2024 SF
    # ── Tier 2: dark horses ───────────────────────────────────────────────
    "Belgium":        0.800,   # FIFA #8; De Bruyne 33; generation turning
    "Morocco":        0.792,   # FIFA #11; 2022 SF legacy; peak window
    "Croatia":        0.762,   # FIFA #10; post-Modrić; Kovačić/Gvardiol core
    "Colombia":       0.778,   # FIFA #13; Copa 2024 runners-up; James peak
    "Uruguay":        0.748,   # FIFA #16; Núñez/Valverde; strong qualifying
    "Switzerland":    0.738,   # FIFA #17; consistent Xhaka-era; tough group
    "Japan":          0.730,   # FIFA #18; strong qualifying; high-press peak
    "Senegal":        0.722,   # FIFA #19; Diatta/Sarr/Dia attack
    "Iran":           0.690,   # FIFA #20; strong AFC qualifying winner
    "South Korea":    0.710,   # FIFA #22; Son still active; young core
    "Ecuador":        0.695,   # FIFA #23; Caicedo/Ibarra; 2nd in CONMEBOL qual
    "Austria":        0.688,   # FIFA #24; Alaba + Sabitzer; Nations League A
    "Australia":      0.672,   # FIFA #26; Irvine/Hrustic; solid AFC run
    "Mexico":         0.668,   # FIFA #15 (co-host boost); home crowd advantage
    "Norway":         0.665,   # FIFA #29; Haaland-led; first WC since 1998
    "Canada":         0.658,   # FIFA #27 (co-host); Davies/David; 2nd WC
    "Panama":         0.620,   # FIFA #30; CONCACAF qualifier winner
    "Egypt":          0.618,   # FIFA #34; Salah farewell motivation
    "Algeria":        0.615,   # FIFA #35; Mahrez/Bennacer; strong CAF run
    "Scotland":       0.608,   # FIFA #36; McTominay/Robertson; first WC since 1998
    "Paraguay":       0.605,   # FIFA #39; scrappy CONMEBOL qualifiers
    "Tunisia":        0.598,   # FIFA #40; experienced CAF campaigners
    "Ivory Coast":    0.595,   # FIFA #42; Zaha-era transition; AFCON 2024 champs
    "Sweden":         0.590,   # UEFA playoff B winners; returning after 2018
    "Turkey":         0.585,   # UEFA playoff C winners; Çalhanoğlu-led
    "United States":  0.660,   # FIFA #14 (co-host); Pulisic/Reyna/McKennie
    "Saudi Arabia":   0.570,   # FIFA #60; domestic league investment signal
    "South Africa":   0.558,   # FIFA #61; home-region advantage CAF
    "South Korea":    0.710,
    "Uzbekistan":     0.520,   # debut; AFC qualifier; unknown ceiling
    "Qatar":          0.500,   # through qualifying; limited squad depth
    "Cape Verde":     0.512,   # first-time qualifier; CAF qualifier winner
    "DR Congo":       0.518,   # AFCON contender; first WC since 1974
    "Ghana":          0.510,   # FIFA #72; experienced WC returner
    "Jordan":         0.490,   # debut; AFC qualifier runner-up
    "Haiti":          0.478,   # CONCACAF; first WC since 1974
    "New Zealand":    0.462,   # OFC; limited top-level competition
    "Curacao":        0.445,   # debut; smallest nation to qualify
    "Bosnia":         0.552,   # UEFA; first major tournament since 2014
    "Czech Republic": 0.568,   # UEFA; returning after 2006
    "Iraq":           0.498,   # first WC since 1986
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
      - Confirmed group draw (FIFA Dec 5 2025)
      - 2026-era squad composite scores
      - VaR/CVaR bounded match noise (3% VaR, σ≈0.016)
      - Shootout specialist ratings
      - Round of 32 stage (new in 2026 format)

    No known winner to validate against — outputs championship probabilities
    and bracket progression odds as a live prediction.
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
        print("  Model: VaR/CVaR noise · 2026-era squads · confirmed groups")
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
        print("  ► (No known result — this is a live forecast)")
        print("=" * 70 + "\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    fc = WC2026Forecast(n_simulations=50_000, seed=2026)
    fc.print_forecast()
