#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Table of Contents (TOC) Graphic for JPCL
Required size: 1000 × 500 pixels
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Arrow, FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap

# Set up figure with exact dimensions
fig = plt.figure(figsize=(10, 5), dpi=100)  # 1000 x 500 pixels

# Create three panels
ax_left = fig.add_axes([0.02, 0.1, 0.3, 0.8])    # Left panel
ax_center = fig.add_axes([0.35, 0.1, 0.3, 0.8])  # Center panel
ax_right = fig.add_axes([0.68, 0.1, 0.3, 0.8])   # Right panel

# Color scheme
colors = {
    'broadband': '#FFFFFF',
    'filtered_green': '#4CAF50',
    'filtered_ir': '#9C27B0',
    'fmo': '#2E7D32',
    'coherence': '#00BCD4',
    'decoherence': '#F44336',
    'filter': '#1976D2',
    'text': '#212121',
}

# =============================================================================
# LEFT PANEL: Broadband Illumination (Baseline)
# =============================================================================

# Create rainbow gradient for broadband light
rainbow_colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', 
                  '#0000FF', '#4B0082', '#9400D3']
for i, color in enumerate(rainbow_colors):
    ax_left.axhspan(i/7, (i+1)/7, color=color, alpha=0.7)

# Draw FMO complex (7 connected spheres)
fmo_positions = [
    (0.5, 0.6), (0.3, 0.5), (0.7, 0.5),
    (0.4, 0.35), (0.6, 0.35), (0.35, 0.2), (0.65, 0.2)
]

for pos in fmo_positions:
    circle = Circle(pos, 0.06, color=colors['fmo'], alpha=0.5)
    ax_left.add_patch(circle)

# Draw connections (weak/decoherent)
for i, pos1 in enumerate(fmo_positions):
    for j, pos2 in enumerate(fmo_positions[i+1:], i+1):
        ax_left.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                    color=colors['decoherence'], linewidth=0.5, alpha=0.3, linestyle='--')

# Add decoherence X marks
ax_left.text(0.2, 0.15, '✕', color=colors['decoherence'], fontsize=30, 
             fontweight='bold', alpha=0.7)
ax_left.text(0.8, 0.15, '✕', color=colors['decoherence'], fontsize=30, 
             fontweight='bold', alpha=0.7)

ax_left.text(0.5, 0.08, 'Broadband', ha='center', va='top', 
             fontsize=12, fontweight='bold', color=colors['text'])
ax_left.text(0.5, 0.02, 'τc ≈ 300 fs', ha='center', va='top', 
             fontsize=11, fontweight='bold', color=colors['decoherence'])

ax_left.set_xlim(0, 1)
ax_left.set_ylim(0, 1)
ax_left.axis('off')
ax_left.set_title('Baseline', fontsize=11, fontweight='bold', pad=5)

# =============================================================================
# CENTER PANEL: Spectral Filter
# =============================================================================

# Draw OPV filter (semi-transparent blue panel)
filter_patch = FancyBboxPatch((0.2, 0.15), 0.6, 0.7, 
                               boxstyle='round,pad=0.02',
                               color=colors['filter'], alpha=0.4,
                               edgecolor=colors['filter'], linewidth=2)
ax_center.add_patch(filter_patch)

# Create transmission spectrum
wavelengths = np.linspace(400, 900, 500)
transmission = (np.exp(-(wavelengths-750)**2/2/25**2) + 
                np.exp(-(wavelengths-820)**2/2/25**2))

# Plot transmission spectrum on filter
trans_x = 0.25 + 0.5 * (transmission / transmission.max())
ax_center.plot(trans_x, 0.15 + 0.7 * (wavelengths - 400) / 500, 
               color='white', linewidth=2)

# Mark transmission peaks
ax_center.plot([0.75, 0.75], [0.15, 0.82], color='yellow', linestyle='--', 
               linewidth=1.5, alpha=0.8)
ax_center.plot([0.75, 0.75], [0.15, 0.88], color='yellow', linestyle='--', 
               linewidth=1.5, alpha=0.8)

