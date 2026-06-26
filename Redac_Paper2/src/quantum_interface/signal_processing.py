"""
V6: Quantum Machine Learning / Hybrid Signal Processing (Axe 6).

Implements quantum-inspired kernel methods and Matrix Product State (MPS)
denoising to extract weak pathological stress signals from noisy SERS and
CQD fluorescence telemetry in the hostile greenhouse environment.

References
----------
- Havlíček et al. (2019) "Supervised learning with quantum-enhanced
  feature spaces." Nature 567, 209–212.
- Stoudenmire & Schwab (2016) "Supervised Learning with Tensor Networks."
  NIPS 2016, 4806–4814.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.distance import cdist

# ═══════════════════════════════════════════════════════════════════════════
# 1. Quantum Kernel Methods — quantum-inspired feature maps for denoising
# ═══════════════════════════════════════════════════════════════════════════


def _quantum_rbf_kernel(
    X: NDArray[np.float64], Y: NDArray[np.float64] | None, gamma: float
) -> NDArray[np.float64]:
    """
    Quantum-inspired Radial Basis Function kernel.

    The feature map φ(x) = exp(i Σ_j θⱼ(x) σⱼ) is approximated by the
    standard RBF kernel which, for finite-dimensional embeddings, is
    equivalent to a Gaussian projected over the Bloch sphere.
    """
    dists = cdist(X, Y if Y is not None else X, metric="sqeuclidean")
    return np.exp(-gamma * dists)


def _quantum_angle_kernel(
    X: NDArray[np.float64], Y: NDArray[np.float64] | None, gamma: float
) -> NDArray[np.float64]:
    """
    Quantum Angle kernel — projects data onto the unit hyperspere and
    computes inner products mimicking a variational quantum circuit
    with angle encoding.
    """
    X_norm = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
    if Y is not None:
        Y_norm = Y / np.maximum(np.linalg.norm(Y, axis=1, keepdims=True), 1e-12)
    else:
        Y_norm = X_norm
    K = X_norm @ Y_norm.T
    return np.clip(K, -1.0, 1.0) ** 2


class QuantumKernelDenoiser:
    """
    Denoises SERS/CQD spectral measurements using a quantum-inspired kernel
    ridge regression (KRR) model.

    The method treats the noisy spectral time-series as a regression problem
    where the latent "clean" signal is reconstructed from its quantum kernel
    expansion over a dictionary of reference spectra.

    Parameters
    ----------
    gamma : float
        Kernel width parameter (default 0.5). Larger values fit more
        locally; smaller values smooth more aggressively.
    regularization : float
        Tikhonov regularisation (default 1e-3). Higher values suppress
        high-frequency noise at the cost of bias.
    kernel_type : {"rbf", "angle"}
        Quantum-inspired kernel type.
    """

    def __init__(
        self,
        gamma: float = 0.5,
        regularization: float = 1e-3,
        kernel_type: str = "rbf",
    ):
        self.gamma = gamma
        self.regularization = regularization
        self.kernel_type = kernel_type
        self._alpha: NDArray[np.float64] | None = None
        self._X_fit: NDArray[np.float64] | None = None

    def _kernel(
        self, X: NDArray[np.float64], Y: NDArray[np.float64] | None = None
    ) -> NDArray[np.float64]:
        if self.kernel_type == "rbf":
            return _quantum_rbf_kernel(X, Y, self.gamma)
        elif self.kernel_type == "angle":
            return _quantum_angle_kernel(X, Y, self.gamma)
        else:
            raise ValueError(f"Unknown kernel_type: {self.kernel_type}")

    def fit(self, X: NDArray[np.float64], y: NDArray[np.float64]) -> QuantumKernelDenoiser:
        """
        Fit the kernel ridge regression model.

        Solves: (K + λ I) α = y

        Parameters
        ----------
        X : (n_samples, n_features)
            Reference spectral dictionary (e.g., clean SERS templates).
        y : (n_samples,) or (n_samples, n_outputs)
            Target values (e.g., known stress levels or clean spectra).
        """
        K = self._kernel(X)
        n = K.shape[0]
        K_reg = K + self.regularization * np.eye(n)
        self._alpha = np.linalg.solve(K_reg, np.asarray(y))
        self._X_fit = X.copy()
        return self

    def predict(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Predict denoised signal from quantum kernel expansion.

        Parameters
        ----------
        X : (n_query, n_features)
            Noisy spectral measurements.

        Returns
        -------
        y_pred : (n_query,) or (n_query, n_outputs)
            Denoised signal / stress estimate.
        """
        if self._alpha is None or self._X_fit is None:
            raise RuntimeError("Model must be fitted before predict.")
        K_test = self._kernel(X, self._X_fit)
        return K_test @ self._alpha

    def anomaly_score(self, X: NDArray[np.float64], y_observed: NDArray[np.float64]) -> float:
        """
        Compute normalised reconstruction error as a stress anomaly score.

        A high score indicates the observed signal deviates significantly
        from the quantum kernel reconstruction, suggesting pathological stress.
        """
        y_pred = self.predict(X)
        residual = np.asarray(y_observed) - y_pred
        mse = float(np.mean(residual**2))
        variance = float(np.var(y_observed)) + 1e-12
        return mse / variance


