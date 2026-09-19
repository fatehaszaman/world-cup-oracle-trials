"""Run the retrospective 2018 replay with supplied R16 qualifiers."""
from pathlib import Path
import argparse
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backtest.wc2018_backtest import WC2018BacktestV3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulations", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=2018)
    args = parser.parse_args()
    if args.simulations <= 0:
        parser.error("--simulations must be positive")
    bt = WC2018BacktestV3(n_simulations=args.simulations, seed=args.seed)
    bt.run()
    bt.print_report()


if __name__ == "__main__":
    main()
