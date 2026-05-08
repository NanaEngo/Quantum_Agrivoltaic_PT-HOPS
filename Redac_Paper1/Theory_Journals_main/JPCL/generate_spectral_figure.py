#!/usr/bin/env python3
"""
Generate Figure 1(e) - Spectral Relationships
Shows FMO absorption, solar spectrum, bath spectral density, and filter transmission
"""

import numpy as np
import matplotlib.pyplot as plt

# Wavelength range (nm)
wavelengths_nm = np.linspace(600, 900, 500)
wavelengths_m = wavelengths_nm * 1e-9

# Convert to wavenumbers (cm^-1)
# E = hc/λ => wavenumber = 1/λ (in cm^-1)
wavenumbers = 1e7 / wavelengths_nm  # cm^-1

# Constants
hbar = 1.0545718e-34  # J*s
c = 2.99792458e8  # m/s
kB = 1.380649e-23  # J/K
T = 295  # K

# ============================================
# 1. FMO Absorption Spectrum (BChl a in FMO)
# ============================================
# Qy transition of BChl a peaks around 800 nm
# FMO has broad absorption with peaks at ~750 nm and ~805 nm
fmo_absorption = (
    0.6 * np.exp(-((wavelengths_nm - 750)**2) / (2 * 15**2)) +  # High energy peak
    1.0 * np.exp(-((wavelengths_nm - 805)**2) / (2 * 20**2))    # Main Qy peak
)

# ============================================
# 2. Solar Spectrum (AM1.5G normalized)
# ============================================
# Approximate AM1.5G in visible-NIR region
# Peak around 500 nm, tailing off to NIR
solar_norm = (
    0.8 * np.exp(-((wavelengths_nm - 550)**2) / (2 * 150**2)) +
    0.4 * np.exp(-((wavelengths_nm - 800)**2) / (2 * 100**2))
)
solar_norm = solar_norm / solar_norm.max()

# ============================================
# 3. Bath Spectral Density (Drude-Lorentz + vibronic modes)
# ============================================
# Convert wavenumbers to angular frequency
omega = wavenumbers * 2 * np.pi * c * 100  # rad/s

# Drude-Lorentz parameters
lambda_dl = 35 * 100 * hbar * c * 2 * np.pi  # J (35 cm^-1)
gamma_dl = 1 / (106e-15)  # rad/s (106 fs decay)

# Drude-Lorentz spectral density
J_dl = (2 * lambda_dl * gamma_dl * omega) / (omega**2 + gamma_dl**2)

# Vibronic modes (underdamped oscillators)
# Frequencies: 150, 200, 575, 1185 cm^-1
vibronic_freqs = np.array([150, 200, 575, 1185]) * 2 * np.pi * c * 100  # rad/s
vibronic_widths = np.array([10, 15, 20, 30]) * 2 * np.pi * c * 100  # rad/s
huang_rhys = np.array([0.05, 0.02, 0.01, 0.005])

J_vibronic = np.zeros_like(omega)
for w_k, gamma_k, S_k in zip(vibronic_freqs, vibronic_widths, huang_rhys):
    J_vibronic += (
        2 * np.pi * S_k * omega * w_k * gamma_k /
        ((omega**2 - w_k**2)**2 + omega**2 * gamma_k**2)
    )

J_total = J_dl + J_vibronic
J_total_norm = J_total / J_total.max()

# ============================================
# 4. Filter Transmission (dual-band Gaussian)
# ============================================
filter_centers = [750, 820]  # nm
filter_widths = [20, 20]  # nm FWHM
filter_weights = [0.5, 0.5]

T_filter = np.zeros_like(wavelengths_nm)
for center, width, weight in zip(filter_centers, filter_widths, filter_weights):
    T_filter += weight * np.exp(-((wavelengths_nm - center)**2) / (2 * (width/2.355)**2))

# ============================================
# Create Figure
# ============================================
fig, ax = plt.subplots(figsize=(8, 5))