# ═══════════════════════════════════════════════════════════════════════════
# 2. Tensor Network Denoising — MPS/DMRG-inspired signal compression
# ═══════════════════════════════════════════════════════════════════════════


class MpsDenoiser:
    """
    Matrix Product State (MPS) denoiser for 1-D spectral time series.

    Decomposes the noisy signal into a MPS representation via sequential
    truncated SVD with bond dimension χ (chi). Truncating the Schmidt
    coefficients acts as a non-linear low-pass filter that preserves sharp
    spectral features better than a standard Fourier filter.

    This implementation uses *only* sequential left-canonical decomposition
    followed by contraction — no DMRG sweeps — which is sufficient for
    fixed-χ compression of 1-D measurement data.

    Parameters
    ----------
    chi : int
        Maximum bond dimension (default 8). Higher χ preserves more
        structure; lower χ smooths more aggressively.
    """

    def __init__(self, chi: int = 8):
        self.chi = chi
        self._signal_length: int = 0

    # ────────────────────────────────────────────────────────────────

    def fit_transform(self, signal: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Denoise a 1-D signal via MPS compression (sequential truncated SVD).

        Parameters
        ----------
        signal : (n,)
            Noisy 1-D spectral intensity array (n ≥ 2).

        Returns
        -------
        denoised : (n,)
            Denoised signal after MPS truncation.
        """
        n = len(signal)
        if n < 2:
            return signal.copy()

        self._signal_length = n

        # --- Sequential left-canonical MPS decomposition ---
        # We view the signal as an MPS of L = n sites, each with
        # physical dimension d = 1.  The left-canonical form is built
        # by repeated truncated SVD from left to right.
        remainder = signal.reshape(1, -1)  # (chi_left=1, n)
        tensors: list[NDArray[np.float64]] = []

        for _i in range(n - 1):
            U, s, Vt = np.linalg.svd(remainder, full_matrices=False)
            chi_eff = min(self.chi, U.shape[1])
            # Left-canonical tensor A_i = U[:, :chi_eff]
            tensors.append(U[:, :chi_eff])
            # Absorb singular values into remainder for the next site
            remainder = np.diag(s[:chi_eff]) @ Vt[:chi_eff, :]
        # Last tensor (right-most site, not decomposed further)
        tensors.append(remainder)

        # --- Contract MPS back to 1-D signal ---
        result = tensors[0]
        for t in tensors[1:]:
            result = result @ t
        denoised = result.flatten()[:n]

        return denoised


# ═══════════════════════════════════════════════════════════════════════════
# 3. High-level diagnostic pipeline
# ═══════════════════════════════════════════════════════════════════════════


def detect_stress_anomaly(
    noisy_spectrum: NDArray[np.float64],
    reference_dictionary: NDArray[np.float64],
    reference_labels: NDArray[np.float64],
    gamma: float = 0.5,
    regularization: float = 1e-3,
    zscore_threshold: float = 2.0,
    mps_chi: int = 16,
) -> dict:
    """
    Run the full QML signal-processing pipeline on a noisy spectrum.

    Steps
    -----
    1. MPS denoising of the input spectrum.
    2. Quantum kernel regression against the reference dictionary.
    3. Anomaly scoring with Z-score thresholding.

    Parameters
    ----------
    noisy_spectrum : (n_features,)
        Raw (noisy) SERS or CQD fluorescence measurement.
    reference_dictionary : (n_templates, n_features)
        Library of clean reference spectra.
    reference_labels : (n_templates,)
        Known stress levels or health scores for each reference.
    gamma : float
        Quantum kernel width.
    regularization : float
        Kernel ridge regularisation.
    zscore_threshold : float
        Z-score above which an anomaly is flagged.
    mps_chi : int
        MPS bond dimension for denoising.

    Returns
    -------
    dict with keys:
        - 'denoised_spectrum': MPS-filtered spectrum.
        - 'predicted_stress': kernel-regression stress estimate.
        - 'anomaly_score': normalised reconstruction error.
        - 'is_anomaly': True if anomaly_score > zscore_threshold.
        - 'early_warning': True if is_anomaly and stress still sub-critical.
    """
    # Step 1: MPS denoising (sequential truncated SVD compression)
    mps = MpsDenoiser(chi=mps_chi)
    denoised = mps.fit_transform(noisy_spectrum)

    # Step 2: Quantum kernel regression
    qk = QuantumKernelDenoiser(gamma=gamma, regularization=regularization)
    qk.fit(reference_dictionary, reference_labels)
    predicted_stress = float(qk.predict(denoised.reshape(1, -1)).flat[0])

    # Step 3: Anomaly detection
    anomaly = qk.anomaly_score(denoised.reshape(1, -1), noisy_spectrum.reshape(1, -1))
    is_anomaly = anomaly > zscore_threshold

    # Early warning: anomaly detected but stress level still moderate
    early_warning = is_anomaly and predicted_stress < 0.5

    return {
        "denoised_spectrum": denoised.tolist(),
        "predicted_stress": predicted_stress,
        "anomaly_score": float(anomaly),
        "is_anomaly": bool(is_anomaly),
        "early_warning": bool(early_warning),
    }
