"""Plot cosinor fitted curves for consecutive 24-hour periods."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def compute_cosinor_curve(time_hours: np.ndarray, mesor: float, amplitude: float, phase: float) -> np.ndarray:
    """Compute the cosinor fitted curve for a 24-hour period."""
    angular_frequency = 2 * np.pi / 24
    return mesor + amplitude * np.cos(angular_frequency * time_hours + phase)


def plot_consecutive_cosinor_fits(
    data: pd.DataFrame,
    start_index: int,
    periods: int,
    output_path: Path,
    concatenate: bool,
) -> None:
    """Plot cosinor fits for a consecutive block of days."""
    data = data.sort_values(["record_date", "record_num"]).reset_index(drop=True)
    subset = data.iloc[start_index : start_index + periods]

    time_hours = np.linspace(0, 24, 240)

    fig, ax = plt.subplots(figsize=(10, 6))

    for day_index, row in enumerate(subset.itertuples(index=False)):
        fitted = compute_cosinor_curve(time_hours, row.M, row.A, row.phi)
        label = f"{row.record_date} (#{int(row.record_num)})"
        x_values = time_hours + (24 * day_index if concatenate else 0)
        ax.plot(x_values, fitted, label=label, linewidth=1.5, alpha=0.85)

    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Fitted value")
    title_suffix = "concatenated" if concatenate else "overlaid"
    ax.set_title(f"Cosinor fitted curves (10 consecutive 24-hour periods, {title_suffix})")
    ax.set_xlim(0, 24 * periods if concatenate else 24)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, ncol=2, frameon=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot cosinor fitted curves for 10 consecutive periods.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("data_samples/M0142_cosinor_features.csv"),
        help="Path to the cosinor features CSV file.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Start index for consecutive periods.",
    )
    parser.add_argument(
        "--periods",
        type=int,
        default=10,
        help="Number of consecutive periods to plot.",
    )
    parser.add_argument(
        "--concatenate",
        action="store_true",
        help="Plot consecutive days on a continuous timeline instead of overlapping.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/cosinor_fits.png"),
        help="Output path for the generated plot.",
    )
    args = parser.parse_args()

    data = pd.read_csv(args.csv)
    plot_consecutive_cosinor_fits(
        data,
        args.start,
        args.periods,
        args.output,
        args.concatenate,
    )


if __name__ == "__main__":
    main()
