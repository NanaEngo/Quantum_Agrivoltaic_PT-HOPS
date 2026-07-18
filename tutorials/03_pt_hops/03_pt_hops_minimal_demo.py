"""03_pt_hops_minimal_demo.py
A pedagogical, simplified PT-HOPS style demo for teaching purposes.
This is NOT a production-grade HOPS implementation. It demonstrates colored noise
and ensemble averaging for a toy two-level system.
"""

import numpy as np
import matplotlib.pyplot as plt

# Pauli matrices
sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
H_sys = 0.5 * sigma_x  # simple coherent drive


def drude_correlation(t, lam, gamma, beta=1.0):
    """Pedagogical Drude-like correlator (classical approx)."""
    return lam * gamma * np.exp(-gamma * t)


def generate_colored_noise(dt, n_steps, lam, gamma):
    """Generate a demonstrative complex Ornstein-Uhlenbeck process."""
    x = np.zeros(n_steps, dtype=complex)
    # white noise increments (complex)
    xi = (np.random.normal(size=n_steps) + 1j * np.random.normal(size=n_steps)) / np.sqrt(2.0)
    tau = 1.0 / gamma
    # scale for discrete-time OU
    for i in range(1, n_steps):
        expf = np.exp(-dt / tau)
        var_factor = np.sqrt((1.0 - np.exp(-2.0 * dt / tau)) / 2.0)
        x[i] = x[i - 1] * expf + var_factor * xi[i]
    return x


def rk4_step(psi, dt, H_eff, noise_term):
    k1 = -1j * (H_eff @ psi + noise_term)
    k2 = -1j * (H_eff @ (psi + 0.5 * dt * k1) + noise_term)
    k3 = -1j * (H_eff @ (psi + 0.5 * dt * k2) + noise_term)
    k4 = -1j * (H_eff @ (psi + dt * k3) + noise_term)
    return psi + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def run_trajectory(T=10.0, dt=0.01, lam=0.2, gamma=1.0):
    n_steps = int(T / dt)
    times = np.linspace(0.0, T, n_steps)
    psi = np.array([1.0, 0.0], dtype=complex)  # initial state |0>
    traj = np.zeros((n_steps, 2), dtype=complex)
    noise = generate_colored_noise(dt, n_steps, lam, gamma)
    H_eff = H_sys
    for i in range(n_steps):
        # couple noise through sigma_z
        noise_term = noise[i] * (sigma_z @ psi)
        psi = rk4_step(psi, dt, H_eff, noise_term)
        # normalize for stability
        psi = psi / np.linalg.norm(psi)
        traj[i] = psi
    return times, traj


def main():
    n_traj = 60
    T = 10.0
    dt = 0.005
    lam = 0.2
    gamma = 1.0

    times, _ = run_trajectory(T=T, dt=dt, lam=lam, gamma=gamma)
    pop = np.zeros(times.size)

    for j in range(n_traj):
        _, traj = run_trajectory(T=T, dt=dt, lam=lam, gamma=gamma)
        pop += np.abs(traj[:, 0]) ** 2

    pop /= float(n_traj)

    plt.figure(figsize=(8, 4))
    plt.plot(times, pop, label=f'n_traj={n_traj}')
    plt.xlabel('Time')
    plt.ylabel('Population |0><0|')
    plt.title('Toy PT-HOPS style trajectories (pedagogical)')
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
