"""Fast checks on the generated record and current public documentation."""
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = json.loads((ROOT / "audit/results.json").read_text())


@pytest.mark.parametrize("key", ["v1_2022", "v2_2022", "trials_2018"])
def test_stage_points_add_up(key):
    bps = RESULTS[key]["bps"]
    assert sum(bps[k]["pts"] for k in ("r16", "qf", "sf", "fin", "win")) == bps["total"]["pts"]


def test_default_trial_2022_is_documented():
    r = RESULTS["trials_2022"][0]
    assert r["seed"] == 42 and r["n_simulations"] == 50000
    assert r["bps"]["total"]["pts"] == 50
    assert "50/64" in (ROOT / "2022-backtest/README.md").read_text()


def test_supplied_2018_points_are_disclosed():
    r = RESULTS["trials_2018"]
    assert r["bps"]["r16"]["pts"] == 16
    assert r["bps"]["total"]["pts"] - 16 == 31
    assert "31/48" in (ROOT / "2018-backtest/README.md").read_text()


def test_documented_blends_and_ties_match_record():
    for year, r in ((2022, RESULTS["trials_2022"][0]),
                    (2018, RESULTS["trials_2018"])):
        e = r["evaluation"]
        expected = (0.4 * e["bracket_fraction"]
                    + 0.3 * e["market_agreement"]["score"]
                    + 0.3 * e["xg_alignment"]["score"])
        assert e["blended_score"] == pytest.approx(expected)
        assert f'{100 * expected:.1f}%' in (ROOT / f"{year}-backtest/README.md").read_text()
    assert RESULTS["trials_2018"]["evaluation"]["xg_alignment"]["n_ties_excluded"] == 1


def test_no_static_passing_badge_or_pinned_snapshot_claim():
    for path in ROOT.rglob("README.md"):
        text = path.read_text()
        assert "tests-passing-brightgreen" not in text
        assert "are intentionally pinned snapshots" not in text
