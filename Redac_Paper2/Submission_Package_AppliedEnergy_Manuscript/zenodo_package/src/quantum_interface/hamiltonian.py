import numpy as np

from ..config_loader import ConfigModel
from ..constants import (
    FMO_COUPLINGS_CM,
    FMO_NSITES,
    FMO_SITE_ENERGIES_CM,
    TRAPPING_SITES,
)


class FmoHamiltonian:
    def __init__(self, config: ConfigModel):
        self.config = config.quantum.fmo
        self.nsites = FMO_NSITES
        self.gamma_rc = self.config.coupling_reaction_center
        self._initialize_base_hamiltonian()

    def _initialize_base_hamiltonian(self):
        self.H_base = np.zeros((FMO_NSITES, FMO_NSITES), dtype=complex)
        for i in range(FMO_NSITES):
            self.H_base[i, i] = FMO_SITE_ENERGIES_CM[i]

        expected_pairs = {(i, j) for i in range(FMO_NSITES) for j in range(i + 1, FMO_NSITES)}
        defined_pairs = set(FMO_COUPLINGS_CM.keys())
        missing = expected_pairs - defined_pairs
        if missing:
            raise ValueError(f"Missing inter-site couplings for pairs: {sorted(missing)}")

        for (i, j), val in FMO_COUPLINGS_CM.items():
            if not np.isfinite(val):
                raise ValueError(f"Non-finite coupling value for pair ({i},{j}): {val}")
            self.H_base[i, j] = val
            self.H_base[j, i] = val

    def get_hamiltonian(self) -> np.ndarray:
        H_total = self.H_base.copy()
        for site_idx in TRAPPING_SITES:
            H_total[site_idx, site_idx] -= 1j * self.gamma_rc
        return H_total