ax_center.text(0.5, 0.92, 'Transmission Spectrum', ha='center', va='bottom',
               fontsize=10, fontweight='bold', color='white')
ax_center.text(0.5, 0.88, '750 nm, 820 nm', ha='center', va='bottom',
               fontsize=10, fontweight='bold', color='yellow')

# Add arrows showing filtering
for y in [0.3, 0.5, 0.7]:
    ax_center.arrow(0.15, y, 0.08, 0, color='white', linewidth=2, 
                   head_width=0.03, head_length=0.02)
    ax_center.arrow(0.82, y, 0.08, 0, color=colors['filtered_green'], 
                   linewidth=2, head_width=0.03, head_length=0.02)

ax_center.text(0.5, 0.08, 'Spectral Filter', ha='center', va='top',
               fontsize=12, fontweight='bold', color=colors['text'])
ax_center.text(0.5, 0.02, 'Vibronic Resonance', ha='center', va='top',
               fontsize=10, fontweight='bold', color=colors['filter'])

ax_center.set_xlim(0, 1)
ax_center.set_ylim(0, 1)
ax_center.axis('off')
ax_center.set_title('Engineering', fontsize=11, fontweight='bold', pad=5)

# =============================================================================
# RIGHT PANEL: Filtered Illumination (Enhanced)
# =============================================================================

# Create dual-color gradient (green + near-IR)
for i in range(100):
    y = i / 100
    if i < 50:
        color = colors['filtered_green']
        alpha = 0.5 + 0.5 * (i / 50)
    else:
        color = colors['filtered_ir']
        alpha = 0.5 + 0.5 * ((100 - i) / 50)
    ax_right.axhspan(y, y + 0.01, color=color, alpha=alpha * 0.7)

# Draw FMO complex (7 connected spheres)
for pos in fmo_positions:
    circle = Circle(pos, 0.06, color=colors['fmo'], alpha=0.8)
    ax_right.add_patch(circle)

# Draw connections (strong/coherent) - glowing cyan
for i, pos1 in enumerate(fmo_positions):
    for j, pos2 in enumerate(fmo_positions[i+1:], i+1):
        # Stronger connections
        ax_right.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                     color=colors['coherence'], linewidth=2, alpha=0.8)

# Add glow effect to connections
for i, pos1 in enumerate(fmo_positions):
    for j, pos2 in enumerate(fmo_positions[i+1:], i+1):
        ax_right.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                     color='white', linewidth=4, alpha=0.3)

# Add coherence waves
for pos in fmo_positions[:3]:
    for r in [0.12, 0.18, 0.24]:
        circle = Circle(pos, r, fill=False, color=colors['coherence'], 
                       linewidth=0.5, alpha=0.3)
        ax_right.add_patch(circle)

ax_right.text(0.5, 0.08, 'Filtered', ha='center', va='top',
              fontsize=12, fontweight='bold', color=colors['text'])
ax_right.text(0.5, 0.02, 'τc ≈ 500 fs (+50%)', ha='center', va='top',
              fontsize=11, fontweight='bold', color=colors['coherence'])

ax_right.set_xlim(0, 1)
ax_right.set_ylim(0, 1)
ax_right.axis('off')
ax_right.set_title('Enhanced Coherence', fontsize=11, fontweight='bold', pad=5)

# =============================================================================
# Main Title
# =============================================================================
fig.text(0.5, 0.98, 'Quantum-Coherent Spectral Engineering', 
         ha='center', va='top', fontsize=16, fontweight='bold', 
         color=colors['text'])

# =============================================================================
# Save figure
# =============================================================================
output_file = 'JPCL/TOC_Graphic.png'
plt.savefig(output_file, dpi=100, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print(f"Saved: {output_file}")

# Also save as TIFF for submission
output_file_tiff = 'JPCL/TOC_Graphic.tiff'
plt.savefig(output_file_tiff, dpi=100, bbox_inches='tight',
            facecolor='white', edgecolor='none', format='tiff')
print(f"Saved: {output_file_tiff}")

plt.show()

print("\n=== TOC Graphic Generation Complete ===")
print("Dimensions: 1000 × 500 pixels (10 × 5 inches at 100 dpi)")
