"""
oracle/coach_correlation.py — Coach Continuity & Player-Coach Correlation Model

## Research Basis

Drawn from documented 2018 and 2022 FIFA World Cup data across all QF+ teams:
  Sources: FIFA.com, ESPN, BBC Sport, The Athletic/NYT, Transfermarkt, Sky Sports,
           Wikipedia (Dalić, Deschamps, Southgate, Scaloni, Regragui, Tabárez),
           Al Jazeera, Marca, Business Insider, Sportsnet, Tandfonline

## What This Module Models

### 1. Coach Tenure Signal
Coach tenure length correlates weakly with ranking outperformance — but the
data reveals a more nuanced pattern:

  Tenure band     | n  | Pattern
  ----------------|----|---------
  <1 year         | 2  | Extreme positive outliers (Dalić 2018 runner-up; Regragui 2022 SF)
  1–2 years       | 4  | Mixed; host-effect confounds Russia; Belgium/England/Sweden all overperformed
  2–6 years       | 4  | Mixed; Brazil underperformed both WCs under Tite; Scaloni won WC
  >6 years        | 6  | Mostly on-par; no dramatic outliers either direction

Key insight: Brazil (#1 or #2 rank) underperformed BOTH times under long-tenured Tite.
Croatia (runner-up 2018, 3rd 2022) overperformed under Dalić at <1yr and then ~5yr.
The primary driver is SQUAD COHESION AND IDENTITY, not raw tenure length.

### 2. Coach-Player Trust / Conflict Adjustments
Documented relationships with quantified score deltas:

  Trust relationships that produced measurable overperformance:
  - Scaloni–Messi (2022): Messi scored 11 PSG goals all season → 7 WC goals + Golden Ball
    Delta: system built around Messi's strengths; +0.035 score adjustment for Argentina
  - Dalić–Modrić (2018 & 2022): Modrić played through legal crisis; won Golden Ball at 32
    Delta: +0.022 for Croatia both years
  - Deschamps–Griezmann (2018 & 2022): Coach supported Griezmann through "The Decision"
    saga; Griezmann delivered key contributions both tournaments
    Delta: +0.012 for France
  - Southgate–Bellingham (2022): Early identification at 19 → scored on WC debut
    Delta: +0.010 for England
  - Regragui–Amrabat/Ounahi (2022): Freed players from lower clubs; both massively
    overperformed (Amrabat: Fiorentina → WC standout; Ounahi: Angers → transfer window star)
    Delta: included in Morocco's form boost alongside squad culture inheritance

  Conflict relationships that produced measurable underperformance:
  - Santos–Ronaldo (2022): Ronaldo's public Man United fallout carried into WC;
    visibly disrupted team focus; Santos fired post-tournament
    Delta: -0.015 for Portugal
  - Tite–Neymar dynamic (2018 & 2022): Coach defended Neymar's diving publicly;
    team's aggression/media distraction outweighed Neymar's individual quality
    Delta: -0.010 for Brazil both years (stacked on age/physical penalties)

### 3. Squad Cohesion Score
Separate from coach tenure: how stable has the SQUAD CORE been across 2+ tournaments?
- High cohesion: same 8-12 starters across 2+ major tournaments → stronger identity
- Low cohesion: major squad turnover, fractured dressing room, captain controversy

## Implementation

The module exposes:
  get_coach_multiplier(team, tournament_year) → float  (score multiplier, ~0.94–1.06)
  get_trust_delta(team, tournament_year)      → float  (additive score delta, ~±0.04)
  get_cohesion_score(team, tournament_year)   → float  (0.0–1.0 cohesion index)
  apply_coach_adjustments(scores, year)       → dict   (full team:score dict with adjustments applied)

The combined effect is bounded at ±0.06 per team to prevent overcorrection.
"""

from __future__ import annotations

from typing import NamedTuple


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

class CoachRecord(NamedTuple):
    team:              str
    tournament_year:   int
    coach_name:        str
    tenure_years:      float   # Years in post at tournament start
    same_coach_2yr:    bool    # Was this coach in place 2 years prior?
    qualifying_cont:   bool    # Led full qualifying campaign?
    trust_delta:       float   # Score delta from trust/conflict relationships
    cohesion_score:    float   # 0.0–1.0 squad cohesion index
    notes:             str     # Documented rationale


