import numpy as np
from ..config_loader import ConfigModel


class FmoHamiltonian:
    """
    Constructs the 8-site FMO Hamiltonian with reaction center trapping.
    Note: Site indices 1-8 in physics are converted to 0-7 in Python.
    All inter-site couplings must be explicitly defined; missing pairs
    raise a ValueError during initialization.
    """

    def __init__(self, config: ConfigModel):
        self.config = config.quantum.fmo
        self.nsites = 8
        self.gamma_rc = self.config.coupling_reaction_center
        self._initialize_base_hamiltonian()

    def _initialize_base_hamiltonian(self):
        # Base 7-site Hamiltonian energies from literature (Adolphs & Renger)
        # We initialize an 8x8 matrix.
        self.H_base = np.zeros((8, 8), dtype=complex)

        # Site energies (cm-1) relative to site 3/4
        energies = [
            280,
            420,
            0,
            110,
            270,
            500,
            310,
            200,
        ]  # Standard model expanded to include site 8
        for i in range(8):
            self.H_base[i, i] = energies[i]

        # Inter-site coupling constants (cm-1)
        couplings = {
            (0, 1): -87.7,
            (0, 2): 5.5,
            (0, 3): -5.9,
            (0, 4): 6.7,
            (0, 5): -13.7,
            (0, 6): -9.9,
            (0, 7): 21.0,
            (1, 2): 30.0,
            (1, 3): 8.2,
            (1, 4): 0.7,
            (1, 5): 11.8,
            (1, 6): 4.3,
            (1, 7): -4.2,
            (2, 3): -53.5,
            (2, 4): -2.2,
            (2, 5): -9.6,
            (2, 6): 6.0,
            (2, 7): 0.6,
            (3, 4): -70.7,
            (3, 5): -17.0,
            (3, 6): -63.3,
            (3, 7): -1.3,
            (4, 5): 81.1,
            (4, 6): -1.3,
            (4, 7): 1.5,
            (5, 6): 39.7,
            (5, 7): -7.9,
            (6, 7): 12.0,
        }

        # Validate that all site pairs (i,j) with i<j are defined
        expected_pairs = {(i, j) for i in range(8) for j in range(i + 1, 8)}
        defined_pairs = set(couplings.keys())
        missing = expected_pairs - defined_pairs
        if missing:
            raise ValueError(
                f"Missing inter-site couplings for pairs: {sorted(missing)}"
            )

        # Validate that all coupling values are finite (no NaN or Inf)
        for (i, j), val in couplings.items():
            if not np.isfinite(val):
                raise ValueError(
                    f"Non-finite coupling value for pair ({i},{j}): {val}"
                )

        for (i, j), val in couplings.items():
            self.H_base[i, j] = val
            self.H_base[j, i] = val

    def get_hamiltonian(self) -> np.ndarray:
        """
        Returns H_base + H_trap
        """
        H_total = self.H_base.copy()
        # Non-Hermitian trapping term on Site 3 (index 2) and Site 4 (index 3)
        # H_trap = -i * Gamma_RC * (|3><3| + |4><4|)
        # In 0-indexed terms, physical site 3 is index 2, physical site 4 is index 3.
        H_total[2, 2] -= 1j * self.gamma_rc
        H_total[3, 3] -= 1j * self.gamma_rc
        return H_total
