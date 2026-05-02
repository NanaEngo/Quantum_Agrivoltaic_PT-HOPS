import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)

def apply_jpcl_theme():
    """
    Apply JPCL (ACS) publication standards to matplotlib.
    Focuses on legibility, high DPI, and correct units.
    """
    # Standard ACS Column Widths (inches)
    # Single column: 3.25 in
    # Double column: 7 in
    
    jpcl_params = {
        'figure.dpi': 600,
        'figure.figsize': (3.25, 2.75), # Single column default
        'axes.labelsize': 10,
        'axes.titlesize': 10,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'legend.fontsize': 8,
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'lines.linewidth': 1.2,
        'axes.linewidth': 0.8,
        'grid.alpha': 0.3,
        'grid.linestyle': '--',
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
        'text.usetex': False # Keep False for broader compatibility, unless TeX is verified
    }
    
    plt.rcParams.update(jpcl_params)
    logger.info("JPCL Publication Theme applied successfully (600 DPI, Arial/Sans).")

def get_color_palette():
    """
    Returns the high-contrast color palette for FMO site populations.
    """
    # Using a perceptually uniform palette (e.g., colorblind friendly)
    return ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7']
