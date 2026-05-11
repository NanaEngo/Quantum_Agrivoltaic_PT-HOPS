# Comprehensive Codebase Restructuring Proposal — 2026-05-10

## Executive Summary

The codebase is **rich and feature-complete** but suffers from **organizational fragmentation**. This proposal outlines a coherent restructuring strategy to improve:

1. **Coherency** — Clear logical organization and relationships
2. **Completeness** — All related functionality grouped together
3. **Consistency** — Uniform patterns and conventions

---

## 🔍 Current State Analysis

### Strengths
- ✅ Rich feature set (quantum dynamics, agrivoltaics, LCA, etc.)
- ✅ Comprehensive test suite (31 tests + 5 audits)
- ✅ Multiple simulation backends (MesoHOPS, GPU, simple)
- ✅ Production-grade reproducibility pipeline
- ✅ Well-documented constants and configurations

### Weaknesses
- ❌ **Scattered responsibilities** — Models directory has 13 unrelated modules
- ❌ **Unclear dependencies** — No clear module hierarchy
- ❌ **Mixed concerns** — Analysis, simulation, and optimization mixed together
- ❌ **Inconsistent naming** — `quantum_dynamics_simulator` vs `simple_quantum_dynamics_simulator`
- ❌ **Orphaned code** — `scratch/`, `simulations/`, `orca_work/` directories unclear
- ❌ **Monolithic modules** — `quantum_dynamics_simulator.py` (~1000 LOC)
- ❌ **Duplicate utilities** — Multiple figure generation, data storage approaches
- ❌ **Unclear entry points** — Multiple main files (`main.py`, `main_parallel.py`, notebooks)

---

## 📊 Current Structure Issues

### Models Directory (13 modules, unclear organization)
```
models/
├── quantum_dynamics_simulator.py          # Core simulation
├── simple_quantum_dynamics_simulator.py   # Fallback
├── quantum_analysis.py                    # Analysis
├── spectral_optimizer.py                  # Optimization
├── agrivoltaic_coupling_model.py          # Domain-specific
├── environmental_factors.py               # Domain-specific
├── lca_analyzer.py                        # Domain-specific
├── biodegradability_analyzer.py           # Domain-specific
├── eco_design_analyzer.py                 # Domain-specific
├── techno_economic_model.py               # Domain-specific
├── sensitivity_analyzer.py                # Analysis
├── multi_scale_transformer.py             # Transformation
└── spectroscopy_2des.py                   # Analysis
```

**Problem:** No clear separation of concerns. Quantum dynamics, analysis, optimization, and domain models all mixed.

### Utils Directory (11 modules, unclear organization)
```
utils/
├── csv_data_storage.py                    # Data I/O
├── figure_generator.py                    # Visualization
├── generate_figures.py                    # Visualization (duplicate?)
├── generate_fmo_schematic.py              # Visualization
├── logging_config.py                      # Logging
├── orca_wrapper.py                        # External tool
├── parallel_utils.py                      # Parallelization
├── patch_notebook_standardization.py      # Notebook utilities
├── sync_ipynb.py                          # Notebook utilities
├── theme.py                               # Visualization
└── import_standardizer.py                 # Import management
```

**Problem:** Utilities are too diverse. Should be split by domain.

### Reproducibility Directory (Mixed concerns)
```
reproducibility/
├── main.py                                # Production pipeline
├── main_parallel.py                       # Parallel variant
├── audit_convergence.py                   # Convergence auditing
├── check_env.py                           # Environment checking
├── optimize.py                            # Optimization
├── run_temp_sweep_only.py                 # Temperature sweep
├── run_temp_sweep_cluster.sh              # Cluster script
└── logs/, results/                        # Output directories
```

**Problem:** Multiple entry points, unclear which is canonical. Mixing pipeline, auditing, and optimization.

