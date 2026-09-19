"""Run each isolated project's tests, compilation and executable smoke checks.

Exit nonzero when any check fails. Small smoke samples test execution only;
they must not replace the 50,000-run published historical results.
"""
from pathlib import Path
import argparse
import datetime
import json
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baselines", action="store_true")
    parser.add_argument("--suite", help="Run only this named folder/repository.")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    paths = [ROOT / n for n in ("2018-backtest", "2022-backtest", "2026-prediction")]
    if args.baselines:
        paths = [ROOT.parent / n for n in ("world-cup-oracle", "world-cup-oracle-v2")] + paths
    if args.suite:
        paths = [p for p in paths if p.name == args.suite]
        if not paths:
            parser.error("Unknown suite; use --baselines for sibling repositories.")
    output = ROOT / "audit" / "checks"
    output.mkdir(parents=True, exist_ok=True)
    all_ok = True
    for path in paths:
        if not path.is_dir():
            raise SystemExit(f"Missing repository: {path}")
        checks = {
            "pytest": ["-m", "pytest", "-q", "--disable-warnings", "--junitxml=" + str(output / f"{path.name}.xml")],
            "compile": ["-m", "compileall", "-q", "oracle", "backtest", "data", "examples", "scripts"],
            "imports": ["-c", "import importlib,pkgutil; modules=[m.name for n in ('oracle','data','backtest') for m in pkgutil.walk_packages(importlib.import_module(n).__path__, n+'.')]; [importlib.import_module(n) for n in modules]; print('Imported', len(modules), 'modules successfully')"],
            "prediction": ["examples/run_prediction.py", "--simulations", "16"],
            "backtest": ["examples/run_backtest.py", "--simulations", "16"],
            "benchmark": ["scripts/benchmark.py", "--simulations", "16"],
        }
        record = {"suite": path.name, "python": platform.python_version(),
                  "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "checks": {}}
        for name, command in checks.items():
            try:
                r = subprocess.run([sys.executable, *command], cwd=path,
                                   capture_output=True, text=True, timeout=args.timeout)
                code, text = r.returncode, r.stdout + r.stderr
            except subprocess.TimeoutExpired as exc:
                code, text = 124, f"Timed out after {args.timeout}s: {exc}"
            log = output / f"{path.name}-{name}.log"
            # Normalize presentation whitespace only; preserve all result text.
            normalized = "\n".join(line.rstrip() for line in text.splitlines()).rstrip()
            log.write_text(normalized + "\n" if normalized else "")
            record["checks"][name] = {"returncode": code, "log": log.name,
                                      "command": ["python", *command]}
            if name == "pytest" and code in (0, 1):
                suite = ET.parse(output / f"{path.name}.xml").getroot().find("testsuite")
                if suite is not None:
                    record["pytest"] = {k: int(suite.get(k, 0)) for k in
                                        ("tests", "failures", "errors", "skipped")}
                    record["pytest"]["passed"] = (record["pytest"]["tests"]
                        - sum(record["pytest"][k] for k in ("failures", "errors", "skipped")))
            all_ok &= code == 0
            print(path.name, name, code, flush=True)
        (output / f"{path.name}.json").write_text(json.dumps(record, indent=2) + "\n")
    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