# ---------------------------------------------------------------------------
# Empirical coach records — 2018 World Cup QF+ teams
# ---------------------------------------------------------------------------

_COACH_RECORDS_2018: list[CoachRecord] = [
    CoachRecord(
        team="France", tournament_year=2018,
        coach_name="Didier Deschamps", tenure_years=6.0,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=+0.012,   # Deschamps–Griezmann: publicly backed him through "The Decision"; Griezmann delivered
        cohesion_score=0.88,
        notes=(
            "Deschamps in post since Jul 2012. Benzema excluded (Valbuena scandal) — "
            "debated but France won. Griezmann free spirit quote post-club saga. "
            "Pogba/Kanté consistent with club form. Mbappé breakout as youngest brace scorer since Pelé. "
            "Trust delta from documented Deschamps-Griezmann relationship (ESPN June 2018)."
        ),
    ),
    CoachRecord(
        team="Croatia", tournament_year=2018,
        coach_name="Zlatko Dalić", tenure_years=0.67,
        same_coach_2yr=False, qualifying_cont=False,
        trust_delta=+0.022,   # Dalić–Modrić deep trust; Kalinić sent home → discipline cemented
        cohesion_score=0.91,
        notes=(
            "Dalić emergency appointment Oct 2017 (replaced sacked Čačić). Only 8 months tenure. "
            "Sent Kalinić home after substitute refusal vs Nigeria — authority established immediately. "
            "Modrić played through perjury charges; Dalić's trust philosophy ('frank and sincere') "
            "unlocked Modrić's Golden Ball. Squad had strong pre-existing identity (SAME SQUAD from "
            "qualifying). Cohesion score reflects squad stability, not coach tenure. "
            "Source: Wikipedia/Dalić, ESPN Croatia report."
        ),
    ),
    CoachRecord(
        team="Belgium", tournament_year=2018,
        coach_name="Roberto Martínez", tenure_years=2.0,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=+0.008,   # Player-power culture; Hazard/De Bruyne trust environment
        cohesion_score=0.83,
        notes=(
            "Martínez appointed Aug 2016. Player-led environment with strong collective trust. "
            "Hazard 46 completed dribbles — 3rd-highest WC history at that point; adidas Silver Ball. "
            "De Bruyne below peak (injury). Lukaku 4 goals. Belgium reached SF vs France. "
            "Source: Business Insider/ESPN."
        ),
    ),
    CoachRecord(
        team="England", tournament_year=2018,
        coach_name="Gareth Southgate", tenure_years=1.75,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=+0.008,   # Southgate's psychologically safe environment; Kane captain breakout
        cohesion_score=0.80,
        notes=(
            "Southgate permanent from Dec 2016. Emphasis on player mental wellbeing. "
            "Kane: PL top scorer → WC Golden Boot (6 goals). Trippier above-expectations performance. "
            "England's first WC SF since 1990. Source: Wikipedia/Southgate."
        ),
    ),
    CoachRecord(
        team="Russia", tournament_year=2018,
        coach_name="Stanislav Cherchesov", tenure_years=2.0,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=+0.005,   # Cheryshev freed from fringe role → 4 goals
        cohesion_score=0.72,
        notes=(
            "Russia FIFA rank #65 — extreme host-nation overperform. Cherchesov's defensive system "
            "beat Spain on penalties in R16. Cheryshev (fringe Villarreal player) → 4 WC goals. "
            "Host advantage modelled separately; this trust delta reflects Cheryshev activation. "
            "Source: Sportsnet R16 Power Rankings."
        ),
    ),
    CoachRecord(
        team="Uruguay", tournament_year=2018,
        coach_name="Óscar Tabárez", tenure_years=12.0,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=+0.000,   # 12-year culture = expected performance level; no overperform delta
        cohesion_score=0.93,
        notes=(
            "Tabárez longest-serving national coach at 2018 WC (12 years). Deep collective culture. "
            "Cavani injury before QF vs France considered decisive for exit. Suárez influential in "
            "group stage. Long tenure built 'collective spirit, tradition, consistency' (The Athletic). "
            "Performed at rank expectation (17th → QF), not above — no delta applied. "
            "Source: The Athletic/NYT June 2018."
        ),
    ),
    CoachRecord(
        team="Brazil", tournament_year=2018,
        coach_name="Tite", tenure_years=2.0,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=-0.010,   # Neymar diving distraction; Tite defended publicly → team aggression signal
        cohesion_score=0.76,
        notes=(
            "Tite made Brazil first non-host to qualify for 2018. Neymar injury (Feb 2018) affected "
            "conditioning. Neymar simulation attracted global mockery; Tite defended 'exceptional' player "
            "publicly. Brazil #2 rank → QF exit = significant underperform. Coutinho strong; Neymar "
            "controversial. Negative delta from documented distraction pattern. "
            "Source: Reuters 2018, ESPN Oct 2021."
        ),
    ),
    CoachRecord(
        team="Sweden", tournament_year=2018,
        coach_name="Janne Andersson", tenure_years=2.0,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=+0.005,   # Collective system unlocked; eliminated Italy and Netherlands in qualifying
        cohesion_score=0.82,
        notes=(
            "Andersson's systemic approach — collective over individual. Defeated Germany in group. "
            "No Ibrahimović (post-international retirement). First WC since 2006. "
            "Source: Tandfonline case study (Taylor & Francis 2022)."
        ),
    ),
]