### Root Directory (Too many files)
```
├── parameters.yaml, laptop_parameters.yaml, parallel_config.yaml  # Config files
├── main.py, main_parallel.py                                      # Entry points
├── refactor.py, refactor_script.py                                # Refactoring scripts
├── run_cluster.sh                                                 # Cluster script
├── quantum_coherence_agrivoltaics_mesohops_complete.py           # Monolithic script
├── REFACTORING_*.md, COMPLETION_REPORT.md, etc.                  # Documentation
└── pytest.ini                                                     # Test config
```

**Problem:** Root directory cluttered with scripts, configs, and documentation.

---

## 🎯 Proposed New Structure

### Tier 1: Clear Separation of Concerns

```
quantum_simulations_framework_parallel_260509/
│
├── src/                                    # Source code (production)
│   ├── core/                               # Core quantum dynamics
│   ├── quantum/                            # Quantum-specific modules
│   ├── agrivoltaic/                        # Agrivoltaic domain
│   ├── analysis/                           # Analysis tools
│   ├── optimization/                       # Optimization tools
│   ├── io/                                 # Data I/O
│   └── visualization/                      # Visualization
│
├── pipelines/                              # Reproducibility pipelines
│   ├── jpcl_resubmission/                  # JPCL submission pipeline
│   ├── convergence_audit/                  # Convergence auditing
│   └── temperature_sweep/                  # Temperature sweep pipeline
│
├── tests/                                  # Test suite
│   ├── unit/                               # Unit tests
│   ├── integration/                        # Integration tests
│   └── fixtures/                           # Test fixtures
│
├── config/                                 # Configuration files
│   ├── parameters.yaml                     # Production config
│   ├── laptop_parameters.yaml              # Development config
│   └── parallel_config.yaml                # Parallel config
│
├── data/                                   # Data directories
│   ├── input/                              # Input data
│   ├── converged/                          # Converged results
│   └── simulations/                        # Simulation outputs
│
├── notebooks/                              # Jupyter notebooks
│   ├── colab/                              # Colab notebooks
│   └── analysis/                           # Analysis notebooks
│
├── docs/                                   # Documentation
│   ├── api/                                # API documentation
│   ├── guides/                             # User guides
│   └── architecture/                       # Architecture docs
│
├── scripts/                                # Utility scripts
│   ├── setup/                              # Setup scripts
│   ├── maintenance/                        # Maintenance scripts
│   └── cluster/                            # Cluster scripts
│
└── .github/                                # GitHub configuration
    └── workflows/                          # CI/CD workflows
```

---

## 📦 Detailed Module Organization

### 1. `src/core/` — Core Quantum Dynamics
**Purpose:** Low-level quantum simulation infrastructure

```
core/
├── __init__.py
├── constants.py                           # Physical constants
├── hamiltonian_factory.py                 # Hamiltonian construction
├── hops_simulator.py                      # Main HOPS simulator
├── gpu_dynamics.py                        # GPU acceleration
├── bath_correlation.py                    # Bath correlation functions (NEW)
├── hierarchy.py                           # Hierarchy management (NEW)
└── integrators.py                         # Integration methods (NEW)
```

**Responsibility:** Pure quantum dynamics, no domain-specific logic.

---

### 2. `src/quantum/` — Quantum Analysis & Metrics
**Purpose:** Quantum information analysis

```
quantum/
├── __init__.py
├── analysis.py                            # Quantum analysis suite (from quantum_analysis.py)
├── metrics.py                             # Quantum metrics (coherence, QFI, entropy)
├── spectroscopy.py                        # 2D spectroscopy (from spectroscopy_2des.py)
├── spectral_optimization.py               # Spectral optimization (from spectral_optimizer.py)
└── multi_scale.py                         # Multi-scale transformation (from multi_scale_transformer.py)
```

**Responsibility:** Quantum-specific analysis and optimization.

---

### 3. `src/agrivoltaic/` — Agrivoltaic Domain
**Purpose:** Agrivoltaic-specific models and analysis

