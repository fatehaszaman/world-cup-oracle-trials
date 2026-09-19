"""Compatibility entry point: this folder contains a scenario, not a backtest."""
from run_prediction import main

if __name__ == "__main__":
    print("No historical 2026 backtest is implemented; running the static scenario.")
    main()
