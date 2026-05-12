"""
JPCL Publication Theme and Colorblind-Safe Palettes.

This module provides the design system for simulation graphics, ensuring 
compliance with American Chemical Society (ACS) and Journal of Physical 
Chemistry Letters (JPCL) formatting requirements. It integrates with the 
scienceplots library to provide clean, high-resolution (600 DPI) scientific 
visualizations.
"""

import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)

# scienceplots style to use as base — 'science' provides IEEE/ACS-compatible
# defaults (clean axes, no grid, proper font sizing).
# 'no-latex' avoids requiring a LaTeX installation.
_SCIENCE_STYLES = ['science', 'no-latex']


def apply_jpcl_theme():
    """
    Apply JPCL (ACS) publication standards to the global matplotlib state.

    This function configures the matplotlib RC parameters to match the 
    formatting requirements of the Journal of Physical Chemistry Letters. 
    It enforces specific font families (Arial/Helvetica), font sizes, line 
    widths, and high-resolution output (600 DPI) suitable for archival 
    publication.

    Notes
    -----
    The theme uses the 'science' and 'nature' styles from the scienceplots 
    library as a foundation. If scienceplots is unavailable, it falls back 
    to standard seaborn or ggplot styles.
    """
    # Apply scienceplots base style if available
    try:
        import scienceplots  # noqa: F401 — registers styles on import
        plt.style.use(['science', 'nature', 'no-latex']) # JPCL-preferred styles
        logger.info("scienceplots 'science' + 'nature' styles applied.")
    except (ImportError, Exception):
        logger.warning("scienceplots not available — using seaborn-paper fallback.")
        try:
            plt.style.use('seaborn-v0_8-paper')
        except:
            plt.style.use('ggplot')

    # ACS/JPCL overrides on top of scienceplots base
    # Standard ACS column widths: single = 3.25 in, double = 7 in
    jpcl_params = {
        'figure.dpi': 600,
        'figure.figsize': (3.25, 2.75),   # single column default
        'axes.labelsize': 10,
        'axes.titlesize': 10,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'legend.fontsize': 8,
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'lines.linewidth': 1.2,
        'axes.linewidth': 0.8,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
        'text.usetex': False,
    }
    plt.rcParams.update(jpcl_params)
    logger.info("JPCL Publication Theme applied (600 DPI, Arial/Sans, scienceplots base).")


def get_color_palette():
    """
    Colorblind-safe palette (Wong 2011) for FMO site populations.
    7 colors — one per BChl site.
    """
    return ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7']
