"""MesoHOPS 1.8.0 smoke test: non-dyadic absorption response from a 2-site aggregate.
Mirrors tests/test_nondyadic_spectroscopy.py::_make_traj, then FFTs the correlator.
Run: conda run -n MesoHOP-sim-18 python smoke_18_absorption.py  (exit 0 + 'SMOKE PASS')
"""
import numpy as np
from mesohops.trajectory.exp_noise import bcf_exp
from mesohops.trajectory.hops_trajectory import HopsTrajectory as HOPS
from mesohops.util.nondyadic_spectroscopy import calc_absorption_response

n_site, n_state = 2, 3
H = np.zeros((n_state, n_state), dtype=np.complex128)
H[1:, 1:] = np.diag([100.0, 0.0]) + np.diag([-50.0] * (n_site - 1), k=1) + np.diag([-50.0] * (n_site - 1), k=-1)
lop = []
for i in range(n_site):
    m = np.zeros((n_state, n_state))
    m[i + 1, i + 1] = 1.0
    lop.append(m)
gw = [[10.0, 10.0]] * n_site
sys_p = {"HAMILTONIAN": H, "GW_SYSBATH": gw, "L_HIER": lop, "L_NOISE1": lop,
         "ALPHA_NOISE1": bcf_exp, "PARAM_NOISE1": gw}
noise_p = {"SEED": 42, "MODEL": "FFT_FILTER", "TLEN": 1700.0, "TAU": 0.25}

T_MAX, T_STEP = 1600.0, 0.5
dipoles = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
E_1 = np.array([1.0, 0.0, 0.0])

c1 = calc_absorption_response(HOPS(sys_p, noise_param=noise_p, hierarchy_param={"MAXHIER": 2},
                                   eom_param={"EQUATION_OF_MOTION": "NONLINEAR"}),
                              dipoles, E_1, T_MAX, T_STEP)
c1b = calc_absorption_response(HOPS(sys_p, noise_param=noise_p, hierarchy_param={"MAXHIER": 2},
                                    eom_param={"EQUATION_OF_MOTION": "NONLINEAR"}),
                               dipoles, E_1, T_MAX, T_STEP)
assert len(c1) == round(T_MAX / T_STEP), f"length {len(c1)}"  # grid is t_step..t_max (no t=0)
assert np.all(np.isfinite(c1)), "non-finite correlator"
assert np.max(np.abs(np.asarray(c1) - np.asarray(c1b))) < 1e-10, "seed not deterministic"

c1 = np.asarray(c1, dtype=np.complex128) - np.mean(c1)  # kill DC tail (uncoupled ground-state coherence)
spec = np.abs(np.fft.fft(c1 * np.hanning(len(c1))))
omega = np.fft.fftfreq(len(c1), d=T_STEP) * 2 * np.pi  # rad/fs
pos = omega > 0
binwidth = 1e15 / (T_MAX * 2 * np.pi * 2.99792458e10) * 2 * np.pi  # cm^-1 per bin
cm1 = omega[pos] * 1e15 / (2 * np.pi * 2.99792458e10)
peak = cm1[np.argmax(spec[pos])]
print(f"C1(t) len={len(c1)} | decay |C1(T_MAX)|={abs(np.asarray(c1, dtype=np.complex128)[-1]):.3e}")
print(f"absorption peak = {peak:.1f} cm^-1 (bin width {binwidth:.1f}; expected transitions 20.7 or 120.7 cm^-1)")
assert min(abs(peak - 20.7), abs(peak - 120.7)) < 3 * binwidth, "peak far from dimer manifold"
print("SMOKE PASS")