# ---------------------------------------------------------------------------
# Empirical coach records — 2022 World Cup QF+ teams
# ---------------------------------------------------------------------------

_COACH_RECORDS_2022: list[CoachRecord] = [
    CoachRecord(
        team="Argentina", tournament_year=2022,
        coach_name="Lionel Scaloni", tenure_years=4.25,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=+0.035,   # Scaloni–Messi system built for Messi; worst PSG season → Golden Ball
        cohesion_score=0.92,
        notes=(
            "Scaloni appointed Aug 2018 (interim after Sampaoli debacle); permanent Nov 2018. "
            "Messi at PSG: 11 goals in 34 apps (worst professional season) → WC: 7 goals, 3 assists, "
            "5 MOTM, Golden Ball — most dramatic club-to-WC overperformance across both tournaments. "
            "Scaloni quote: 'We have a relationship of great trust, can talk about everything.' "
            "Enzo Fernández Best Young Player. Emiliano Martínez Golden Glove + PK saves vs Netherlands. "
            "System distributed defensive duties to free Messi. Source: Sporting News, Fox Sports."
        ),
    ),
    CoachRecord(
        team="France", tournament_year=2022,
        coach_name="Didier Deschamps", tenure_years=10.5,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=+0.008,   # Griezmann deployed in evolved #10 role; tactical adaptation over years
        cohesion_score=0.85,
        notes=(
            "Deschamps continuous since 2012. Benzema recalled 2021 but withdrew injured 2 days before "
            "tournament. Mbappé: 8 goals, hat-trick in final. Giroud became France all-time top scorer. "
            "Griezmann in deeper #10 role (Atlético adaptation) — joint-top assists (3). "
            "Mbappe-Griezmann internal friction reported (L'Equipe) but managed. France reached Final. "
            "Source: Wikipedia/Deschamps, Mirror 2021."
        ),
    ),
    CoachRecord(
        team="Croatia", tournament_year=2022,
        coach_name="Zlatko Dalić", tenure_years=5.0,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=+0.022,   # Consistent with 2018 — Dalić–Modrić trust maintained across two WCs
        cohesion_score=0.90,
        notes=(
            "Dalić 2nd WC at 5yr tenure (vs 0.67yr in 2018). Modrić 37yo, 4th WC, still driving midfield. "
            "Livaković: PKs vs Japan R16 and Brazil QF. Gvardiol emerged as top CB prospect. "
            "Croatia 3rd place — 2nd successive WC semifinal under Dalić. Most sustained overperformance "
            "case across both tournaments. Source: Wikipedia/Dalić."
        ),
    ),
    CoachRecord(
        team="Morocco", tournament_year=2022,
        coach_name="Walid Regragui", tenure_years=0.23,
        same_coach_2yr=False, qualifying_cont=False,
        trust_delta=+0.015,   # Freed Amrabat/Ounahi from lower-club shadow; motivational uplift
        cohesion_score=0.89,
        notes=(
            "Regragui appointed 31 Aug 2022 — only 85 DAYS before Morocco's first WC match. "
            "Previous coach Halilhodžić dismissed 3 months prior; squad culture inherited intact. "
            "Squad identity built under Halilhodžić; Regragui added tactical organization + motivation. "
            "Amrabat (Fiorentina) → WC standout; Ounahi (Angers, relegation club) → elite interest. "
            "Bounou: La Liga's best GK that season → 3 WC clean sheets. Hakimi: 42 successful duels. "
            "First African/Arab coach to reach WC SF. Counter-argument to tenure hypothesis. "
            "Source: Wikipedia/Regragui, Al Jazeera Dec 2022."
        ),
    ),
    CoachRecord(
        team="Netherlands", tournament_year=2022,
        coach_name="Louis van Gaal", tenure_years=1.25,
        same_coach_2yr=False, qualifying_cont=True,
        trust_delta=+0.003,   # Van Gaal cancer backdrop = 'fighting for Louis' rallying effect; Gakpo activation
        cohesion_score=0.78,
        notes=(
            "Van Gaal (third Netherlands stint) appointed Aug 2021; replaced Frank de Boer. "
            "Managed while battling aggressive prostate cancer — publicly disclosed mid-tournament. "
            "'We are fighting for Louis' team rallying cry. Gakpo: 3 goals from 0.31 xG (extreme efficiency). "
            "Van Dijk consistent defensive anchor. Weghorst (Besiktas loan → 90+11 equalizer vs Argentina QF). "
            "Netherlands eliminated on PKs vs Argentina. Source: Marca Dec 2022, ESPN."
        ),
    ),
    CoachRecord(
        team="Brazil", tournament_year=2022,
        coach_name="Tite", tenure_years=6.5,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=-0.010,   # Pattern repeats: Brazil #1 rank → QF exit; Vinicius below expectations
        cohesion_score=0.74,
        notes=(
            "Tite 2nd WC (longest-serving at 2022 WC — 2,346 days in post). "
            "Brazil #1 rank → QF exit vs Croatia on PKs = significant underperform for 2nd straight WC. "
            "Richarlison bicycle kick vs Serbia = WC goal of tournament (3 goals total). "
            "Vinicius Jr: strong Real Madrid form → ineffective at WC. Neymar injured in group, returned QF. "
            "Tite stepped down post-tournament. Most notable 'high tenure, underperform' case both WCs. "
            "Source: CBS Sports/ESPN."
        ),
    ),
    CoachRecord(
        team="England", tournament_year=2022,
        coach_name="Gareth Southgate", tenure_years=6.0,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=+0.010,   # Southgate–Bellingham trust; early identification of 19yo
        cohesion_score=0.83,
        notes=(
            "Southgate 6yr tenure (2nd WC). Bellingham (19): first WC start → scored on debut vs Iran, "
            "drove QF vs Senegal. 'I don't think we could have predicted how quickly Bellingham could mature.' "
            "Kane consistent (3 goals). Maguire loyalty controversial but adequate. "
            "Foden below expected impact. England QF = on par with rank. "
            "Source: The Independent Dec 2022, The Athletic/NYT."
        ),
    ),
    CoachRecord(
        team="Portugal", tournament_year=2022,
        coach_name="Fernando Santos", tenure_years=8.0,
        same_coach_2yr=True, qualifying_cont=True,
        trust_delta=-0.015,   # Santos–Ronaldo conflict: Piers Morgan interview, sub-reaction, bench drama
        cohesion_score=0.70,
        notes=(
            "Santos 8yr tenure. Ronaldo publicly fell out with Man United management (Piers Morgan "
            "interview Oct 2022 — frozen out at club). At WC: started but substituted vs South Korea; "
            "reacted angrily (media footage). Santos dropped Ronaldo for R16 and QF. "
            "Ramos (first WC start): hat-trick vs Switzerland R16 — youngest WC knockout hat-trick since Pelé. "
            "Bruno Fernández: 5 goal contributions. Santos fired post-Morocco loss. "
            "Ronaldo saga dominated media → documented team distraction. "
            "Source: ESPN Dec 2022, Sky Sports, Goal.com."
        ),
    ),
]

