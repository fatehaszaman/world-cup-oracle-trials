"""Run the dedicated static 48-team scenario, not a live forecast."""
from pathlib import Path
import argparse
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backtest.wc2026_forecast import WC2026Forecast


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    if args.simulations <= 0:
        parser.error("--simulations must be positive")
    forecast = WC2026Forecast(n_simulations=args.simulations, seed=args.seed)
    forecast.run()
    forecast.print_forecast()


if __name__ == "__main__":
    main()
