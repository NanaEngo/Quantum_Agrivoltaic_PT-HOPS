import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)

# scienceplots style to use as base — 'science' provides IEEE/ACS-compatible
# defaults (clean axes, no grid, proper font sizing).
# 'no-latex' avoids requiring a LaTeX installation.
_SCIENCE_STYLES = ['science', 'no-latex']


def apply_jpcl_theme():
    """
    Apply JPCL (ACS) publication standards to matplotlib.
    Uses scienceplots 'science' style as base, then overrides with
    ACS-specific values (column widths, DPI, colorblind-safe palette).
    """
    # Apply scienceplots base style if available
    try:
        import scienceplots  # noqa: F401 — registers styles on import
        plt.style.use(_SCIENCE_STYLES)
        logger.info("scienceplots 'science' base style applied.")
    except ImportError:
        logger.warning(
            "scienceplots not installed — falling back to manual rcParams. "
            "Install with: pip install scienceplots"
        )

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
