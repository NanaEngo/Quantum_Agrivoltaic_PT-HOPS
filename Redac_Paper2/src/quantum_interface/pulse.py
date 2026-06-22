import numpy as np

from ..config_loader import ConfigModel
from ..constants import FLOQUET_SITES, FMO_NSITES, OMIT_SUPPRESSION_RATE


class FloquetStarkSwitch:
    """
    Implements Floquet Stark Detuning and Optomechanically Induced Transparency (OMIT)
    as a dynamic protection switch against exciton overload under high solar intensities.
    """

    def __init__(self, config: ConfigModel):
        self.config = config
        self.solar_threshold = config.simulation.solar_flux_threshold
        self.amplitude = config.quantum.floquet.driving_amplitude
        self.frequency = config.quantum.floquet.driving_frequency

    def get_stark_detuning(self, solar_flux: float, time_ps: float) -> np.ndarray:
        """
        Calculates a time-dependent diagonal energy shift matrix for the FMO site transitions.
        Under high solar flux (exceeding solar_threshold), it detunes the energy levels
        using a time-dependent driving field V(t)*cos(omega*t) in the Floquet picture.
        At zero solar flux (night mode), returns a zero shift matrix.
        """
        shift_matrix = np.zeros((FMO_NSITES, FMO_NSITES), dtype=complex)
        if solar_flux <= 0.0:
            return shift_matrix

        # If solar flux exceeds the threshold, activate the detuning switch
        if solar_flux > self.solar_threshold:
            # Shift primary optical absorption site energies (Site 1 & 6, index 0 and 5)
            # using the Floquet driving envelope
            detuning_val = self.amplitude * np.cos(self.frequency * time_ps)
            for site in FLOQUET_SITES:
                shift_matrix[site, site] = detuning_val

        return shift_matrix

    def apply_omit_attenuation(self, solar_flux: float, baseline_transmission: float) -> float:
        """
        Calculates the attenuated transmission rate using Optomechanically Induced Transparency (OMIT).
        When the solar flux exceeds the threshold, OMIT modulation dynamically shuts down
        transmission at the target wavelengths (750/820 nm).
        """
        if solar_flux > self.solar_threshold:
            # Nonlinear suppression of transmission under high flux
            suppression_factor = 1.0 / (
                1.0 + OMIT_SUPPRESSION_RATE * (solar_flux - self.solar_threshold)
            )
            return float(baseline_transmission * suppression_factor)
        return float(baseline_transmission)