```
agrivoltaic/
├── __init__.py
├── coupling_model.py                      # Coupling model (from agrivoltaic_coupling_model.py)
├── environmental_factors.py               # Environmental effects
├── lca_analyzer.py                        # Life cycle assessment
├── biodegradability_analyzer.py           # Biodegradability analysis
├── eco_design_analyzer.py                 # Ecological design analysis
└── techno_economic_model.py               # Techno-economic analysis
```

**Responsibility:** Domain-specific models and analysis.

---

### 4. `src/analysis/` — General Analysis Tools
**Purpose:** Cross-domain analysis utilities

```
analysis/
├── __init__.py
├── sensitivity_analyzer.py                # Sensitivity analysis
├── convergence_analyzer.py                # Convergence analysis (NEW)
├── performance_analyzer.py                # Performance analysis (NEW)
└── statistical_analyzer.py                # Statistical analysis (NEW)
```

**Responsibility:** General-purpose analysis tools.

---

### 5. `src/optimization/` — Optimization Tools
**Purpose:** Optimization algorithms and strategies

```
optimization/
├── __init__.py
├── spectral_optimizer.py                  # Spectral optimization
├── parameter_optimizer.py                 # Parameter optimization (NEW)
└── ensemble_optimizer.py                  # Ensemble optimization (NEW)
```

**Responsibility:** Optimization algorithms.

---

### 6. `src/io/` — Data I/O
**Purpose:** Data storage, loading, and management

```
io/
├── __init__.py
├── csv_storage.py                         # CSV data storage (from csv_data_storage.py)
├── hdf5_storage.py                        # HDF5 storage (NEW)
├── metadata.py                            # Metadata management (NEW)
└── validators.py                          # Data validation (NEW)
```

**Responsibility:** Data I/O and validation.

---

### 7. `src/visualization/` — Visualization
**Purpose:** Plotting and figure generation

```
visualization/
├── __init__.py
├── figure_generator.py                    # Main figure generator
├── fmo_schematic.py                       # FMO schematic (from generate_fmo_schematic.py)
├── theme.py                               # Plotting theme
├── colors.py                              # Color schemes (NEW)
└── formatters.py                          # Plot formatters (NEW)
```

**Responsibility:** All visualization and plotting.

---

### 8. `src/extensions/` — External Integrations
**Purpose:** Adapters for external tools

```
extensions/
├── __init__.py
├── mesohops_adapters.py                   # MesoHOPS integration
├── stochastic_bundling.py                 # SBD integration
├── orca_wrapper.py                        # ORCA integration (moved from utils)
└── gpu_backends.py                        # GPU backend adapters (NEW)
```

**Responsibility:** External tool integration.

---

### 9. `pipelines/` — Reproducibility Pipelines
**Purpose:** Complete reproducible workflows

```
pipelines/
├── __init__.py
├── jpcl_resubmission/
│   ├── __init__.py
│   ├── main.py                            # Main pipeline (from reproducibility/main.py)
│   ├── config.py                          # Pipeline configuration (NEW)
│   └── stages.py                          # Pipeline stages (NEW)
├── convergence_audit/
│   ├── __init__.py
│   ├── audit.py                           # Convergence audit (from audit_convergence.py)
│   └── validators.py                      # Audit validators (NEW)
└── temperature_sweep/
    ├── __init__.py
    ├── sweep.py                           # Temperature sweep (from run_temp_sweep_only.py)
    └── analysis.py                        # Sweep analysis (NEW)
```

**Responsibility:** Complete reproducible workflows.

---

### 10. `tests/` — Test Suite
**Purpose:** Comprehensive testing

