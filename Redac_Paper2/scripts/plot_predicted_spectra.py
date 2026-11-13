"""Plot predicted linear-absorption spectra (NPoM OFF vs ON) for SI S12.

ponytail: reads what spectro_npom_fmo.py --full writes; no theming layer.
Run: conda run -n MesoHOP-sim-18 python scripts/plot_predicted_spectra.py
"""

from __future__ import annotations

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

    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=600)
    ax.vlines(axis_off, 0, pow_off / pow_off.max(), color="#1f4e79", lw=1.3, label="NPoM OFF (8-site FMO)")
    ax.vlines(axis_on, 0, pow_on / pow_on.max(), color="#c0392b", linestyle=(0, (4, 2)), lw=1.3,
              label="NPoM ON (dressed, $V=0.8\\,nm^3$)")
    # ponytail: no in-figure labels — matched shifts are dense and always collide;
    # the numeric fingerprint lives in the SM table (delta_cm1 rows).

    ax.set_xlabel("Energy (cm$^{-1}$)")
    ax.set_ylabel("Normalized absorption")
    ax.set_xlim(11500, 13500)
    ax.set_ylim(0, 1.06)
    ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "Figure_SI_predicted_spectra.png"
    fig.savefig(target)
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
