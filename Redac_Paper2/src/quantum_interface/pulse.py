import numpy as np

from ..config_loader import ConfigModel
from ..constants import EV_TO_CM1, FLOQUET_SITES, FMO_NSITES, OMIT_I_SAT_W_M2


class FloquetStarkSwitch:
    """
    Flux-dependent photoprotection for the OPV-FMO interface.

    Two coordinated responses share one hysteresis latch:

    1. Floquet Stark detuning of the FMO site transitions above threshold.
    2. Flux-dependent OPTICAL LIMITING of the 750/820 nm passbands: the NPoM
       picocavity saturates under strong drive, so transmission follows
       T = T0 / (1 + I / I_sat). This is optical limiting (a *reduction* of
       passband transmission with flux), NOT optomechanically induced
       transparency, which would open a transmission window.

    Hysteresis: the latch engages when solar_flux > solar_threshold (850 W/m2),
    stays engaged while solar_flux > release_threshold (750 W/m2), and releases
    at or below 750 W/m2 (dead band 750-850 W/m2). Zero flux (night mode)
    resets the latch to the off state.

    Statelessness: the latch is instance state, so a call *sequence* on one
    instance is assumed (monotone time order). Both methods are safe to call
    back-to-back: each call re-evaluates the latch from its own flux reading,
    and neither method mutates anything else.
    """

    def __init__(self, config: ConfigModel):
        self.config = config
        self.solar_threshold = config.simulation.solar_flux_threshold
        self.release_threshold = getattr(config.simulation, "solar_flux_release", 750.0)
        self.amplitude = config.quantum.floquet.driving_amplitude
        self.frequency = config.quantum.floquet.driving_frequency
        self._switch_latched = False

    def _update_latch(self, solar_flux: float) -> bool:
        """Engage above threshold, hold down to release threshold, reset at night."""
        if solar_flux <= 0.0:
            self._switch_latched = False
        elif solar_flux > self.solar_threshold:
            self._switch_latched = True
        elif solar_flux <= self.release_threshold:
            self._switch_latched = False
        # in the dead band (release < flux <= threshold): hold current state
        return self._switch_latched

    def get_stark_detuning(self, solar_flux: float, time_ps: float) -> np.ndarray:
        """
        Calculates a time-dependent diagonal energy shift matrix for the FMO site transitions.
        When the hysteresis latch is engaged (flux > 850 W/m2, held down to 750 W/m2),
        it detunes the energy levels using a time-dependent driving field
        V(t)*cos(omega*t) in the Floquet picture. At zero solar flux (night mode)
        the latch resets and a zero shift matrix is returned.
        """
        shift_matrix = np.zeros((FMO_NSITES, FMO_NSITES), dtype=complex)
        if self._update_latch(solar_flux):
            # Shift primary optical absorption site energies (Site 1 & 6, index 0 and 5)
            # using the Floquet driving envelope
            # driving_amplitude is in eV (parameters.yaml); H is in cm^-1
            detuning_val = self.amplitude * EV_TO_CM1 * np.cos(self.frequency * time_ps)
            for site in FLOQUET_SITES:
                shift_matrix[site, site] = detuning_val

        return shift_matrix

    def apply_optical_limiting(self, solar_flux: float, baseline_transmission: float) -> float:
        """
        Flux-dependent optical limiting of the 750/820 nm passbands (NPoM
        picocavity saturation), NOT optomechanically induced transparency.

        When the hysteresis latch is engaged (flux > 850 W/m2, held down to
        750 W/m2), transmission follows the saturation law
        T = T0 / (1 + I / I_sat) with I_sat = 800 W/m2, i.e. 0.444 * T0 at
        1000 W/m2. Below the release threshold T = T0 (and T = T0 at zero flux).
        Shares the instance latch with get_stark_detuning(); assumes calls are
        made in sequence on the same instance.
        """
        if self._update_latch(solar_flux):
            suppression_factor = 1.0 / (1.0 + solar_flux / OMIT_I_SAT_W_M2)
            return float(baseline_transmission * suppression_factor)
        return float(baseline_transmission)

    # Backwards-compatible alias (pre-2026-09 name)
    apply_omit_attenuation = apply_optical_limiting