```
tests/
├── __init__.py
├── conftest.py                            # Pytest configuration
├── unit/
│   ├── test_core.py
│   ├── test_quantum.py
│   ├── test_agrivoltaic.py
│   ├── test_analysis.py
│   ├── test_io.py
│   └── test_visualization.py
├── integration/
│   ├── test_jpcl_pipeline.py
│   ├── test_convergence_audit.py
│   ├── test_temperature_sweep.py
│   └── test_full_pipeline.py
├── fixtures/
│   ├── conftest.py
│   ├── hamiltonian_fixtures.py
│   ├── config_fixtures.py
│   └── data_fixtures.py
└── performance/
    ├── test_performance.py
    └── benchmarks.py
```

**Responsibility:** All testing.

---

## 🔄 Migration Strategy

### Phase 1: Preparation (Week 1)
- [ ] Create new directory structure
- [ ] Create migration mapping document
- [ ] Set up CI/CD for parallel testing
- [ ] Create migration scripts

### Phase 2: Core Migration (Week 2-3)
- [ ] Move `core/` modules (no changes needed)
- [ ] Move `extensions/` modules
- [ ] Create `src/` structure
- [ ] Update imports in moved files

### Phase 3: Quantum Modules (Week 3-4)
- [ ] Create `src/quantum/` and move modules
- [ ] Consolidate analysis modules
- [ ] Update imports
- [ ] Run tests

### Phase 4: Domain Modules (Week 4-5)
- [ ] Create `src/agrivoltaic/` and move modules
- [ ] Create `src/analysis/` and move modules
- [ ] Create `src/optimization/` and move modules
- [ ] Update imports

### Phase 5: I/O & Visualization (Week 5-6)
- [ ] Create `src/io/` and move modules
- [ ] Create `src/visualization/` and move modules
- [ ] Consolidate duplicate utilities
- [ ] Update imports

### Phase 6: Pipelines (Week 6-7)
- [ ] Create `pipelines/` structure
- [ ] Move reproducibility scripts
- [ ] Refactor into pipeline stages
- [ ] Update imports

### Phase 7: Configuration & Documentation (Week 7-8)
- [ ] Reorganize config files
- [ ] Create comprehensive documentation
- [ ] Update README and guides
- [ ] Final testing

### Phase 8: Cleanup & Deployment (Week 8-9)
- [ ] Remove old directories
- [ ] Archive scratch code
- [ ] Final validation
- [ ] Deploy to production

---

## 🎯 Key Improvements

### 1. Coherency
**Before:** Unclear relationships between modules  
**After:** Clear hierarchical organization with explicit dependencies

### 2. Completeness
**Before:** Related functionality scattered across directories  
**After:** All related functionality grouped together

### 3. Consistency
**Before:** Inconsistent naming and patterns  
**After:** Uniform naming conventions and design patterns

### 4. Maintainability
**Before:** Difficult to locate and modify functionality  
**After:** Clear module boundaries and responsibilities

### 5. Testability
**Before:** Mixed unit and integration tests  
**After:** Organized test structure with clear test types

### 6. Scalability
**Before:** Difficult to add new features  
**After:** Clear extension points for new functionality

---

## 📋 Naming Conventions

### Module Naming
- **Singular nouns** for modules: `analysis.py`, not `analyzers.py`
- **Descriptive names**: `bath_correlation.py`, not `bc.py`
- **Consistent suffixes**: `_analyzer.py`, `_optimizer.py`, `_simulator.py`

### Class Naming
- **PascalCase** for classes: `BathCorrelationDecomposer`
- **Descriptive names**: `QuantumMetricsAnalyzer`, not `QMA`
- **Consistent patterns**: `*Analyzer`, `*Optimizer`, `*Simulator`

### Function Naming
- **snake_case** for functions: `calculate_coherence()`
- **Verb-first**: `run_simulation()`, not `simulation_run()`
- **Consistent prefixes**: `calculate_*`, `run_*`, `validate_*`

---

## 🔗 Dependency Graph