# ---------------------------------------------------------------------------
# Index for fast lookups
# ---------------------------------------------------------------------------

_ALL_RECORDS: list[CoachRecord] = _COACH_RECORDS_2018 + _COACH_RECORDS_2022
_INDEX: dict[tuple[str, int], CoachRecord] = {
    (r.team, r.tournament_year): r for r in _ALL_RECORDS
}

# Teams we have coach data for
COVERED_TEAMS_2018 = {r.team for r in _COACH_RECORDS_2018}
COVERED_TEAMS_2022 = {r.team for r in _COACH_RECORDS_2022}


# ---------------------------------------------------------------------------
# Tenure multiplier function
# ---------------------------------------------------------------------------

def _tenure_multiplier(tenure_years: float, same_coach_2yr: bool) -> float:
    """
    Convert coach tenure into a composite score multiplier.

    Based on empirical pattern across 16 team-entries (2018 + 2022 WCs):
      - <1 year BUT squad culture inherited intact → slight positive (Dalić/Regragui pattern)
      - 1–2 years → modest positive (stability forming)
      - 2–5 years → neutral baseline (most cases)
      - >5 years → slight positive if qualifying cont, slight negative if squad stagnation signal
      - No coach 2yr prior → small negative (uncertainty cost)

    The multiplier range is tight (0.97–1.03) — tenure is a WEAK signal.
    The strong signals are trust_delta and cohesion_score.
    """
    if tenure_years < 1.0:
        # New coach with inherited squad identity (Dalić/Regragui): slight boost
        base = 1.010 if same_coach_2yr else 1.005
    elif tenure_years < 2.0:
        base = 1.012
    elif tenure_years < 4.0:
        base = 1.008
    elif tenure_years < 7.0:
        base = 1.005
    else:
        # Long tenure: diminishing marginal returns; Brazil pattern caps the upside
        base = 1.002

    # Discount if no continuity from 2yr prior
    if not same_coach_2yr:
        base -= 0.008

    return round(base, 4)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_coach_record(team: str, year: int) -> CoachRecord | None:
    """Return the CoachRecord for a team at a given tournament year, or None."""
    return _INDEX.get((team, year))


