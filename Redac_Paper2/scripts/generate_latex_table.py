#!/usr/bin/env python3
"""Generate LaTeX table of 5-run comparison for manuscript."""

import os

import h5py

# The manuscript defines Φ_FT = Γ_RC × ∫(P₃+P₄)dt (Eq. 2), which corresponds
# to the physical forward transfer yield. Old HDF5 files were generated with
# this definition, so rc_yield values are used directly.

# Load data
f_base = h5py.File("Redac_Paper2/data/converged/production_dynamics.h5", "r")
pop_base = f_base["dynamics/populations"][:]
rc_base = f_base["dynamics/rc_yield"][:]
trace_base = pop_base.sum(axis=1)
f_base.close()

f_v08 = h5py.File("Redac_Paper2/data/production_dynamics.h5", "r")
pop_v08 = f_v08["dynamics/populations"][:]
rc_v08 = f_v08["dynamics/rc_yield"][:]
trace_v08 = pop_v08.sum(axis=1)
f_v08.close()

f_v12 = h5py.File("Redac_Paper2/data/converged/production_dynamics_295K_NPoM_ON.h5", "r")
pop_v12 = f_v12["dynamics/populations"][:]
rc_v12 = f_v12["dynamics/rc_yield"][:]
trace_v12 = pop_v12.sum(axis=1)
f_v12.close()

f_77k = h5py.File("Redac_Paper2/data/converged/production_dynamics_77K.h5", "r")
pop_77k = f_77k["dynamics/populations"][:]
rc_77k = f_77k["dynamics/rc_yield"][:]
trace_77k = pop_77k.sum(axis=1)
f_77k.close()

# Trapping sites max
trap_base = (pop_base[:, 2] + pop_base[:, 3]).max() if pop_base.shape[0] > 2 else 0.0
trap_v08 = (pop_v08[:, 2] + pop_v08[:, 3]).max()
trap_v12 = (pop_v12[:, 2] + pop_v12[:, 3]).max()
trap_77k = (pop_77k[:, 2] + pop_77k[:, 3]).max()


def f4(v):
    return f"{v:.4f}"


def f6(v):
    return f"{v:.6f}"


def f2(v):
    return f"{v:.2f}"


# SERS EF
ef_v08 = 100.0
ef_v12 = 44.0
ef_77k = 44.0

fom_v08 = rc_v08[-1] * ef_v08
fom_v12 = rc_v12[-1] * ef_v12
fom_77k = rc_77k[-1] * ef_77k

site1_base = pop_base[-1, 0]
site1_v08 = pop_v08[-1, 0]
site1_v12 = pop_v12[-1, 0]
site1_77k = pop_77k[-1, 0]

site6_base = pop_base[-1, 5] if pop_base.shape[1] > 5 else 0.0
site6_v08 = pop_v08[-1, 5]
site6_v12 = pop_v12[-1, 5]
site6_77k = pop_77k[-1, 5]

plasmon_v08 = pop_v08[-1, 8]
plasmon_v12 = pop_v12[-1, 8]
plasmon_77k = pop_77k[-1, 8]

# Build LaTeX
latex = r"\begin{table*}[tbp]" + "\n"
latex += r"\centering" + "\n"
latex += r"\caption{\textbf{Comparative summary of simulated configurations.}" + "\n"
latex += r"All NPoM-on configurations use the 9-site dressed Hamiltonian" + "\n"
latex += r"(8 FMO~$+$~1 plasmon mode) with hierarchy depth $L=8$, $K=2$ Matsubara" + "\n"
latex += r"terms, $\Delta t = 0.2$~fs over a $1000$~fs window." + "\n"
latex += r"The NPoM-off baseline uses the 8-site FMO Hamiltonian with identical" + "\n"
latex += r"solver parameters." + "\n"
latex += r"Trapping yield $\Phi_{\rm FT}$ is defined in Eq.~(2);" + "\n"
latex += r"the SERS enhancement factor $\mathrm{EF}$ follows the Purcell scaling" + "\n"
latex += r"$\mathrm{EF} \propto (Q/V)^2$ normalized to $\mathrm{EF}=10^2$ at" + "\n"
latex += r"$V=0.8$~nm$^3$~\cite{Chikkaraddy2016}.}" + "\n"
latex += r"\label{tab:comparative_summary}" + "\n"
latex += r"\small" + "\n"
latex += r"\begin{tabular}{lcccc}" + "\n"
latex += r"\toprule" + "\n"
latex += (
    r"\bfseries Metric & \bfseries NPoM-off & \bfseries NPoM-on & \bfseries NPoM-on & \bfseries NPoM-on \\"
    + "\n"
)
latex += (
    r"\bfseries & \bfseries (baseline) & \bfseries $V=0.8$~nm$^3$ & \bfseries $V=1.2$~nm$^3$ & \bfseries $V=1.2$~nm$^3$ \\"
    + "\n"
)
latex += (
    r"\bfseries & \bfseries $T=295$~K & \bfseries $T=295$~K & \bfseries $T=295$~K & \bfseries $T=77$~K \\"
    + "\n"
)
latex += r"\midrule" + "\n"