### Tier 1: Core (No dependencies on other tiers)
```
core/
  ├── constants.py
  ├── hamiltonian_factory.py
  ├── bath_correlation.py
  ├── hierarchy.py
  └── integrators.py
```

### Tier 2: Extensions (Depends on Tier 1)
```
extensions/
  ├── mesohops_adapters.py (depends on core)
  ├── stochastic_bundling.py (depends on core)
  └── gpu_backends.py (depends on core)
```

### Tier 3: Quantum & Analysis (Depends on Tier 1-2)
```
quantum/
  ├── analysis.py (depends on core)
  ├── metrics.py (depends on core)
  └── spectroscopy.py (depends on core)

analysis/
  ├── sensitivity_analyzer.py (depends on core)
  └── convergence_analyzer.py (depends on core)
```

### Tier 4: Domain (Depends on Tier 1-3)
```
agrivoltaic/
  ├── coupling_model.py (depends on core, quantum)
  ├── environmental_factors.py (depends on core)
  └── lca_analyzer.py (depends on analysis)
```

### Tier 5: I/O & Visualization (Depends on Tier 1-4)
```
io/
  ├── csv_storage.py (depends on core)
  └── validators.py (depends on core)

visualization/
  ├── figure_generator.py (depends on quantum, analysis)
  └── theme.py (no dependencies)
```

### Tier 6: Pipelines (Depends on all tiers)
```
pipelines/
  ├── jpcl_resubmission/ (depends on all)
  ├── convergence_audit/ (depends on core, analysis)
  └── temperature_sweep/ (depends on core, quantum)
```

---

## 📊 Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Coherency** | Scattered | Hierarchical |
| **Completeness** | Fragmented | Grouped |
| **Consistency** | Inconsistent | Uniform |
| **Maintainability** | Difficult | Easy |
| **Testability** | Mixed | Organized |
| **Scalability** | Limited | Extensible |
| **Documentation** | Unclear | Clear |
| **Onboarding** | Steep | Gentle |

---

## 🚀 Implementation Roadmap

### Immediate (This Sprint)
- [ ] Create new directory structure
- [ ] Create migration mapping
- [ ] Set up CI/CD for parallel testing

### Short Term (Next 2 Sprints)
- [ ] Migrate core modules
- [ ] Migrate quantum modules
- [ ] Update all imports

### Medium Term (Next 4 Sprints)
- [ ] Migrate domain modules
- [ ] Migrate I/O and visualization
- [ ] Migrate pipelines

### Long Term (Next 8 Sprints)
- [ ] Complete cleanup
- [ ] Comprehensive documentation
- [ ] Performance optimization
- [ ] Production deployment

---

## 📝 Documentation Updates

### New Documentation Files
1. **ARCHITECTURE.md** — Overall architecture and design
2. **MODULE_GUIDE.md** — Guide to each module
3. **MIGRATION_GUIDE.md** — Step-by-step migration guide
4. **DEPENDENCY_GRAPH.md** — Module dependencies
5. **NAMING_CONVENTIONS.md** — Naming standards

### Updated Documentation Files
1. **README.md** — Update with new structure
2. **QUICKSTART.md** — Update with new paths
3. **CONTRIBUTING.md** — Update with new guidelines

---

## ✨ Conclusion

This restructuring will transform the codebase from a **rich but fragmented** collection of modules into a **coherent, complete, and consistent** framework. The hierarchical organization will improve:

- **Developer experience** — Clear module organization
- **Code quality** — Consistent patterns and conventions
- **Maintainability** — Easy to locate and modify code
- **Scalability** — Clear extension points
- **Testing** — Organized test structure
- **Documentation** — Clear module responsibilities

**Estimated Effort:** 8-9 weeks  
**Risk Level:** Low (backward compatible migration)  
**Expected ROI:** High (improved maintainability and scalability)

---

**Restructuring Proposal — 2026-05-10**  
**Status:** Ready for review and approval  
**Next Step:** Create detailed migration plan
