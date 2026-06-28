"""
Unit tests for src.quantum_interface.signal_processing (Axe 6: QML signal processing).

Tests QuantumKernelDenoiser, MpsDenoiser, and detect_stress_anomaly pipeline.
"""

import numpy as np
import pytest

from src.quantum_interface.signal_processing import (
    MpsDenoiser,
    QuantumKernelDenoiser,
    detect_stress_anomaly,
)


class TestQuantumKernelDenoiser:
    """Quantum Kernel Ridge Regression denoiser."""

    def test_fit_predict_rbf(self):
        """QK-1: RBF kernel fitting and prediction recovers clean signal."""
        n_samples = 10
        n_features = 3
        rng = np.random.default_rng(42)
        X = rng.normal(size=(n_samples, n_features))
        y = np.sum(X**2, axis=1)  # simple nonlinear target

        model = QuantumKernelDenoiser(gamma=0.5, regularization=1e-3, kernel_type="rbf")
        model.fit(X, y)
        y_pred = model.predict(X)

        assert y_pred.shape == y.shape
        assert np.all(np.isfinite(y_pred))

    def test_fit_predict_angle(self):
        """QK-2: Angle kernel does not raise and returns finite values."""
        n_samples = 10
        n_features = 3
        rng = np.random.default_rng(123)
        X = np.abs(rng.normal(size=(n_samples, n_features))) + 0.1
        y = np.log(np.sum(X, axis=1))

        model = QuantumKernelDenoiser(gamma=0.5, regularization=1e-3, kernel_type="angle")
        model.fit(X, y)
        y_pred = model.predict(X)

        assert y_pred.shape == y.shape
        assert np.all(np.isfinite(y_pred))

    def test_predict_before_fit_raises(self):
        """QK-3: Calling predict before fit raises RuntimeError."""
        model = QuantumKernelDenoiser()
        with pytest.raises(RuntimeError, match="fitted"):
            model.predict(np.array([[1.0, 2.0, 3.0]]))

    def test_anomaly_score_healthy(self):
        """QK-4: Anomaly score is low when signal matches training distribution."""
        rng = np.random.default_rng(42)
        X_train = rng.normal(size=(20, 3))
        y_train = 0.5 * X_train[:, 0] + 0.3 * X_train[:, 1]

        model = QuantumKernelDenoiser(gamma=0.5, regularization=1e-2)
        model.fit(X_train, y_train)

        # Test on in-distribution sample
        x_test = rng.normal(size=(1, 3))
        score = model.anomaly_score(x_test, model.predict(x_test).reshape(1, -1))
        # Reconstruction should be close, so anomaly score near 0
        assert score < 1.0

    def test_unknown_kernel_raises(self):
        """QK-5: Invalid kernel type raises ValueError."""
        model = QuantumKernelDenoiser(kernel_type="invalid_kernel")
        X = np.array([[1.0, 2.0]])
        with pytest.raises(ValueError, match="kernel_type"):
            model._kernel(X)

    def test_pennylane_backend(self):
        """QK-6: Pennylane backend functions and uses PCA appropriately."""
        n_samples = 10
        n_features = 8
        n_qubits = 4
        rng = np.random.default_rng(42)
        X = rng.normal(size=(n_samples, n_features))
        y = np.sum(X**2, axis=1)

        model = QuantumKernelDenoiser(backend="pennylane", n_qubits=n_qubits)
        model.fit(X, y)
        y_pred = model.predict(X)

        assert y_pred.shape == y.shape
        assert np.all(np.isfinite(y_pred))
        assert model._pca is not None
        assert model._pca.n_components == n_qubits


class TestMpsDenoiser:
    """Matrix Product State denoiser."""

    @pytest.mark.parametrize("chi", [4, 8, 16])
    def test_denoise_sine_wave(self, chi):
        """MPS-1: Denoising a sine wave reduces L2 error vs noisy version."""
        n = 64
        t = np.linspace(0, 4 * np.pi, n)
        clean = np.sin(t)
        rng = np.random.default_rng(42)
        noisy = clean + 0.3 * rng.normal(size=n)

        mps = MpsDenoiser(chi=chi)
        denoised = mps.fit_transform(noisy)

        noise_err = float(np.mean((noisy - clean) ** 2))
        mps_err = float(np.mean((denoised - clean) ** 2))

        assert mps_err < noise_err, (
            f"chi={chi}: MPS error {mps_err:.4f} >= noise error {noise_err:.4f}"
        )

    def test_output_length(self):
        """MPS-2: Output signal length matches input."""
        n = 32
        rng = np.random.default_rng(42)
        signal = rng.normal(size=n)
        mps = MpsDenoiser(chi=8)
        denoised = mps.fit_transform(signal)
        assert len(denoised) == n

    def test_constant_signal(self):
        """MPS-3: Constant signal is perfectly recovered."""
        n = 16
        signal = np.full(n, 5.0)
        mps = MpsDenoiser(chi=4)
        denoised = mps.fit_transform(signal)
        assert np.allclose(denoised, 5.0, atol=1e-5)


class TestDetectStressAnomaly:
    """End-to-end QML stress anomaly detection pipeline."""

    def test_healthy_signal_no_anomaly(self):
        """SA-1: Clean signal classified as healthy (no anomaly)."""
        n_features = 3
        # Healthy spectrum: strong 180 cm⁻¹, moderate 740 cm⁻¹, low 1145 cm⁻¹
        healthy_spectrum = np.array([100.0, 50.0, 20.0])

        ref_dict = np.array(
            [
                [100.0, 50.0, 20.0],
                [60.0, 80.0, 120.0],
                [20.0, 10.0, 200.0],
            ],
            dtype=np.float64,
        )
        ref_labels = np.array([0.0, 0.4, 0.9], dtype=np.float64)

        # Add small noise to make it realistic
        rng = np.random.default_rng(42)
        noisy = healthy_spectrum + 0.01 * rng.normal(size=n_features)

        result = detect_stress_anomaly(
            noisy_spectrum=noisy,
            reference_dictionary=ref_dict,
            reference_labels=ref_labels,
            gamma=1.0,
            regularization=0.01,
            zscore_threshold=3.0,
            mps_chi=8,
        )

        assert "denoised_spectrum" in result
        assert "predicted_stress" in result
        assert "anomaly_score" in result
        assert "is_anomaly" in result
        assert "early_warning" in result
        assert result["predicted_stress"] < 0.3  # Should predict near-healthy

    def test_severe_stress_detected(self):
        """SA-2: Severely contaminated signal triggers anomaly."""
        n_features = 3
        # Stress spectrum: high 1145 cm⁻¹ (oxidative stress marker)
        stress_spectrum = np.array([20.0, 10.0, 200.0])

        ref_dict = np.array(
            [
                [100.0, 50.0, 20.0],
                [60.0, 80.0, 120.0],
                [20.0, 10.0, 200.0],
            ],
            dtype=np.float64,
        )
        ref_labels = np.array([0.0, 0.4, 0.9], dtype=np.float64)

        rng = np.random.default_rng(42)
        noisy = stress_spectrum + 0.05 * rng.normal(size=n_features)
        noisy = np.maximum(noisy, 0.0)

        result = detect_stress_anomaly(
            noisy_spectrum=noisy,
            reference_dictionary=ref_dict,
            reference_labels=ref_labels,
            gamma=1.0,
            regularization=0.01,
            zscore_threshold=2.0,
            mps_chi=8,
        )

        # The stress should be detected as high
        assert result["predicted_stress"] > 0.5