latex += "Number of trajectories $n_{\\rm traj}$ & 2 & 100 & 20 & 2\\\\\n"
latex += "System size & 8$\\times$8 & 9$\\times$9 & 9$\\times$9 & 9$\\times$9\\\\\n"
latex += "Site energy disorder $\\sigma$ (cm$^{-1}$) & 50 & 50 & 50 & 50\\\\\n"
latex += "Trapping rate $\\Gamma_{\\rm RC}$ (ps$^{-1}$) & 0.15 & 0.15 & 0.15 & 0.15\\\\\n"
latex += "\\midrule\n"

latex += "\\bfseries Trapping yield $\\Phi_{\\rm FT}$"
latex += " & \\bfseries " + f4(rc_base[-1])
latex += " & \\bfseries " + f4(rc_v08[-1])
latex += " & \\bfseries " + f4(rc_v12[-1])
latex += " & \\bfseries " + f4(rc_77k[-1]) + " \\\\\n"
latex += "\\midrule\n"

latex += "Trapping sites (3+4) max. population"
latex += " & " + f4(trap_base)
latex += " & " + f4(trap_v08)
latex += " & " + f4(trap_v12)
latex += " & " + f4(trap_77k) + "\\\\\n"

latex += "Site~1 final population"
latex += " & " + f4(site1_base)
latex += " & " + f4(site1_v08)
latex += " & " + f4(site1_v12)
latex += " & " + f4(site1_77k) + "\\\\\n"

latex += "Site~6 final population"
latex += " & " + f4(site6_base)
latex += " & " + f4(site6_v08)
latex += " & " + f4(site6_v12)
latex += " & " + f4(site6_77k) + "\\\\\n"

latex += "Plasmon mode final population"
latex += " & ---"
latex += " & " + f4(plasmon_v08)
latex += " & " + f4(plasmon_v12)
latex += " & " + f4(plasmon_77k) + "\\\\\n"

latex += "Population trace $\\mu\\pm\\sigma$"
latex += " & " + f4(trace_base.mean()) + "$\\pm$" + f6(trace_base.std())
latex += " & " + f4(trace_v08.mean()) + "$\\pm$" + f6(trace_v08.std())
latex += " & " + f4(trace_v12.mean()) + "$\\pm$" + f6(trace_v12.std())
latex += " & " + f4(trace_77k.mean()) + "$\\pm$" + f6(trace_77k.std()) + "\\\\\n"

latex += "\\midrule\n"
latex += "SERS enhancement factor EF"
latex += " & --- & " + str(ef_v08) + " & " + str(ef_v12) + " & " + str(ef_77k) + "\\\\\n"

latex += "Figure of merit $\\Phi_{\\rm FT}\\times\\mathrm{EF}$"
latex += " & ---"
latex += " & " + f2(fom_v08)
latex += " & " + f2(fom_v12)
latex += " & " + f2(fom_77k) + "\\\\\n"

latex += "\\bottomrule\n"
latex += "\\end{tabular}\n"
latex += "\\end{table*}\n"

print(latex)

output_dir = "Redac_Paper2/Submission_Package_Nature_Energy_Manuscript"
os.makedirs(output_dir, exist_ok=True)
out_path = os.path.join(output_dir, "table_comparative_4runs.tex")
with open(out_path, "w") as f:
    f.write(latex)
print(f"LaTeX table saved to: {out_path}")

# Also print markdown table
print()
print("=" * 70)
print("MARKDOWN TABLE")
print("=" * 70)
header = "| Metric | NPoM OFF | V=0.8 295K | V=1.2 295K | V=1.2 77K |"
sep = "|:-------|:--------:|:----------:|:----------:|:---------:|"
print(header)
print(sep)
print(
    f"| Phi_FT | {f4(rc_base[-1])} | {f4(rc_v08[-1])} | {f4(rc_v12[-1])} | **{f4(rc_77k[-1])}** |"
)
print(f"| Trap (3+4) max | {f4(trap_base)} | {f4(trap_v08)} | {f4(trap_v12)} | {f4(trap_77k)} |")
print(f"| Site 1 final | {f4(site1_base)} | {f4(site1_v08)} | {f4(site1_v12)} | {f4(site1_77k)} |")
print(f"| Plasmon final | --- | {f4(plasmon_v08)} | {f4(plasmon_v12)} | {f4(plasmon_77k)} |")
print(
    f"| Trace mu | {f4(trace_base.mean())} | {f4(trace_v08.mean())} | {f4(trace_v12.mean())} | {f4(trace_77k.mean())} |"
)
print(
    f"| Trace sigma | {f6(trace_base.std())} | {f6(trace_v08.std())} | {f6(trace_v12.std())} | {f6(trace_77k.std())} |"
)
print(f"| EF_SERS | --- | {ef_v08} | {ef_v12} | {ef_77k} |")
print(f"| FOM | --- | {f2(fom_v08)} | {f2(fom_v12)} | {f2(fom_77k)} |")
