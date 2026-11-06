"""Plot predicted linear-absorption spectra (NPoM OFF vs ON) for SI S12.

ponytail: reads what spectro_npom_fmo.py --full writes; no theming layer.
Run: conda run -n MesoHOP-sim-18 python scripts/plot_predicted_spectra.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SPECTRO = ROOT / "data" / "spectro"
OUT = ROOT / "Submission_Package_SolarEnergy_Manuscript" / "figures"


def load(cfg: str) -> tuple[np.ndarray, np.ndarray]:
    arr = np.loadtxt(SPECTRO / f"spectrum_{cfg}.csv", delimiter=",")
    return arr[:, 0], arr[:, 1]


def main() -> None:
    axis_off, pow_off = load("off")
    axis_on, pow_on = load("on")
    peaks = json.loads((SPECTRO / "peaks.json").read_text())

    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=600)
    ax.plot(axis_off, pow_off / pow_off.max(), lw=1.1, color="#1f4e79", label="NPoM OFF (8-site FMO)")
    ax.plot(axis_on, pow_on / pow_on.max(), lw=1.1, color="#c0392b", ls="--", label="NPoM ON (dressed, $V=0.8\\,nm^3$)")

    # Annotate matched-shift lines (ON peaks that moved vs OFF).
    for row in peaks.get("shift_table", []):
        off_c, on_c, shift = row["off_cm1"], row["on_cm1"], row["delta_cm1"]
        i_off = int(np.argmin(np.abs(axis_off - off_c)))
        i_on = int(np.argmin(np.abs(axis_on - on_c)))
        ax.annotate(
            f"$\\Delta={shift:+.0f}$ cm$^{-1}$",
            xy=(on_c, pow_on[i_on] / pow_on.max()),
            xytext=(off_c, pow_off[i_off] / pow_off.max()),
            arrowprops={"arrowstyle": "->", "color": "0.35", "lw": 0.7},
            fontsize=6.5,
            ha="center",
            va="bottom",
        )

    ax.set_xlabel("Energy (cm$^{-1}$)")
    ax.set_ylabel("Normalized absorption")
    ax.set_xlim(50, 2500)
    ax.legend(fontsize=7)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "Figure_SI_predicted_spectra.png"
    fig.savefig(target)
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
