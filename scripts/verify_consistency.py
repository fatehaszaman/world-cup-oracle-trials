"""Recompute published diagnostics in isolated processes.

Run from the trials root: python scripts/verify_consistency.py
Use --baselines if sibling clones world-cup-oracle and world-cup-oracle-v2 exist.
Output is JSON; no result is labeled held-out accuracy.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROBE = """
import json
from backtest.wc{year}_backtest import {cls}
b = {cls}(n_simulations=50000, seed={seed})
{scoring}
result = {{"seed": {seed}, "n_simulations": 50000, "bps": bps}}
if hasattr(b, "blended_evaluation_score"):
    result["evaluation"] = b.blended_evaluation_score()
    for key in ("market_agreement", "xg_alignment"):
        result["evaluation"][key].pop("per_match")
result["bps"].pop("champion_probs", None)
print(json.dumps(result))
"""


def probe(folder, year, cls, seed, baseline2018=False):
    scoring = ("bps = b.bracket_progression_score(b.run())" if baseline2018
               else "bps = b.bracket_progression_score()")
    code = PROBE.format(year=year, cls=cls, seed=seed, scoring=scoring)
    result = subprocess.run([sys.executable, "-c", code], cwd=folder,
                            text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baselines", action="store_true")
    parser.add_argument("--seed-grid", action="store_true",
                        help="Also run seeds 0-9; this can take several minutes")
    args = parser.parse_args()
    output = {
        "interpretation": "In-sample exploratory diagnostics, not forecast accuracy",
        "trials_2022": [
            probe(ROOT / "2022-backtest", 2022, "WC2022Backtest", seed)
            for seed in ([*range(10), 42] if args.seed_grid else [42])
        ],
        "trials_2018": probe(ROOT / "2018-backtest", 2018, "WC2018BacktestV3", 2018),
    }
    if args.baselines:
        output["v1_2022"] = probe(ROOT.parent / "world-cup-oracle", 2022, "WC2022Backtest", 42)
        output["v2_2022"] = probe(ROOT.parent / "world-cup-oracle-v2", 2022, "WC2022Backtest", 42)
        output["v2_2018"] = probe(ROOT.parent / "world-cup-oracle-v2", 2018, "WC2018Backtest", 2018, True)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
