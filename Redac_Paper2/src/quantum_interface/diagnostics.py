import numpy as np
from ..config_loader import ConfigModel

# NPoM plasmonic coupling constants
# Maximum physically realistic coupling cap (cm-1) when mode volume approaches zero
MAX_PLASMON_COUPLING_CM = 1000.0
# Reference mode volume (nm3) for coupling normalization
REFERENCE_MODE_VOLUME_NM3 = 1.0
# Reference coupling strength (cm-1) at reference volume (typical strong coupling onset)
REFERENCE_COUPLING_CM = 120.0
# Mode volume guardrail threshold (nm3) — below this, use max coupling cap
VOLUME_GUARDRAIL_THRESHOLD = 1e-6

# SERS diagnostic constants
# SERS enhancement factor multiplier (scaled by optomechanical coupling)
SERS_ENHANCEMENT_FACTOR = 100.0


class NpomCoupling:
    """
    Models the strong coherent coupling regime between the 8-site FMO transitions,
    the OPV excitons, and a localized surface plasmon mode within a sub-nanometer
    Nanoparticle-on-Mirror (NPoM) cavity with a graphene barrier.
    """

    def __init__(self, config: ConfigModel):
        self.config = config
        self.mode_volume_nm3 = config.quantum.fmo.mode_volume_nm3

    def get_plasmon_coupling(self) -> float:
        """
        Calculates the single-emitter coupling strength g_0.
        Uses a physically motivated scaling relation g_0 propto 1/sqrt(V_mode).
        Implements a guardrail check to prevent numerical divergence when V_mode -> 0.
        """
        if self.mode_volume_nm3 <= VOLUME_GUARDRAIL_THRESHOLD:
            # High-value guardrail limit to prevent divergence
            return MAX_PLASMON_COUPLING_CM

        # Scaling relationship normalized to standard plasmonic volume references
        g_0 = REFERENCE_COUPLING_CM * np.sqrt(REFERENCE_MODE_VOLUME_NM3 / self.mode_volume_nm3)
        return float(g_0)

    def dress_hamiltonian(self, H_fmo: np.ndarray) -> np.ndarray:
        """
        Dresses the 8-site Hamiltonian by coupling the primary optical sites (e.g., Site 1 and 6)
        to a new single-photon plasmonic mode in the NPoM cavity.
        Excludes direct charge transfer terms (Dexter-type) to model the graphene barrier.
        Returns a 9x9 dressed Hamiltonian matrix.
        """
        g_0 = self.get_plasmon_coupling()

        # Expand H_fmo from 8x8 to 9x9
        # Index 8 represents the plasmonic photon mode in the cavity
        H_dressed = np.zeros((9, 9), dtype=complex)
        H_dressed[0:8, 0:8] = H_fmo

        # Energy of the plasmon mode (resonance matching around 800 nm/12500 cm-1)
        # For dynamics tracking, we write it in the rotating frame where plasmon is relative energy 0.
        H_dressed[8, 8] = 0.0

        # Couple optical input sites (BChl 1 and 6, index 0 and 5) to the plasmon mode
        H_dressed[0, 8] = g_0
        H_dressed[8, 0] = g_0
        H_dressed[5, 8] = g_0
        H_dressed[8, 5] = g_0

        # Graphene barrier shields direct charge transfers. Hence, Dexter terms remain strictly 0.
        # Direct tunneling terms (site to site or site to plasmon) are excluded.

        return H_dressed


class SersDiagnostics:
    """
    Simulates Surface-Enhanced Raman Scattering (SERS) readouts using molecular cavity optomechanics.
    Uses the current FMO population state to calculate expected Raman peak intensities.
    """

    def __init__(self, config: ConfigModel):
        self.config = config
        self.coupling = config.quantum.sers.optomechanical_coupling

    def calculate_raman_spectrum(self, populations: np.ndarray) -> dict:
        """
        Given the population array of the 8 sites, calculates the Raman peak intensities
        for characteristic vibration modes (typically associated with active energy transfer sites).
        Returns a dict of key frequencies (cm-1) and their simulated SERS intensities.
        """
        # We assume 3 characteristic vibrational modes of BChl a in the FMO complex:
        # Mode 1: 180 cm-1 (low frequency Franck-Condon mode, mostly coupled to Site 3/4)
        # Mode 2: 740 cm-1 (ring deformation mode, coupled to Site 1 & 2)
        # Mode 3: 1145 cm-1 (C-C stretch mode, coupled to all active transitions)

        # SERS enhancement is scaled by the optomechanical coupling parameter
        enhancement = SERS_ENHANCEMENT_FACTOR * self.coupling

        mode_180 = enhancement * (populations[2] + populations[3])  # Site 3 & 4
        mode_740 = enhancement * (populations[0] + populations[1])  # Site 1 & 2
        mode_1145 = enhancement * np.sum(populations)  # Total excitation population

        return {
            "180_cm": float(mode_180),
            "740_cm": float(mode_740),
            "1145_cm": float(mode_1145),
        }
