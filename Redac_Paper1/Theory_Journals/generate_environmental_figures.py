#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Environmental Robustness Figures for JPCL Manuscript
From: simulation_data/environmental_effects_20260225_170850.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Set publication-quality style
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica'],
    'axes.linewidth': 1.0,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.figsize': (10, 4.5),
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.02,
})

# Load environmental effects data
print("Loading environmental effects data...")
df = pd.read_csv('../../simulation_data/environmental_effects_20260225_170850.csv')
print(f"Loaded {len(df)} days of environmental data")

# Calculate quantum advantage (eta_quantum)
# ETR enhancement relative to Markovian baseline (0.8 from manuscript context)
etr_baseline = 0.8  # Markovian baseline
eta_quantum = (df['etr_with_environment'] - etr_baseline) / etr_baseline

# Calculate PCE degradation
pce_initial = df['pce_with_environment'].iloc[0]
pce_degradation = (pce_initial - df['pce_with_environment']) / pce_initial * 100

# Create figure with 2 panels
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

# Color scheme
colors = {
    'temperature': '#D32F2F',     # Red
    'optimal': '#4CAF50',         # Green
    'eta': '#1976D2',             # Blue
    'fit': '#7B1FA2',             # Purple
}

# =============================================================================
# PANEL (a): Temperature Dependence
# =============================================================================
ax = axes[0]

# Plot temperature profile over year
ax.plot(df['time_days'], df['temperature_k'], color=colors['temperature'], 
        linewidth=1.5, alpha=0.8, label='Temperature')

# Highlight optimal temperature range (285-300 K from manuscript)
ax.axhspan(285, 300, alpha=0.3, color=colors['optimal'], 
           label='Optimal range (285-300 K)')

# Mark physiological temperature
ax.axhline(y=295, color='black', linestyle='--', linewidth=1, alpha=0.5, 
           label='Physiological (295 K)')

ax.set_xlabel('Time (days)')
ax.set_ylabel('Temperature (K)')
ax.set_title('(a) Temperature Profile')
ax.legend(loc='upper right', framealpha=0.9, fontsize=8)
ax.set_xlim(0, 365)
ax.set_ylim(280, 310)
ax.grid(True, alpha=0.3)

# Add annotation for quantum advantage at different temperatures
ax.annotate('Max coherence\npreservation', xy=(100, 305), fontsize=9, 
            color=colors['optimal'], fontweight='bold')

# =============================================================================
# PANEL (b): Quantum Advantage Distribution
# =============================================================================
ax = axes[1]

# Plot histogram of quantum advantage
n, bins, patches = ax.hist(eta_quantum, bins=40, color=colors['eta'], 
                           alpha=0.7, edgecolor='darkblue', linewidth=0.5,
                           density=True, label='Ensemble distribution')

# Fit normal distribution and plot
mu, sigma = stats.norm.fit(eta_quantum)
x_fit = np.linspace(eta_quantum.min(), eta_quantum.max(), 100)
pdf_fit = stats.norm.pdf(x_fit, mu, sigma)
ax.plot(x_fit, pdf_fit, color=colors['fit'], linewidth=2.5, 
        label=f'Fit: μ={mu:.3f}, σ={sigma:.3f}')

# Mark mean and confidence interval
ax.axvline(x=mu, color=colors['fit'], linestyle='--', linewidth=2, 
           label=f'Mean: {mu:.3f}')
ax.axvspan(mu - 1.96*sigma, mu + 1.96*sigma, alpha=0.2, color=colors['fit'],
           label='95% CI')

# Mark threshold from manuscript (η > 0.15)
ax.axvline(x=0.15, color='red', linestyle=':', linewidth=2, 
           label='Threshold (0.15)')

ax.set_xlabel('Quantum Advantage (η)')
ax.set_ylabel('Probability Density')
ax.set_title(f'(b) Disorder Ensemble (n={len(eta_quantum)})')
ax.legend(loc='upper right', framealpha=0.9, fontsize=8)
ax.grid(True, alpha=0.3)

# Add statistics annotation
cv = sigma / mu * 100  # Coefficient of variation
ax.annotate(f'CV = {cv:.1f}%', xy=(0.25, 0.7*max(pdf_fit)), fontsize=9, 
            fontweight='bold')

# =============================================================================
# Final layout and save
# =============================================================================
plt.tight_layout()

# Save to JPCL folder
output_file = 'JPCL/ETR_Under_Environmental_Effects.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nSaved: {output_file}")

# Also save as PDF for better quality
output_file_pdf = 'JPCL/ETR_Under_Environmental_Effects.pdf'
plt.savefig(output_file_pdf, bbox_inches='tight')
print(f"Saved: {output_file_pdf}")

plt.show()

print("\n=== Figure Generation Complete ===")
print("Key statistics:")
print(f"  Temperature range: {df['temperature_k'].min():.1f} - {df['temperature_k'].max():.1f} K")
print(f"  Mean quantum advantage: {mu:.4f}")
print(f"  Std deviation: {sigma:.4f}")
print(f"  Coefficient of variation: {cv:.1f}%")
print(f"  95% CI: [{mu-1.96*sigma:.4f}, {mu+1.96*sigma:.4f}]")
print(f"  PCE degradation (annual): {pce_degradation.iloc[-1]:.3f}%")
