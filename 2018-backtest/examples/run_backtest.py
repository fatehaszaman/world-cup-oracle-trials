"""Run this folder's 2018 replay, not the absent 2022 module."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backtest.wc2018_backtest import WC2018BacktestV3


if __name__ == "__main__":
    WC2018BacktestV3().print_report()
