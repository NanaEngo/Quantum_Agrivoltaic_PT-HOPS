"""Unit tests for the AM1.5G passband-cost computation (spectral co-design)."""

from src.lca.neb import _FALLBACK, passband_fraction


def test_passband_fractions_from_reference_spectrum():
    f_am15g, f_window, band_w = passband_fraction()
    # 750 nm band ~4.9 W/m2 + 820 nm band ~5.3 W/m2 of the 1000.4 W/m2 AM1.5G.
    assert 9.0 < band_w < 11.0
    assert 0.009 < f_am15g < 0.012
    assert 0.011 < f_window < 0.015


def test_fallback_matches_reference_integrals():
    # Published manuscript numbers must stay reproducible even without the CSV.
    assert abs(passband_fraction("/nonexistent/astmg173.csv")[0] - _FALLBACK[0]) < 1e-12
    assert _FALLBACK == (0.0102, 0.0127, 10.236)
