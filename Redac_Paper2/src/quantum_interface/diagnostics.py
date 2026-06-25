import numpy as np

from ..config_loader import ConfigModel
from ..constants import (
    FMO_NSITES,
    N_DIM_DRESSED,
    PLASMON_COUPLING_SITES,
    SERS_ENHANCEMENT_FACTOR,
    SERS_VIBRONIC_SITES_180,
    SERS_VIBRONIC_SITES_740,
    NPoM_MAX_PLASMON_COUPLING_CM,
    NPoM_REFERENCE_COUPLING_CM,
    NPoM_REFERENCE_MODE_VOLUME_NM3,
    NPoM_VOLUME_GUARDRAIL_THRESHOLD,
)


class NpomCoupling:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.mode_volume_nm3 = config.quantum.fmo.mode_volume_nm3

    def get_plasmon_coupling(self) -> float:
        if self.mode_volume_nm3 <= NPoM_VOLUME_GUARDRAIL_THRESHOLD:
            return NPoM_MAX_PLASMON_COUPLING_CM
        g_0 = NPoM_REFERENCE_COUPLING_CM * np.sqrt(
            NPoM_REFERENCE_MODE_VOLUME_NM3 / self.mode_volume_nm3
        )
        return float(g_0)

    def dress_hamiltonian(self, H_fmo: np.ndarray) -> np.ndarray:
        g_0 = self.get_plasmon_coupling()
        H_dressed = np.zeros((N_DIM_DRESSED, N_DIM_DRESSED), dtype=complex)
        H_dressed[:FMO_NSITES, :FMO_NSITES] = H_fmo
        H_dressed[FMO_NSITES, FMO_NSITES] = 0.0
        for site in PLASMON_COUPLING_SITES:
            H_dressed[site, FMO_NSITES] = g_0
            H_dressed[FMO_NSITES, site] = g_0
        return H_dressed


class SersDiagnostics:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.coupling = config.quantum.sers.optomechanical_coupling

    def calculate_raman_spectrum(self, populations: np.ndarray) -> dict:
        enhancement = SERS_ENHANCEMENT_FACTOR * self.coupling
        return {
            "180_cm": float(enhancement * sum(populations[s] for s in SERS_VIBRONIC_SITES_180)),
            "740_cm": float(enhancement * sum(populations[s] for s in SERS_VIBRONIC_SITES_740)),
            "1145_cm": float(enhancement * np.sum(populations)),
        }

    def calculate_correlation_metric(self, raman_spectrum: dict, trap_yield: float) -> float:
        """
        Calculates the diagnostic correlation metric (eta_diag).
        eta_diag = I_180 / trap_yield
        """
        if trap_yield == 0:
            return 0.0
        return float(raman_spectrum["180_cm"] / trap_yield)
