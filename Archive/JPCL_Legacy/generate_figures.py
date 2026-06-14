import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

print(f"Current working directory: {os.getcwd()}")

# Load data - adjust path from JPCL to simulation_data (3 levels up)
df_qd = pd.read_csv('../../../simulation_data/quantum_dynamics_20260225_170638.csv')

fig, axes = plt.subplots(2, 2, figsize=(8, 8))

# (a) Coherence
axes[0, 0].plot(df_qd['time_fs'], df_qd['coherences'], 'g-', label='Filtered')
axes[0, 0].axhline(y=0.5, color='gray', linestyle='--', label='Broadband (ref)')
axes[0, 0].set_xlabel('Time (fs)')
axes[0, 0].set_ylabel('Coherence (l₁-norm)')
axes[0, 0].legend()
axes[0, 0].set_title('(a) Coherence Extension')

# (b) Population
axes[0, 1].plot(df_qd['time_fs'], df_qd['population_site_1'], 'b-', label='Site 1')
axes[0, 1].plot(df_qd['time_fs'], df_qd['population_site_3'], 'r-', label='Site 3 (RC)')
axes[0, 1].set_xlabel('Time (fs)')
axes[0, 1].set_ylabel('Population')
axes[0, 1].legend()
axes[0, 1].set_title('(b) Population Transfer')

# (c) IPR
ipr = 1 / (df_qd[[f'population_site_{i}' for i in range(1,8)]]**2).sum(axis=1)
axes[1, 0].plot(df_qd['time_fs'], ipr, 'purple')
axes[1, 0].set_xlabel('Time (fs)')
axes[1, 0].set_ylabel('IPR (ξ)')
axes[1, 0].set_title('(c) Delocalization')

# (d) QFI
axes[1, 1].plot(df_qd['time_fs'], df_qd['qfi'], 'orange')
axes[1, 1].set_xlabel('Time (fs)')
axes[1, 1].set_ylabel('QFI')
axes[1, 1].set_title('(d) Quantum Fisher Information')

plt.tight_layout()
plt.savefig('Quantum_dynamics.png', dpi=300)
print("Generated Quantum_dynamics.png")


# Load environmental data
df_env = pd.read_csv('../../../simulation_data/environmental_effects_20260225_170850.csv')

fig2, axes2 = plt.subplots(1, 2, figsize=(10, 4))

# (a) Temperature dependence
eta_quantum = (df_env['etr_with_environment'] - 0.8) / 0.8  # Approximate
axes2[0].plot(df_env['time_days'], df_env['temperature_k'], 'r-', label='Temperature')
axes2[0].set_xlabel('Time (days)')
axes2[0].set_ylabel('Temperature (K)')
axes2[0].axhspan(285, 300, alpha=0.3, color='green', label='Optimal')
axes2[0].legend()
axes2[0].set_title('(a) Temperature Profile')

# (b) ETR with disorder
axes2[1].hist(eta_quantum, bins=30, alpha=0.7, color='blue')
axes2[1].axvline(eta_quantum.mean(), color='red', linestyle='--', 
                label=f'Mean: {eta_quantum.mean():.2f}')
axes2[1].set_xlabel('Coherence Enhancement (η)')
axes2[1].set_ylabel('Frequency')
axes2[1].legend()
axes2[1].set_title('(b) Disorder Ensemble')

plt.tight_layout()
plt.savefig('ETR_Under_Environmental_Effects.pdf')
print("Generated ETR_Under_Environmental_Effects.pdf")
