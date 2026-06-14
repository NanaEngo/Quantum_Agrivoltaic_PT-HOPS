import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
import os

# Use scienceplots style
plt.style.use(['science', 'nature', 'no-latex'])

# Colors from previous script
colors = {
    'primary_blue': '#2E5C8A',
    'secondary_blue': '#5B9BD5',
    'accent_red': '#C5504B',
    'accent_green': '#70AD47',
    'accent_orange': '#ED7D31',
    'accent_purple': '#9F4F96',
    'light_gray': '#D9D9D9',
    'dark_gray': '#595959',
    'background': '#F8F9FA'
}

# Paths to production data
data_dir = 'Redac_Paper1/quantum_simulations_framework_parallel_260512/reproducibility/results/'
ensemble_file = os.path.join(data_dir, 'fmo_dynamics_ensemble_2d6bf169d04e_20260510_125633.csv')

print(f"Loading data from {ensemble_file}...")
df = pd.read_csv(ensemble_file)

# Convert to numeric
cols_to_fix = ['time_fs', 'population_site_1', 'population_site_3', 'population_site_7', 'coherences', 'pop_site1_broadband', 'coherence_broadband']
for col in cols_to_fix:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=cols_to_fix)

# Subsample for smoother plotting
if len(df) > 500:
    df = df.iloc[::len(df)//200]

t = df['time_fs']

# Create 4-panel figure
fig = plt.figure(figsize=(10, 8))
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)

# Panel (a): Population Dynamics (Site 1)
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(t, df['pop_site1_broadband'], color=colors['secondary_blue'], linestyle='--', label='Site 1 (Broad)')
ax1.plot(t, df['population_site_1'], color=colors['secondary_blue'], linewidth=2, label='Site 1 (Filt)')
ax1.set_xlabel('Time (fs)')
ax1.set_ylabel('Population')
ax1.set_title('(a) Site 1 Population', loc='left', fontweight='bold')
ax1.legend()
ax1.grid(alpha=0.3)
ax1.set_xlim(0, 1000)
ax1.set_ylim(0, 0.4) # Site 1 starts high then drops

# Panel (b): Coherence dynamics
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(t, df['coherence_broadband'], color=colors['secondary_blue'], linestyle='--', label='Broadband')
ax2.plot(t, df['coherences'], color=colors['accent_red'], linewidth=2, label='Filtered')
ax2.set_xlabel('Time (fs)')
ax2.set_ylabel('$C_{l_1}(t)$')
ax2.set_title('(b) Total Coherence', loc='left', fontweight='bold')
ax2.legend()
ax2.grid(alpha=0.3)
ax2.set_xlim(0, 1000)

# Panel (c): Target Yield (Site 7 - Reaction Center)
ax3 = fig.add_subplot(gs[1, 0])
# For broadband, we don't have site 7 in the ensemble CSV, so we'll use site 1 broadband as baseline or just plot filtered
ax3.plot(t, df['population_site_7'], color=colors['accent_orange'], linewidth=2, label='Filtered')
ax3.set_xlabel('Time (fs)')
ax3.set_ylabel('Population Site 7')
ax3.set_title('(c) RC Transfer Yield (Filtered)', loc='left', fontweight='bold')
ax3.legend()
ax3.grid(alpha=0.3)
ax3.set_xlim(0, 1000)

# Panel (d): IPR (Filtered)
ax4 = fig.add_subplot(gs[1, 1])
# Calculate IPR for filtered
pop_cols = [f'population_site_{i}' for i in range(1, 8)]
df['ipr'] = 1.0 / (df[pop_cols]**2).sum(axis=1)
ax4.plot(t, df['ipr'], color=colors['accent_purple'], linewidth=2, label='Filtered')
ax4.set_xlabel('Time (fs)')
ax4.set_ylabel(r'IPR ($\xi$)')
ax4.set_title('(d) Delocalization (IPR, Filtered)', loc='left', fontweight='bold')
ax4.legend()
ax4.grid(alpha=0.3)
ax4.set_xlim(0, 1000)

for ax in [ax1, ax2, ax3, ax4]:
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.yaxis.set_major_locator(plt.MaxNLocator(5))

fig.suptitle('Full 7-Site FMO Model: Spectral Bath Engineering Results (Production Data)', 
             fontsize=14, fontweight='bold', y=0.98)

output_path = 'Redac_Paper1/Theory_Journals_main/JPCL/FigureS4_7site_dynamics.pdf'
plt.savefig(output_path, dpi=600, bbox_inches='tight')
plt.savefig(output_path.replace('.pdf', '.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"[OK] Created 7-site equivalent figure at {output_path}")
