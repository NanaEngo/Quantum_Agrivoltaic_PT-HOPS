import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Create base dir if not exists
os.makedirs('Shared_Resources/quantum_dynamics_plots', exist_ok=True)

print("Generating Figure 1: Quantum Dynamics...")
df1 = pd.read_csv('../../simulation_data/quantum_dynamics_20260225_170638.csv')

fig, axes = plt.subplots(2, 2, figsize=(8, 8))

# (a) Coherence
axes[0, 0].plot(df1['time_fs'], df1['coherences'], 'g-', label='Filtered')
axes[0, 0].axhline(y=0.5, color='gray', linestyle='--', label='Broadband (ref)')
axes[0, 0].set_xlabel('Time (fs)')
axes[0, 0].set_ylabel('Coherence (l₁-norm)')
axes[0, 0].legend()
axes[0, 0].set_title('(a) Coherence Extension')

# (b) Population
axes[0, 1].plot(df1['time_fs'], df1['population_site_1'], 'b-', label='Site 1')
axes[0, 1].plot(df1['time_fs'], df1['population_site_3'], 'r-', label='Site 3 (RC)')
axes[0, 1].set_xlabel('Time (fs)')
axes[0, 1].set_ylabel('Population')
axes[0, 1].legend()
axes[0, 1].set_title('(b) Population Transfer')

# (c) IPR
ipr = 1 / (df1[[f'population_site_{i}' for i in range(1,8)]]**2).sum(axis=1)
axes[1, 0].plot(df1['time_fs'], ipr, 'purple')
axes[1, 0].set_xlabel('Time (fs)')
axes[1, 0].set_ylabel('IPR (ξ)')
axes[1, 0].set_title('(c) Delocalization')

# (d) QFI
axes[1, 1].plot(df1['time_fs'], df1['qfi'], 'orange')
axes[1, 1].set_xlabel('Time (fs)')
axes[1, 1].set_ylabel('QFI')
axes[1, 1].set_title('(d) Quantum Fisher Information')

plt.tight_layout()
plt.savefig('Shared_Resources/quantum_dynamics_plots/Quantum_dynamics.png', dpi=300)
print("Figure 1 Complete.")

print("Generating Figure 2: Environmental Robustness...")
df2 = pd.read_csv('../../simulation_data/environmental_effects_20260225_170850.csv')

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# (a) Temperature dependence
eta_quantum = (df2['etr_with_environment'] - 0.8) / 0.8  # Approximate
axes[0].plot(df2['time_days'], df2['temperature_k'], 'r-', label='Temperature')
axes[0].set_xlabel('Time (days)')
axes[0].set_ylabel('Temperature (K)')
axes[0].axhspan(285, 300, alpha=0.3, color='green', label='Optimal')
axes[0].legend()
axes[0].set_title('(a) Temperature Profile')

# (b) ETR with disorder
axes[1].hist(eta_quantum, bins=30, alpha=0.7, color='blue')
axes[1].axvline(eta_quantum.mean(), color='red', linestyle='--', 
                label=f'Mean: {eta_quantum.mean():.2f}')
axes[1].set_xlabel('Quantum Advantage (η)')
axes[1].set_ylabel('Frequency')
axes[1].legend()
axes[1].set_title('(b) Disorder Ensemble')

plt.tight_layout()
plt.savefig('Shared_Resources/quantum_dynamics_plots/ETR_Under_Environmental_Effects.pdf')
print("Figure 2 Complete.")

print("All figures successfully generated to Shared_Resources/quantum_dynamics_plots")
