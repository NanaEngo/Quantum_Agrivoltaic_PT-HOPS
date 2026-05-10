# Quantum-Enhanced Agrivoltaics: Spectral Bath Engineering via Non-Markovian Dynamics

Research framework, simulation codebase, and manuscript source for the **JPCL Major Revision** (jz-2026-00994t).

## 📄 Manuscript Status

- **Status**: Major Revision in progress (deadline: 28-May-2026)
- **Target Journal**: *The Journal of Physical Chemistry Letters* (JPCL)
- **Primary Objective**: Leveraging non-Markovian coherence in the FMO complex to enhance photosynthetic ETR under semi-transparent OPVs via selective vibronic excitation.

---

## 🛠 Project Structure

```text
Redac_Paper1/
├── Theory_Journals_main/JPCL/     # Manuscript & SI (JPCL dated filenames)
├── quantum_simulations_framework_parallel_260509/ # Production Codebase
│   ├── parameters.yaml            # Single source of truth for physics
│   ├── reproducibility/main.py    # Production pipeline orchestrator
│   └── tests/                     # 12-test validation suite
└── simulation_data/                 # Archived simulation results
```

---

## 🚀 "Good Commands" (Quick Reference)

### 1. Simulation Workflows

```bash
# Activate environment
mamba activate MesoHOP-sim

# Run Production Ensemble (L=8, K=2, 100 trajectories)
mamba run -n MesoHOP-sim python quantum_simulations_framework_parallel_260509/reproducibility/main.py --parallel --skip-audit

# Run Verification Suite (SI Validation)
mamba run -n MesoHOP-sim pytest quantum_simulations_framework_parallel_260509/tests/ -v
```

### 2. Monitoring & Forensics

```bash
# Follow the execution log
tail -f quantum_simulations_framework_parallel_260509/reproducibility/logs/execution_*.log

# Check for convergence errors
grep "FATAL" quantum_simulations_framework_parallel_260509/reproducibility/logs/*.log
```

### 3. Manuscript Compilation

```bash
cd Theory_Journals_main/JPCL/
latexmk -pdf Manuscript_JPCL_26-05-08.tex SI_JPCL_26-05-08.tex
```

---

## 📑 Key Research Contributions (JPCL Revision)

1. **Selective Vibronic Excitation**: Demonstrated that the 12-mode Kleinekathöfer bath can be leveraged for quantum control of exciton transport.
2. **PT-HOPS & SBD Convergence**: Rigorous proof of hierarchy stability at $L=8, K=2$ for room-temperature FMO dynamics.
3. **Environmental Robustness**: Validated the stability of quantum-enhanced ETR under static disorder ($\sigma = 50$ cm$^{-1}$) and temperature sweeps.
4. **Synchronized Parameters**: Elimination of magic numbers through a centralized `parameters.yaml` architecture.

---

## 🤝 Contact

**Corresponding Author**: Steve Cabrel Teguia Kouam ([steve.teguia@facsciences-uy1.cm](mailto:steve.teguia@facsciences-uy1.cm))
**HPC Optimization**: Parallel/GPU framework optimized for 128GB RAM/RTX A4000 systems.