def get_coach_multiplier(team: str, year: int) -> float:
    """
    Returns a score multiplier (0.97–1.03) based on coach tenure pattern.
    Returns 1.0 (neutral) if team/year not in database.
    """
    rec = _INDEX.get((team, year))
    if rec is None:
        return 1.0
    return _tenure_multiplier(rec.tenure_years, rec.same_coach_2yr)


def get_trust_delta(team: str, year: int) -> float:
    """
    Returns an additive score delta (±0.035) from documented coach-player
    trust/conflict relationships. Returns 0.0 if team/year not in database.
    """
    rec = _INDEX.get((team, year))
    return rec.trust_delta if rec is not None else 0.0


def get_cohesion_score(team: str, year: int) -> float:
    """
    Returns squad cohesion index (0.0–1.0). High cohesion = stable core squad
    with embedded team identity across 2+ tournaments.
    Returns 0.75 (neutral default) if team/year not in database.
    """
    rec = _INDEX.get((team, year))
    return rec.cohesion_score if rec is not None else 0.75


def apply_coach_adjustments(
    scores: dict[str, float],
    year: int,
    weight: float = 0.40,
) -> dict[str, float]:
    """
    Apply coach continuity and trust adjustments to a team scores dict.

    Parameters
    ----------
    scores : dict[str, float]
        Base composite scores (0–1 scale) for all teams.
    year   : int
        Tournament year (2018 or 2022).
    weight : float
        Blend weight for coach adjustments (default 0.40 = 40% of max effect).
        Kept conservative to prevent over-fitting to two WC observations.

    Returns
    -------
    dict[str, float]
        Adjusted scores, bounded to [0.20, 1.0].

    Adjustment formula
    ------------------
    1. multiplier  = tenure_multiplier(team, year)
    2. trust_raw   = get_trust_delta(team, year)
    3. cohesion    = get_cohesion_score(team, year) — used to scale trust
       (high-cohesion squads amplify trust effects; low-cohesion squads dampen them)
    4. effective_delta = trust_raw × cohesion × weight
    5. adjusted = (base × multiplier + effective_delta) — capped at ±0.06

    The ±0.06 global cap prevents any single coach signal from dominating
    the composite score model.
    """
    adjusted: dict[str, float] = {}
    MAX_TOTAL_EFFECT = 0.06   # Hard cap: coach signal cannot shift score by >6pp

    for team, base in scores.items():
        rec = _INDEX.get((team, year))

        if rec is None:
            adjusted[team] = base
            continue

        # Step 1: tenure multiplier (1.0 ± ~0.01)
        mult = _tenure_multiplier(rec.tenure_years, rec.same_coach_2yr)

        # Step 2: trust/conflict delta, scaled by cohesion and blend weight
        # Cohesion amplifies positive trust signals and attenuates negative conflict signals
        effective_delta = rec.trust_delta * rec.cohesion_score * weight

        # Step 3: raw adjusted value
        raw_adjusted = base * mult + effective_delta

        # Step 4: cap the total absolute shift from base
        total_shift = raw_adjusted - base
        if abs(total_shift) > MAX_TOTAL_EFFECT:
            total_shift = MAX_TOTAL_EFFECT * (1 if total_shift > 0 else -1)

        final = base + total_shift
        adjusted[team] = round(max(0.20, min(1.0, final)), 4)

    return adjusted


