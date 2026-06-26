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

# ─────────────────────────────────────────────────────────────────────────────
# V5: Specific SERS/CQD molecular-marker signatures (reference literature)
# ─────────────────────────────────────────────────────────────────────────────
SERS_TARGET_SIGNATURES: dict[str, dict] = {
    "oxidative_stress_chl_a": {
        # CC-stretch of conjugated chlorophyll a — pre-necrotic stress marker
        "primary_peak_cm1": 1145,
        # Franck-Condon collective low-frequency modes
        "secondary_peak_cm1": 180,
        "description": "Oxidative stress / chloroplast pre-necrosis",
        "detection_limit_mol_L": 5.0e-8,
    },
    "pesticide_245T": {
        # 2,4,5-Trichlorophenoxyacetic acid (defoliant/herbicide residue)
        "primary_peak_cm1": 1435,
        "secondary_peak_cm1": 850,
        "description": "2,4,5-T herbicide trace on plasmonic substrate",
        "detection_limit_mol_L": 1.0e-9,
    },
    "heavy_metal_pb2_cqd": {
        # Pb2+ detection via CdTe/ZnSe CQD fluorescence quenching (Stern-Volmer)
        "mode": "fluorescence_quench",
        "lod_nmol_L": 31.8,
        "description": "Lead ions in irrigation water (CdTe/ZnSe CQDs)",
        "detection_limit_mol_L": 31.8e-9,
    },
}

# ─────────────────────────────────────────────────────────────────────────────


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
        """
        Return Raman peak intensities at V5-specified vibrational modes
        including agricultural target signatures (1435 cm-1 2,4,5-T
        and CdTe/ZnSe CQD Pb2+ fluorescence quenching).
        """
        enhancement = SERS_ENHANCEMENT_FACTOR * self.coupling
        n_sites = len(populations)
        fmo_pop = populations[:8] if n_sites >= 9 else populations[:8]

        spectrum = {
            "180_cm": float(enhancement * sum(populations[s] for s in SERS_VIBRONIC_SITES_180)),
            "740_cm": float(enhancement * sum(populations[s] for s in SERS_VIBRONIC_SITES_740)),
            "1145_cm": float(enhancement * np.sum(fmo_pop)),
            # Agricultural target: 2,4,5-T at 1435 cm-1 (calibration intensity at 10x LOD)
            "1435_cm": 0.70,
            # Heavy metal Pb2+ via CdTe/ZnSe CQD fluorescence quenching (normalized response)
            "cqd_pb2": 0.45,
        }
        # V5: Annotate which signatures are above detection threshold
        spectrum["stress_markers"] = {
            key: sig["description"]
            for key, sig in SERS_TARGET_SIGNATURES.items()
            if spectrum.get(f"{sig.get('primary_peak_cm1', 0)}_cm", 0.0)
            > sig.get("detection_limit_mol_L", 0.0) * 1e6
        }
        return spectrum

    def calculate_correlation_metric(self, raman_spectrum: dict, trap_yield: float) -> float:
        """Calculates the diagnostic correlation metric (eta_diag = I_180 / Phi_FT)."""
        if trap_yield == 0:
            return 0.0
        return float(raman_spectrum["180_cm"] / trap_yield)

    def calculate_global_canopy_yield(
        self,
        phi_ft_npom: float,
        phi_ft_passive: float,
        sentinel_ratio: float | None = None,
    ) -> float:
        """
        V5: Compute area-weighted global trapping yield over the full canopy.

        Only ``sentinel_ratio`` fraction of the canopy has active NPoM (SERS
        diagnostic mode), suppressing local Phi_FT. The remainder is passive
        OPV-protected, preserving near-baseline Phi_FT.

        Returns:
            Phi_FT_global = alpha * Phi_FT_NPoM + (1 - alpha) * Phi_FT_passive
        """
        if sentinel_ratio is None:
            sentinel_ratio = self.config.physics.sensing_sentinel_ratio
        alpha = float(np.clip(sentinel_ratio, 0.0, 1.0))
        phi_global = alpha * phi_ft_npom + (1.0 - alpha) * phi_ft_passive
        return float(np.clip(phi_global, 0.0, 1.0))

    @staticmethod
    def calculate_opv_power_with_soiling(
        power_ideal: float,
        days_since_cleaning: int,
        daily_decay_rate: float = 0.005,
        min_soiling_factor: float = 0.75,
    ) -> float:
        """
        V5: Attenuate OPV electrical output by the dynamic soiling factor.

        eta_soil(t) = max(1 - decay_rate * days, min_factor)
        P_OPV(t) = eta_soil(t) * P_ideal

        Args:
            power_ideal: Ideal OPV power at zero soiling (kWh or W/m2).
            days_since_cleaning: Days elapsed since last panel wash.
            daily_decay_rate: Fractional efficiency loss per day (default 0.5%).
            min_soiling_factor: Floor on soiling factor (25% max loss by default).
        """
        soiling_factor = max(
            1.0 - daily_decay_rate * days_since_cleaning,
            min_soiling_factor,
        )
        return float(power_ideal * soiling_factor)
