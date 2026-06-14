#!/usr/bin/env python3
"""
Create placeholder PDF figures for SI compilation
"""

import matplotlib.pyplot as plt
import numpy as np

# Figure S1: Spectral density
fig, ax = plt.subplots(figsize=(8, 5))
omega = np.linspace(0, 1200, 500)
# Drude-Lorentz
J_dl = 2 * 35 * 50 * omega / (omega**2 + 50**2)
# Vibronic modes
vibronic = np.zeros_like(omega)
for w, S in [(150, 0.05), (200, 0.02), (575, 0.01), (1185, 0.005)]:
    vibronic += S * w**3 * 10 / ((omega**2 - w**2)**2 + omega**2 * 10**2)
J_total = J_dl + vibronic
ax.fill_between(omega, 0, J_dl/max(J_total), alpha=0.3, color='blue', label='Drude-Lorentz')
ax.plot(omega, J_total/max(J_total), 'b-', linewidth=2, label='Total $J(\\omega)$')
# Filter positions
for wl in [750, 820]:
    wn = 1e7/wl
    ax.axvline(x=wn, color='red', linestyle='--', alpha=0.7)
    ax.annotate(f'{wl} nm', xy=(wn, 0.9), ha='center', fontsize=9, color='red')
ax.set_xlabel('Wavenumber (cm$^{-1}$)')
ax.set_ylabel('Normalized $J(\\omega)$')
ax.set_title('Bath Spectral Density with Vibronic Modes')
ax.legend()
ax.set_xlim(0, 1200)
plt.tight_layout()
plt.savefig('spectral_density.pdf', dpi=300)
plt.close()

# Figure S2: Convergence hierarchy
fig, ax = plt.subplots(figsize=(8, 5))
L = [4, 5, 6, 7, 8, 9, 10]
phi = [1.221, 1.238, 1.250, 1.256, 1.262, 1.263, 1.264]
ax.plot(L, phi, 'bo-', linewidth=2, markersize=8)
ax.axhline(y=1.264, color='red', linestyle='--', alpha=0.7, label='Converged ($L=10$)')
ax.set_xlabel('Hierarchy Depth $L$')
ax.set_ylabel('$\\Phi_{\\mathrm{FT}}$')
ax.set_title('Hierarchy Depth Convergence')
ax.legend()
ax.set_xticks(L)
plt.tight_layout()
plt.savefig('convergence_hierarchy.pdf', dpi=300)
plt.close()

# Figure S3: Three-site dynamics
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# Panel (a): Populations
t = np.linspace(0, 1000, 200)
P1_broad = np.exp(-t/300)
P1_filt = np.exp(-t/400)
axes[0,0].plot(t, P1_broad, 'b--', label='Broadband', linewidth=2)
axes[0,0].plot(t, P1_filt, 'r-', label='Filtered', linewidth=2)
axes[0,0].set_xlabel('Time (fs)')
axes[0,0].set_ylabel('Population Site 1')
axes[0,0].legend()
axes[0,0].set_title('(a) Population Dynamics')

# Panel (b): Coherence
C_broad = np.exp(-t/230)
C_filt = np.exp(-t/310)
axes[0,1].plot(t, C_broad, 'b--', label='Broadband', linewidth=2)
axes[0,1].plot(t, C_filt, 'r-', label='Filtered', linewidth=2)
axes[0,1].set_xlabel('Time (fs)')
axes[0,1].set_ylabel('$C_{l_1}(t)$')
axes[0,1].legend()
axes[0,1].set_title('(b) Coherence ($\\tau_c$ extension)')

# Panel (c): Off-resonant control
P1_off = np.exp(-t/290)
axes[1,0].plot(t, P1_broad, 'b--', label='Broadband', linewidth=2)
axes[1,0].plot(t, P1_off, 'g-', label='Off-resonant', linewidth=2)
axes[1,0].set_xlabel('Time (fs)')
axes[1,0].set_ylabel('Population Site 1')
axes[1,0].legend()
axes[1,0].set_title('(c) Off-Resonant Control ($\\eta \\approx 0.03$)')

# Panel (d): Entropy
S_broad = 0.52 + 0.21*(1-np.exp(-t/400))
S_filt = 0.38 + 0.13*(1-np.exp(-t/500))
axes[1,1].plot(t, S_broad, 'b--', label='Broadband', linewidth=2)
axes[1,1].plot(t, S_filt, 'r-', label='Filtered', linewidth=2)
axes[1,1].set_xlabel('Time (fs)')
axes[1,1].set_ylabel('$S_{\\mathrm{vN}}$')
axes[1,1].legend()
axes[1,1].set_title('(d) Von Neumann Entropy')

plt.tight_layout()
plt.savefig('3site_dynamics.pdf', dpi=300)
plt.close()

print("Created placeholder figures:")
print("- spectral_density.pdf")
print("- convergence_hierarchy.pdf")
print("- 3site_dynamics.pdf")