# Plot with different line styles and colors
ax.fill_between(wavelengths_nm, 0, fmo_absorption, alpha=0.3, color='green', label='FMO absorption')
ax.plot(wavelengths_nm, fmo_absorption, 'g-', linewidth=2)

ax.fill_between(wavelengths_nm, 0, solar_norm, alpha=0.2, color='orange', label='Solar irradiance')
ax.plot(wavelengths_nm, solar_norm, 'orange', linewidth=1.5, linestyle='--')

ax.fill_between(wavelengths_nm, 0, J_total_norm, alpha=0.2, color='blue', label='Bath spectral density')
ax.plot(wavelengths_nm, J_total_norm, 'b-', linewidth=1.5, linestyle='-.')

ax.fill_between(wavelengths_nm, 0, T_filter, alpha=0.4, color='red', label='Filter transmission')
ax.plot(wavelengths_nm, T_filter, 'r-', linewidth=2)

# Mark filter center wavelengths
for center in filter_centers:
    ax.axvline(x=center, color='red', linestyle=':', alpha=0.5, linewidth=1)
    ax.annotate(f'{center} nm', xy=(center, 0.9), ha='center', fontsize=9, color='red')

# Labels and formatting
ax.set_xlabel('Wavelength (nm)', fontsize=12, fontweight='bold')
ax.set_ylabel('Normalized intensity / transmission', fontsize=12, fontweight='bold')
ax.set_xlim(600, 900)
ax.set_ylim(0, 1.1)
ax.legend(loc='upper right', framealpha=0.9)
ax.grid(True, alpha=0.3)

# Title
ax.set_title('(e) Spectral Relationships', fontsize=13, fontweight='bold', loc='left')

plt.tight_layout()
plt.savefig('Figure1e_spectral_relationships.pdf', dpi=300, bbox_inches='tight')
plt.savefig('Figure1e_spectral_relationships.png', dpi=300, bbox_inches='tight')
print("Generated Figure1e_spectral_relationships.pdf and .png")

# Also create a combined figure that could be the full Figure 1
# This would be a 5-panel figure in the manuscript
fig_full, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

# Panel (a)-(d) would be the quantum dynamics data from existing generate_figures.py
# Here we just create placeholder labels for reference

# Panel (e) - Spectral relationships (our new figure)
ax_e = axes[4]
ax_e.fill_between(wavelengths_nm, 0, fmo_absorption, alpha=0.3, color='green', label='FMO absorption')
ax_e.plot(wavelengths_nm, fmo_absorption, 'g-', linewidth=2)
ax_e.fill_between(wavelengths_nm, 0, solar_norm, alpha=0.2, color='orange', label='Solar irradiance')
ax_e.plot(wavelengths_nm, solar_norm, 'orange', linewidth=1.5, linestyle='--')
ax_e.fill_between(wavelengths_nm, 0, J_total_norm, alpha=0.2, color='blue', label='Bath spectral density')
ax_e.plot(wavelengths_nm, J_total_norm, 'b-', linewidth=1.5, linestyle='-.')
ax_e.fill_between(wavelengths_nm, 0, T_filter, alpha=0.4, color='red', label='Filter transmission')
ax_e.plot(wavelengths_nm, T_filter, 'r-', linewidth=2)

for center in filter_centers:
    ax_e.axvline(x=center, color='red', linestyle=':', alpha=0.5, linewidth=1)
    ax_e.annotate(f'{center} nm', xy=(center, 0.9), ha='center', fontsize=8, color='red')

ax_e.set_xlabel('Wavelength (nm)', fontsize=10)
ax_e.set_ylabel('Normalized intensity', fontsize=10)
ax_e.set_xlim(600, 900)
ax_e.set_ylim(0, 1.1)
ax_e.legend(loc='upper right', fontsize=8)
ax_e.set_title('(e) Spectral relationships', fontsize=11, fontweight='bold', loc='left')

# Hide unused panel
axes[5].axis('off')

plt.tight_layout()
plt.savefig('Figure1_template_with_spectral.png', dpi=300, bbox_inches='tight')
print("Generated Figure1_template_with_spectral.png (template)")
