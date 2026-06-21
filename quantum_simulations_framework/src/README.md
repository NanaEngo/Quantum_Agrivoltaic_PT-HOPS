# Simulation Framework Architecture (`src/`)

This directory contains the modular source code for the Quantum Agrivoltaic 
PT-HOPS framework. The architecture is designed for high-performance non-Markovian 
dynamics, supporting both CPU-based stochastic trajectory methods and GPU-accelerated 
ensemble averaging.

---

## 📂 Domain-Driven Structure

### 1. `core/` — Numerical Foundations
- **`hops_simulator.py`**: The primary orchestrator for PT-HOPS/SBD trajectory generation.
- **`hamiltonian_factory.py`**: High-precision exciton-vibronic Hamiltonian construction for photosynthetic complexes.
- **`memory_manager.py`**: `MemoryAwareJobScheduler` — OOM prevention with RLIMIT_AS per worker.
- **`constants.py`**: Centralized physical constants ($k_B$, $\hbar$) and unit conversions.

### 2. `quantum/` — Advanced Dynamics
- **`analysis.py`**: Metrics for population kinetics, quantum coherence, and energy transfer efficiency (ETE).
- **`spectroscopy.py`**: Simulated linear absorption and 2D electronic spectroscopy (2DES) signals.
- **`spectral_optimization.py`**: Algorithms for engineering bath spectral densities to maximize transport.

### 3. `agrivoltaic/` — Photosynthetic Models
- **`coupling_model.py`**: Theoretical bridge between exciton dynamics and photovoltaic yield metrics.
- **`environmental_factors.py`**: Modeling of static/dynamic temperature and spectral irradiance effects.
- **`biodegradability_analyzer.py`**: Environmental impact assessment for material sustainability.

### 4. `extensions/` — Solver Enhancements
- **`stochastic_bundling.py`**: Implementation of Stochastically Bundled Dissipators (SBD) for hierarchy compression.
- **`mesohops_adapters.py`**: Version-agnostic adapters for the underlying MesoHOPS solver suite.

### 5. `io/` & `visualization/`
- **`csv_storage.py`**: Hardened serialization with SHA-256 metadata integrity and Git-provenance tracking.
- **`figure_generator.py`**: Publication-grade plotting engine (600 DPI) using the JPCL aesthetic theme.

---

### 6. `utils/` — Infrastructure
- **`parallel_utils.py`**: Memory-aware job count estimation (`estimate_memory_per_traj`, `get_safe_n_jobs`).
- **`gpu_detection.py`**: Unified GPU hardware detection (JAX, CuPy, PyTorch, nvidia-smi).
- **`logging_config.py`**: Structured logging with rotation and test-failure capture.

---

## 📜 Development Standards

- **Numerical Integrity:** Strict enforcement of $L \ge 8, K \ge 2$ for all production-grade simulations.
- **Code Style:** All documentation follows the **NumPy Docstring Format**.
- **Type Safety:** Python 3.10+ static typing (mypy) is utilized throughout the API surface.
- **Coordinate Systems:** Energy is standardized in cm⁻¹, time in femtoseconds (fs), and temperature in Kelvin (K).

---
**Last Updated:** 2026-05-11  
**Status:** Canonical Framework (v1.6-production)

