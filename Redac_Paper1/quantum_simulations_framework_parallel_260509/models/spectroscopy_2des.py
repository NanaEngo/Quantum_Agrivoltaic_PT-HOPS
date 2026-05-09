import logging
import os
from datetime import datetime
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
from core.constants import (
    DEFAULT_SPECTRAL_RESOLUTION,
    DEFAULT_W_BUFFER,
    DEFAULT_DPI,
    PREVIEW_DPI,
    T_DECAY_DIAGONAL,
    T_DECAY_CROSS,
    SPECTROSCOPY_LINEWIDTH_SCALE,
    SPECTROSCOPY_CROSS_PEAK_AMP,
)

logger = logging.getLogger(__name__)


class Spectroscopy2DES:
    """
    Simulation of Two-Dimensional Electronic Spectroscopy (2DES) signals.

    Mathematical Framework:
    2DES signals S(ωτ, T, ωt) are calculated using the third-order response functions
    R^(3)(τ, T, t). The 2D spectrum at a fixed waiting time T is given by:

    S(ωτ, T, ωt) = Re ∫∫ dτ dt exp(iωτ τ + iωt t) Σ_i R_i(τ, T, t)

    This implementation uses a simplified excitonic model where peaks represent:
    1. Diagonal peaks: Absorption/Emission of individual sites
    2. Cross-peaks: Coupling and energy transfer between sites
    3. Oscillations: Coherent excitonic beats (if T is varied)
    """

    def __init__(self, system_size: int):
        self.system_size = system_size
        logger.info(f"Spectroscopy2DES initialized for {system_size} sites.")

    def simulate_2d_spectrum(
        self,
        hamiltonian: np.ndarray,
        waiting_time: float = 0.0,
        resolution: int = DEFAULT_SPECTRAL_RESOLUTION,
        damping: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Generates a 2D spectrum with realistic vibronic broadening.
        
        Parameters:
        - damping: Vibronic damping from Kleinekathöfer model (cm^-1)
        """
        energies, states = np.linalg.eigh(hamiltonian)
        
        # Enhanced resolution and realistic linewidth (Reviewer 2 Compliance)
        linewidth = damping * SPECTROSCOPY_LINEWIDTH_SCALE # Empirical broadening
        
        w_min = np.min(energies) - DEFAULT_W_BUFFER
        w_max = np.max(energies) + DEFAULT_W_BUFFER
        w_axis = np.linspace(w_min, w_max, resolution)
        W_tau, W_t = np.meshgrid(w_axis, w_axis)
        spectrum = np.zeros((resolution, resolution))

        # Diagonal & Cross-peaks with excitonic weighting
        for i, Ei in enumerate(energies):
            for j, Ej in enumerate(energies):
                # Transition strength based on eigenstate overlap (Simplified dipole proxy)
                dipole_strength = np.sum(np.abs(states[:, i])) * np.sum(np.abs(states[:, j]))
                
                if i == j:
                    # Diagonal peak
                    intensity = dipole_strength * np.exp(-waiting_time / T_DECAY_DIAGONAL)
                else:
                    # Cross-peak (Energy Transfer)
                    intensity = dipole_strength * SPECTROSCOPY_CROSS_PEAK_AMP * (1 - np.exp(-waiting_time / T_DECAY_CROSS))
                
                spectrum += intensity * np.exp(
                    -((W_tau - Ei) ** 2 + (W_t - Ej) ** 2) / (2 * linewidth**2)
                )

        return {
            "omega_exc": w_axis,
            "omega_det": w_axis,
            "spectrum": spectrum,
            "waiting_time": waiting_time,
            "eigenenergies": energies,
        }

    def plot_2d_spectrum(
        self,
        results: Dict[str, Any],
        output_dir: str = "../Graphics/",
        filename: str = "spectroscopy_2des",
    ) -> str:
        """
        Plots the 2D spectrum as a contour plot.
        """
        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(8, 7))
        plt.contourf(
            results["omega_exc"],
            results["omega_det"],
            results["spectrum"].T,
            50,
            cmap="nipy_spectral",
        )
        plt.colorbar(label="Signal Intensity (arb. units)")

        # Draw diagonal line
        plt.plot(results["omega_exc"], results["omega_exc"], "w--", alpha=0.5)

        plt.xlabel(r"Excitation Frequency $\omega_{\tau}$ (cm$^{-1}$)")
        plt.ylabel(r"Detection Frequency $\omega_t$ (cm$^{-1}$)")
        plt.title(f"2D Electronic Spectrum (T = {results['waiting_time']} fs)")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.pdf"
        filepath = os.path.join(output_dir, full_filename)

        plt.savefig(filepath, dpi=DEFAULT_DPI, bbox_inches="tight")
        
        png_filename = f"{filename}_{timestamp}.png"
        png_filepath = os.path.join(output_dir, png_filename)
        plt.savefig(png_filepath, dpi=PREVIEW_DPI, bbox_inches="tight")
        
        plt.close()

        logger.info(f"2DES plot saved to {filepath}")
        return filepath