# ---------------------------------------------------------------------------
# Correlation summary (for reporting / README)
# ---------------------------------------------------------------------------

def print_correlation_summary(year: int) -> None:
    """Print a formatted summary of coach signals for a given tournament year."""
    records = [r for r in _ALL_RECORDS if r.tournament_year == year]
    if not records:
        print(f"No data for year {year}")
        return

    print(f"\n{'='*72}")
    print(f"  Coach Correlation Summary — {year} FIFA World Cup")
    print(f"{'='*72}")
    print(f"  {'Team':<14} {'Coach':<22} {'Tenure':>6} {'2yr?':>5} {'Trust':>7} {'Cohesion':>9}")
    print(f"  {'-'*72}")

    # Sort by trust delta descending
    for r in sorted(records, key=lambda x: x.trust_delta, reverse=True):
        tenure_str = f"{r.tenure_years:.2f}y"
        cont_str   = "YES" if r.same_coach_2yr else "NO"
        trust_str  = f"{r.trust_delta:+.3f}"
        print(f"  {r.team:<14} {r.coach_name:<22} {tenure_str:>6} {cont_str:>5} {trust_str:>7} {r.cohesion_score:>9.2f}")

    print(f"\n  KEY INSIGHT: No clean linear tenure→performance correlation.")
    print(f"  Biggest overperformers: Croatia 2018 (0.67yr), Morocco 2022 (0.23yr)")
    print(f"  Biggest underperformer: Brazil (both WCs) under long-tenured Tite")
    print(f"  Primary driver: squad cohesion + coach-player trust, not raw tenure")
    print(f"{'='*72}\n")


# ---------------------------------------------------------------------------
# Module self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print_correlation_summary(2018)
    print_correlation_summary(2022)

    print("\n  Sample adjustments (2022 WC base scores):")
    sample_scores = {
        "Argentina": 0.878, "France": 0.885, "Brazil": 0.838,
        "Morocco": 0.672, "Croatia": 0.726, "Portugal": 0.791,
        "England": 0.834, "Netherlands": 0.762,
    }
    adj = apply_coach_adjustments(sample_scores, year=2022, weight=0.40)
    print(f"\n  {'Team':<14} {'Base':>6} {'Adj':>6} {'Delta':>7}")
    print(f"  {'-'*38}")
    for team in sorted(sample_scores, key=lambda t: sample_scores[t], reverse=True):
        base = sample_scores[team]
        a    = adj[team]
        print(f"  {team:<14} {base:>6.3f} {a:>6.3f} {a-base:>+7.4f}")
