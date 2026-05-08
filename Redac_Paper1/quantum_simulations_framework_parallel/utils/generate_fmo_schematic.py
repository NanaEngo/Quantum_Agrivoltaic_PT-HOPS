#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate FMO Complex Schematic for JPCL Figures.
Draws the 7-site BChl arrangement in the FMO monomer.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import os
import logging

logger = logging.getLogger(__name__)

def generate_fmo_schematic(output_path):
    """
    Draw a stylized 7-site FMO complex schematic.
    """
    fig, ax = plt.subplots(figsize=(5, 5))
    
    # FMO positions (normalized 0-1)
    fmo_positions = [
        (0.5, 0.6), (0.3, 0.5), (0.7, 0.5),
        (0.4, 0.35), (0.6, 0.35), (0.35, 0.2), (0.65, 0.2)
    ]
    
    # Colors
    color_fmo = '#2E7D32'  # Green
    color_coherence = '#00BCD4' # Cyan
    
    # Draw connections (coherent)
    for i, pos1 in enumerate(fmo_positions):
        for j, pos2 in enumerate(fmo_positions[i+1:], i+1):
            ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                     color=color_coherence, linewidth=2, alpha=0.6)

    # Draw BChl sites
    for i, pos in enumerate(fmo_positions):
        circle = Circle(pos, 0.06, color=color_fmo, alpha=0.9, zorder=10)
        ax.add_patch(circle)
        ax.text(pos[0], pos[1], str(i+1), color='white', ha='center', va='center', 
                fontweight='bold', zorder=11)

    ax.set_xlim(0.2, 0.8)
    ax.set_ylim(0.1, 0.7)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, transparent=True)
    plt.close()
    logger.info(f"FMO schematic generated at {output_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dest = os.path.join(os.path.dirname(__file__), '../../Theory_Journals_main/JPCL/FMO_Schematic_JPCL.png')
    generate_fmo_schematic(dest)
