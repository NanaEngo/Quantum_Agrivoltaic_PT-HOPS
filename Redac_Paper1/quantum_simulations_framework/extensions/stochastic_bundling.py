import logging
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class StochasticBundle:
    """
    Represents a group of environmental frequency modes (poles) bundled together
    for Stochastically Bundled Dissipators (SBD).
    """

    bundle_id: int
    center_frequency: float
    effective_coupling: float
    modes: List[Tuple[float, float]]  # List of (frequency, coupling_strength)
    variance: float


class StochasticallyBundledDissipator:
    """
    Implements the Stochastically Bundled Dissipators (SBD) logic.
    Instead of associating a hierarchy index with each individual mode,
    this class aggregates correlation function poles into distinct bundles.
    """

    def __init__(self, n_bundles: int = 5):
        self.n_bundles = n_bundles
        self.bundles: List[StochasticBundle] = []
        logger.info(f"Initialized StochasticallyBundledDissipator with {n_bundles} bundles.")

    def discretize_spectral_density(self, modes: List[Tuple[float, float]]) -> List[StochasticBundle]:
        """
        Groups explicit environmental modes into clustered bundles using a basic
        K-Means 1D approach based on frequency proximity and weighted by coupling strength.
        """
        if not modes:
            return []

        # Reset bundles on each call to prevent accumulation across repeated calls
        self.bundles = []

        frequencies = np.array([m[0] for m in modes])
        couplings = np.array([m[1] for m in modes])

        # If we have fewer modes than requested bundles, just return individual bundles
        if len(modes) <= self.n_bundles:
            for i, mode in enumerate(modes):
                bundle = StochasticBundle(
                    bundle_id=i,
                    center_frequency=mode[0],
                    effective_coupling=abs(mode[1]),  # use magnitude for physical coupling
                    modes=[mode],
                    variance=0.0,
                )
                self.bundles.append(bundle)
            return self.bundles

        # Very simple 1D clustering (uniform bins for this structural demonstration)
        min_freq, max_freq = np.min(frequencies), np.max(frequencies)
        bin_edges = np.linspace(min_freq, max_freq * (1 + 1e-9) + 1e-5, self.n_bundles + 1)

        for i in range(self.n_bundles):
            # Find modes in this bin
            mask = (frequencies >= bin_edges[i]) & (frequencies < bin_edges[i + 1])
            bin_modes = [modes[j] for j in range(len(modes)) if mask[j]]

            if not bin_modes:
                continue

            bin_freqs = np.array([m[0] for m in bin_modes])
            bin_coups = np.array([m[1] for m in bin_modes])
            bin_coups_abs = np.abs(bin_coups)

            # Weighted center frequency (by |coupling|)
            total_coupling = np.sum(bin_coups_abs)
            center_freq = (np.sum(bin_freqs * bin_coups_abs) / total_coupling
                           if total_coupling > 0 else np.mean(bin_freqs))

            variance = np.var(bin_freqs)

            # Effective coupling: sum of magnitudes (physically: total bath coupling strength)
            effective_coupling = float(np.sum(bin_coups_abs))

            bundle = StochasticBundle(
                bundle_id=i,
                center_frequency=center_freq,
                effective_coupling=effective_coupling,
                modes=bin_modes,
                variance=variance,
            )
            self.bundles.append(bundle)

        logger.info(
            f"Successfully bundled {len(modes)} explicit modes into {len(self.bundles)} SBD bundles."
        )
        return self.bundles

    def get_bundle_parameters(self) -> Tuple[List[float], List[float]]:
        """
        Returns the effective frequencies and couplings for the bundles,
        which can be fed directly back into reduced HOPS or PT-HOPS equations.
        """
        freqs = [b.center_frequency for b in self.bundles]
        coups = [b.effective_coupling for b in self.bundles]
        return freqs, coups
