import logging
import numpy as np
import scipy.linalg as la
from typing import List, Optional, Dict, Any, Union
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

class QuantumAnalysisSuite:
    """
    Suite of analysis methods for quantum dynamics simulations.
    Provides methods to calculate coherence, entanglement, ETR, and other quantum metrics.
    """

    @staticmethod
    def calculate_etr(populations: NDArray[np.float64], time_points: NDArray[np.float64]) -> float:
        """
        Calculate the Electron Transfer Rate (ETR) from population dynamics.

        Parameters
        ----------
        populations : np.ndarray (n_times, n_sites)
            Site populations from simulation.
        time_points : np.ndarray
            Corresponding time points in fs.

        Returns
        -------
        etr : float
            Estimated energy transfer rate in ps^-1.
        """
        pop_site1 = populations[:, 0]
        transferred = 1.0 - pop_site1

        idx_half = np.argmax(transferred >= 0.5)
        if idx_half > 0 and transferred[idx_half] >= 0.5:
            t_half = time_points[idx_half]  # fs
            etr = float(np.log(2) / (t_half * 1e-3))  # ps^-1
        else:
            n_fit = min(20, len(time_points))
            if n_fit > 2:
                coeffs = np.polyfit(time_points[:n_fit], transferred[:n_fit], 1)
                rate_fs = coeffs[0]  # transfer per fs
                etr = float(rate_fs * 1e3)  # ps^-1
            else:
                etr = 0.0

        return etr

    @staticmethod
    def calculate_coherence_measure(density_matrix: NDArray[np.complex128]) -> float:
        """
        Calculate the l1-norm of coherence for a density matrix.
        C_l1(rho) = sum_{i!=j} |rho_{ij}|
        """
        n = density_matrix.shape[0]
        coherence = 0.0
        for i in range(n):
            for j in range(n):
                if i != j:
                    coherence += np.abs(density_matrix[i, j])
        return float(coherence)

    @staticmethod
    def calculate_qfi(rho: NDArray[np.complex128], H: NDArray[np.float64]) -> float:
        """Calculate the Quantum Fisher Information (QFI)."""
        eigenvals, eigenvecs = np.linalg.eigh(rho)
        eigenvals = np.real(eigenvals)

        qfi = 0.0
        n = len(eigenvals)
        for i in range(n):
            for j in range(n):
                denom = eigenvals[i] + eigenvals[j]
                if denom > 1e-12:
                    H_ij = np.abs(eigenvecs[:, i].conj() @ H @ eigenvecs[:, j]) ** 2
                    qfi += 2.0 * (eigenvals[i] - eigenvals[j]) ** 2 / denom * H_ij

        return float(np.real(qfi))

    @staticmethod
    def calculate_entropy_von_neumann(rho: NDArray[np.complex128]) -> float:
        """Calculate the von Neumann entropy of a quantum state."""
        eigenvals = np.linalg.eigvals(rho)
        eigenvals = np.real(eigenvals)
        eigenvals = np.clip(eigenvals, a_min=1e-12, a_max=None)
        entropy = -np.sum(eigenvals * np.log(eigenvals))
        return float(entropy)

    @staticmethod
    def calculate_purity(rho: NDArray[np.complex128]) -> float:
        """Calculate the purity of a quantum state: tr(rho^2)."""
        purity = np.real(np.trace(rho @ rho))
        return float(purity)

    @classmethod
    def calculate_linear_entropy(cls, rho: NDArray[np.complex128]) -> float:
        """Calculate the linear entropy of a quantum state: 1 - tr(rho^2)."""
        return 1.0 - cls.calculate_purity(rho)

    @staticmethod
    def calculate_ipr(rho: NDArray[np.complex128]) -> float:
        """Calculate the Inverse Participation Ratio (IPR)."""
        diag = np.real(np.diag(rho))
        sum_sq = np.sum(diag ** 2)
        return float(1.0 / sum_sq if sum_sq > 1e-12 else 1.0)

    @classmethod
    def calculate_concurrence(cls, rho: NDArray[np.complex128]) -> float:
        """Calculate the concurrence of a quantum state (for 2-qubit systems)."""
        n = rho.shape[0]

        if n < 2:
            return 0.0

        if n > 2:
            total_concurrence = 0.0
            n_pairs = 0
            for i in range(n):
                for j in range(i + 1, n):
                    rho_ij = np.zeros((2, 2), dtype=complex)
                    rho_ij[0, 0] = rho[i, i]
                    rho_ij[0, 1] = rho[i, j]
                    rho_ij[1, 0] = rho[j, i]
                    rho_ij[1, 1] = rho[j, j]
                    pair_concurrence = cls._calculate_2x2_concurrence(rho_ij)
                    total_concurrence += pair_concurrence
                    n_pairs += 1
            return float(total_concurrence / n_pairs if n_pairs > 0 else 0.0)
        else:
            return float(cls._calculate_2x2_concurrence(rho))

    @staticmethod
    def _calculate_2x2_concurrence(rho: NDArray[np.complex128]) -> float:
        """Helper to calculate concurrence for a 2x2 density matrix."""
        sigma_y = np.array([[0, -1j], [1j, 0]])
        rho_tilde = np.kron(sigma_y, sigma_y) @ rho.conj() @ np.kron(sigma_y, sigma_y)
        R = la.sqrtm(rho @ rho_tilde)
        evals = np.linalg.eigvals(R)
        evals = np.sort(np.real(evals))[::-1]
        c = max(0, evals[0] - evals[1] - evals[2] - evals[3])
        return float(c)

    @classmethod
    def calculate_bipartite_entanglement(cls, rho: NDArray[np.complex128], partition: Optional[List[int]] = None) -> float:
        """Calculate bipartite entanglement using von Neumann entropy of reduced density matrix."""
        n = rho.shape[0]

        if partition is None:
            partition = list(range(n // 2))

        if len(partition) == 0 or len(partition) == n:
            return 0.0

        reduced_rho = np.zeros((len(partition), len(partition)), dtype=complex)
        for i, idx_i in enumerate(partition):
            for j, idx_j in enumerate(partition):
                reduced_rho[i, j] = rho[idx_i, idx_j]

        trace = np.trace(reduced_rho)
        if trace > 0:
            reduced_rho = reduced_rho / trace
        else:
            return 0.0

        return cls.calculate_entropy_von_neumann(reduced_rho)

    @classmethod
    def calculate_multipartite_entanglement(cls, rho: NDArray[np.complex128]) -> float:
        """Calculate multipartite entanglement measure."""
        n = rho.shape[0]
        if n < 2:
            return 0.0

        total_entanglement = 0.0
        n_partitions = 0
        for i in range(1, min(n, 6)):
            partition = list(range(i))
            ent = cls.calculate_bipartite_entanglement(rho, partition)
            total_entanglement += ent
            n_partitions += 1

        return float(total_entanglement / n_partitions if n_partitions > 0 else 0.0)

    @classmethod
    def calculate_pairwise_concurrence(cls, rho: NDArray[np.complex128]) -> float:
        """Calculate average pairwise concurrence across all pairs of sites."""
        n = rho.shape[0]
        if n < 2:
            return 0.0

        total_concurrence = 0.0
        n_pairs = 0
        for i in range(n):
            for j in range(i + 1, n):
                rho_ij = np.zeros((2, 2), dtype=complex)
                rho_ij[0, 0] = rho[i, i]
                rho_ij[0, 1] = rho[i, j]
                rho_ij[1, 0] = rho[j, i]
                rho_ij[1, 1] = rho[j, j]
                pair_concurrence = cls._calculate_2x2_concurrence(rho_ij)
                total_concurrence += pair_concurrence
                n_pairs += 1

        return float(total_concurrence / n_pairs if n_pairs > 0 else 0.0)

    @staticmethod
    def calculate_quantum_synergy_index(rho_opv: NDArray[np.complex128], rho_psu: NDArray[np.complex128]) -> float:
        """Calculate quantum synergy index between OPV and photosynthetic system."""
        numerator = np.trace(rho_opv @ rho_psu) - np.trace(rho_opv) * np.trace(rho_psu)
        denominator = np.linalg.norm(rho_opv) * np.linalg.norm(rho_psu)
        synergy = numerator / denominator if denominator != 0 else 0.0
        return float(np.real(synergy))

    @staticmethod
    def calculate_mandel_q_parameter(vibrational_mode_occupations: NDArray[np.float64]) -> float:
        """Calculate Mandel Q parameter for vibrational mode non-classicality."""
        mean_occ = np.mean(vibrational_mode_occupations)
        if mean_occ < 1e-12:
            return 0.0
        variance = np.var(vibrational_mode_occupations)
        return float((variance - mean_occ) / mean_occ)

    @staticmethod
    def calculate_fidelity(rho: NDArray[np.complex128], sigma: NDArray[np.complex128]) -> float:
        """Calculate quantum fidelity between two states."""
        try:
            sqrt_rho = la.sqrtm(rho)
            matrix = sqrt_rho @ sigma @ sqrt_rho
            return float(np.real(np.trace(la.sqrtm(matrix))) ** 2)
        except (np.linalg.LinAlgError, ValueError, TypeError) as e:
            logger.debug(f"Fidelity calculation fallback due to: {e}")
            return float(np.real(np.trace(rho @ sigma)))

    @classmethod
    def calculate_quantum_discord(cls, rho: NDArray[np.complex128]) -> float:
        """Simplified measure of quantum correlations beyond entanglement (Quantum Discord)."""
        s_total = cls.calculate_entropy_von_neumann(rho)
        diag = np.diag(rho).real
        p_others = diag[1:]
        p_others_sum = np.sum(p_others)
        if p_others_sum < 1e-12:
            return 0.0
        p_others /= p_others_sum
        s_others = -np.sum(p_others * np.log(p_others + 1e-15))
        return float(max(0.0, s_others - s_total))

    @staticmethod
    def stochastically_bundled_dissipators(rho: NDArray[np.complex128], l_bundled: List[NDArray[np.complex128]], p_alpha: List[float]) -> NDArray[np.complex128]:
        """Implement Stochastically Bundled Dissipators (SBD)."""
        d_rho = np.zeros_like(rho, dtype=complex)
        for L, p in zip(l_bundled, p_alpha):
            if p > 0:
                L_dag = L.conj().T
                d_rho += p * (L @ rho @ L_dag - 0.5 * (L_dag @ L @ rho + rho @ L_dag @ L))
        return d_rho

    @staticmethod
    def spectral_density_drude_lorentz(omega: Union[float, NDArray[np.float64]], lambda_reorg: float, gamma: float) -> Union[float, NDArray[np.float64]]:
        """Drude-Lorentz spectral density J(omega) = (2 * lambda * gamma * omega) / (omega^2 + gamma^2)."""
        omega_arr = np.asarray(omega)
        J = (2 * lambda_reorg * gamma * omega_arr) / (omega_arr**2 + gamma**2)
        if np.isscalar(omega):
            return 0.0 if omega == 0 else float(J)
        J[omega_arr == 0] = 0
        return J

    @staticmethod
    def spectral_density_vibronic(omega: Union[float, NDArray[np.float64]], omega_mode: float, lambda_mode: float, gamma_mode: float) -> Union[float, NDArray[np.float64]]:
        """Underdamped vibronic mode spectral density."""
        omega_arr = np.asarray(omega)
        numerator = 2 * lambda_mode * omega_mode * gamma_mode * omega_arr
        denominator = (omega_arr**2 - omega_mode**2)**2 + omega_arr**2 * gamma_mode**2
        J = numerator / denominator
        if np.isscalar(omega):
            return 0.0 if omega == 0 else float(J)
        J[omega_arr == 0] = 0
        return J

    @staticmethod
    def spectral_density_total(omega: Union[float, NDArray[np.float64]], lambda_reorg: float, gamma: float, vibronic_modes: Optional[List[Dict[str, float]]] = None) -> Union[float, NDArray[np.float64]]:
        """Total spectral density combining Drude-Lorentz and vibronic modes."""
        J_total = QuantumAnalysisSuite.spectral_density_drude_lorentz(omega, lambda_reorg, gamma)
        if vibronic_modes:
            for mode in vibronic_modes:
                J_total += QuantumAnalysisSuite.spectral_density_vibronic(omega, mode['omega'], mode['lambda'], mode['gamma'])
        return J_total
