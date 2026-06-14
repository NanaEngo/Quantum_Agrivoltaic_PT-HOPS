# Quantum-Enhanced Agrivoltaics: Spectral Bath Engineering via Non-Markovian Dynamics
> Last updated: 2026-05-13

Research framework, simulation codebase, and manuscript source for the **JPCL Major Revision** (jz-2026-00994t).

## 📄 Manuscript Status

- **Status**: ✅ **Submission Ready** (Revision submitted May 13, 2026)
- **Target Journal**: *The Journal of Physical Chemistry Letters* (JPCL)
- **Primary Objective**: Leveraging non-Markovian coherence in the FMO complex to enhance photosynthetic energy transfer under semi-transparent OPVs via selective vibronic excitation.

---

## 🛠 Project Structure

```text
Redac_Paper1/
├── Theory_Journals_main/JPCL/     # Manuscript & SI (JPCL dated filenames)
├── quantum_simulations_framework_parallel_260512/ # Production Codebase
│   ├── parameters.yaml            # Single source of truth for physics
│   ├── reproducibility/main.py    # Production pipeline orchestrator
│   └── reproducibility/audit_convergence.py # Convergence verification
└── COMPREHENSIVE_AUDIT_REPORT.md    # Definitive technical audit
```

---

## 🚀 "Good Commands" (Quick Reference)

### 1. Simulation Workflows

```bash
# Activate environment
mamba activate MesoHOP-sim

# Run Production Ensemble (L=8, K=2, 100 trajectories)
mamba run -n MesoHOP-sim python quantum_simulations_framework_parallel_260512/reproducibility/main.py --parallel --skip-audit

# Run Verification Suite (23-point Validation)
mamba run -n MesoHOP-sim pytest tests/ -v
```

### 2. Monitoring & Forensics

```bash
# Follow the execution log
tail -f quantum_simulations_framework_parallel_260512/reproducibility/logs/execution_*.log

# Check for convergence errors
grep "FATAL" quantum_simulations_framework_parallel_260512/reproducibility/logs/*.log
```

### 3. Manuscript Compilation

```bash
cd Theory_Journals_main/JPCL/
# Compile main manuscript and Supporting Information
latexmk -pdf Manuscript_JPCL_26-05-13.tex SI_JPCL_26-05-13.tex
```

---

## 📑 Key Research Contributions (JPCL Revision)

1. **Selective Vibronic Excitation**: Demonstrated that the 12-mode Kleinekathöfer bath can be leveraged for quantum control of exciton transport.
2. **PT-HOPS & SBD Convergence**: Rigorous proof of hierarchy stability at $L=8, K=2$ (MAE $\approx \num{3.10e-11}$) for room-temperature FMO dynamics.
3. **Environmental Robustness**: Validated the stability of quantum-enhanced transport under static disorder ($\sigma = \qty{50}{\per\centi\meter}$) and temperature sweeps ($T = \qtyrange{275}{315}{\kelvin}$).
4. **Memory-Aware Scheduling**: Integrated a hardware-aware parallelization engine managing the \qty{54}{\giga\byte} RAM footprint per HOPS trajectory.

---

## 🤝 Contact

**Corresponding Author**: Steve Cabrel Teguia Kouam ([steve.teguia@facsciences-uy1.cm](mailto:steve.teguia@facsciences-uy1.cm))
**HPC Optimization**: Parallel framework optimized for \qty{128}{GB} RAM workstation and cluster environments.
