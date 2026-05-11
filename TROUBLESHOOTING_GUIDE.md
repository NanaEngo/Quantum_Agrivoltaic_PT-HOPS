# Comprehensive Troubleshooting Guide

This guide covers common issues and solutions for testing and running the quantum simulations framework.

---

## Environment Issues

### Issue: "MesoHOPS NOT found" or ImportError

**Symptoms:**
```
ImportError: No module named 'mesohops'
ERROR: MesoHOPS not found in environment
```

**Solutions:**

1. **Verify conda environment exists:**
   ```bash
   mamba env list | grep MesoHOP-sim
   ```
   If not listed, create it:
   ```bash
   mamba create -n MesoHOP-sim python=3.10
   mamba activate MesoHOP-sim
   mamba install mesohops numpy scipy matplotlib
   ```

2. **Verify MesoHOPS is installed:**
   ```bash
   mamba run -n MesoHOP-sim python -c "import mesohops; print(mesohops.__version__)"
   ```
   If error, reinstall:
   ```bash
   mamba install -n MesoHOP-sim mesohops --force-reinstall
   ```

3. **Check PYTHONPATH:**
   ```bash
   mamba run -n MesoHOP-sim python -c "import sys; print(sys.path)"
   ```
   Should include framework directory. If not, add it:
   ```bash
   export PYTHONPATH="/path/to/framework:$PYTHONPATH"
   ```

4. **Use mamba run wrapper:**
   ```bash
   # Instead of:
   python main.py
   
   # Use:
   mamba run -n MesoHOP-sim python main.py
   ```

---

## Test Execution Issues

### Issue: Tests hang or timeout

**Symptoms:**
```
TIMEOUT: test_quantum_dynamics_simulator exceeded 60.00s timeout
Hanging at: "Starting integration..."
```

**Solutions:**

1. **Use timeout flag:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/ -v --timeout=60
   ```

2. **Run individual test with verbose output:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/test_models_dynamics.py::test_quantum_dynamics_simulator -v -s
   ```

3. **Skip slow tests:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/ -v -k "not test_full_pipeline_flow and not test_quantum_dynamics_simulator"
   ```

4. **Run laptop suite instead:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/test_laptop_suite.py -v
   ```

5. **Check system resources:**
   ```bash
   free -h  # Check available RAM
   top     # Check CPU usage
   ```

---

### Issue: Out of Memory (OOM) during tests

**Symptoms:**
```
MemoryError: Unable to allocate X.XX GiB for an array
Killed (process killed by system)
```

**Solutions:**

1. **Run laptop suite (uses <500 MB):**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/test_laptop_suite.py -v
   ```

2. **Skip memory-intensive tests:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/ -v -k "not test_hops_simulator_simulation_stub"
   ```

3. **Check available memory:**
   ```bash
   free -h
   ```
   If <2 GB available, close other applications

4. **Reduce test parameters in config:**
   ```yaml
   # In laptop_parameters.yaml
   dynamics:
     L_max: 2          # Reduce from 8
     matsubara_truncation: 1  # Reduce from 2
     n_traj: 5         # Reduce from 100
   ```

5. **Run tests sequentially:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/ -v -n 1
   ```

---

### Issue: Test assertion failures

**Symptoms:**
```
AssertionError: assert np.allclose(traces, 1.0, atol=0.01) failed
Trace range: [0.85, 1.15]
```

**Solutions:**

1. **Check trace preservation tolerance:**
   - Laptop suite uses `atol=0.15` (loose)
   - Production uses `atol=0.01` (strict)
   - This is expected due to reduced parameters

2. **Verify simulation parameters:**
   ```bash
   grep -r "atol=" tests/
   ```

3. **Check if using laptop suite:**
   ```bash
   # Laptop suite (loose tolerance)
   mamba run -n MesoHOP-sim pytest tests/test_laptop_suite.py -v
   
   # Full suite (strict tolerance)
   mamba run -n MesoHOP-sim pytest tests/ -v
   ```

4. **Review test logs:**
   ```bash
   tail -100 reproducibility/logs/tests_*.log
   ```

---

### Issue: Mock/patch errors in integration tests

**Symptoms:**
```
AssertionError: assert_called_once() failed
AttributeError: 'MagicMock' object has no attribute 'assert_called_with'
```

**Solutions:**

1. **Apply fixes from QUICK_FIX_GUIDE.md:**
   - Fix #1: test_config_validation_failure
   - Fix #2: test_environment_check
   - Fix #3: test_full_pipeline_flow
   - Fix #4: test_pipeline_exits_on_no_mesohops

2. **Verify patches are correct:**
   ```python
   # Check patch target
   @patch("reproducibility.main.load_and_validate_config")
   # NOT: @patch("load_and_validate_config")
   ```

3. **Check decorator order:**
   ```python
   # Decorators are applied bottom-to-top
   @patch("A")
   @patch("B")
   def test(mock_b, mock_a):  # Note: reversed order
       pass
   ```

---

## Configuration Issues

### Issue: "Config validation failed" or "L_max too small"

**Symptoms:**
```
ValueError: L_max must be >= 8 (got 4)
```

**Solutions:**

1. **Check config file:**
   ```bash
   cat Redac_Paper1/quantum_simulations_framework_parallel_260509/parameters.yaml | grep L_max
   ```

2. **Use laptop config for testing:**
   ```bash
   mamba run -n MesoHOP-sim python reproducibility/main.py --config laptop_parameters.yaml
   ```

3. **Verify config is valid YAML:**
   ```bash
   python -c "import yaml; yaml.safe_load(open('parameters.yaml'))"
   ```

4. **Check for typos:**
   ```bash
   # Should be L_max, not L or max_L
   grep -E "L_max|L:|max_L" parameters.yaml
   ```

---

### Issue: "Bath parameters not found" or KeyError

**Symptoms:**
```
KeyError: 'reorganization_energy'
KeyError: 'vibronic_frequencies'
```

**Solutions:**

1. **Verify config has all required keys:**
   ```bash
   python -c "
   import yaml
   cfg = yaml.safe_load(open('parameters.yaml'))
   required = ['bath', 'dynamics', 'simulation']
   for key in required:
       if key not in cfg:
           print(f'Missing: {key}')
   "
   ```

2. **Check bath section:**
   ```yaml
   bath:
     temperature: 295.0
     reorganization_energy: 35.0
     drude_cutoff: 500.0
     vibronic_frequencies: [100.0, 200.0]
     huang_rhys_factors: [0.1, 0.05]
     vibronic_damping: [10.0, 20.0]
   ```

3. **Use default config:**
   ```bash
   cp parameters.yaml parameters.yaml.bak
   # Restore from git
   git checkout parameters.yaml
   ```

---

## Performance Issues

### Issue: Tests are very slow

**Symptoms:**
```
test_quantum_dynamics_simulator PASSED in 420.50s
```

**Solutions:**

1. **Use laptop suite:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/test_laptop_suite.py -v
   ```

2. **Reduce simulation parameters:**
   ```yaml
   dynamics:
     L_max: 2          # Reduce from 8
     matsubara_truncation: 1  # Reduce from 2
     time_max: 10      # Reduce from 1000
   simulation:
     n_traj: 5         # Reduce from 100
   ```

3. **Skip slow tests:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/ -v --timeout=60 -k "not slow"
   ```

4. **Use parallel execution:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/ -v -n 4
   ```

---

### Issue: CPU not fully utilized

**Symptoms:**
```
top shows: 25% CPU usage (should be 100%)
```

**Solutions:**

1. **Increase number of workers:**
   ```yaml
   parallel_config:
     n_workers: 8  # Increase from 4
   ```

2. **Increase trajectory count:**
   ```yaml
   simulation:
     n_traj: 100  # Increase from 10
   ```

3. **Check for I/O bottleneck:**
   ```bash
   iostat -x 1 5
   ```

4. **Check system load:**
   ```bash
   top
   ps aux | grep python
   ```

---

## File and Path Issues

### Issue: "File not found" or "No such file or directory"

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'parameters.yaml'
```

**Solutions:**

1. **Check current directory:**
   ```bash
   pwd
   ls -la parameters.yaml
   ```

2. **Use absolute paths:**
   ```bash
   # Instead of:
   python main.py --config parameters.yaml
   
   # Use:
   python main.py --config /full/path/to/parameters.yaml
   ```

3. **Check file exists:**
   ```bash
   find . -name "parameters.yaml" -type f
   ```

4. **Verify working directory:**
   ```bash
   cd /home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS
   mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py
   ```

---

### Issue: "Permission denied" when writing results

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'results/output.csv'
```

**Solutions:**

1. **Check directory permissions:**
   ```bash
   ls -ld reproducibility/results/
   ```

2. **Create directory if missing:**
   ```bash
   mkdir -p reproducibility/results/
   mkdir -p reproducibility/logs/
   ```

3. **Fix permissions:**
   ```bash
   chmod 755 reproducibility/results/
   chmod 755 reproducibility/logs/
   ```

4. **Check disk space:**
   ```bash
   df -h
   ```

---

## Logging and Debugging

### Issue: No output or logs

**Symptoms:**
```
No output from pytest
No log files created
```

**Solutions:**

1. **Enable verbose output:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/ -v -s
   ```

2. **Check log directory:**
   ```bash
   ls -la reproducibility/logs/
   tail -f reproducibility/logs/tests_*.log
   ```

3. **Enable debug logging:**
   ```bash
   export PYTHONUNBUFFERED=1
   mamba run -n MesoHOP-sim pytest tests/ -v -s --log-cli-level=DEBUG
   ```

4. **Check if pytest is installed:**
   ```bash
   mamba run -n MesoHOP-sim python -c "import pytest; print(pytest.__version__)"
   ```

---

### Issue: Cryptic error messages

**Symptoms:**
```
RuntimeError: HOPS simulation failed
ValueError: Invalid state
```

**Solutions:**

1. **Run with full traceback:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/ -v -s --tb=long
   ```

2. **Check logs for details:**
   ```bash
   grep -A 10 "ERROR" reproducibility/logs/tests_*.log
   ```

3. **Run individual test:**
   ```bash
   mamba run -n MesoHOP-sim pytest tests/test_core.py::test_hops_simulator_simulation_stub -v -s
   ```

4. **Add debug prints:**
   ```python
   # In test file
   import logging
   logger = logging.getLogger(__name__)
   logger.debug(f"Variable value: {var}")
   ```

---

## Git and Version Control Issues

### Issue: "Uncommitted changes" or merge conflicts

**Symptoms:**
```
error: Your local changes to the following files would be overwritten by merge
```

**Solutions:**

1. **Check status:**
   ```bash
   git status
   ```

2. **Stash changes:**
   ```bash
   git stash
   ```

3. **Discard changes:**
   ```bash
   git checkout -- .
   ```

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "Test fixes"
   ```

---

### Issue: "LFS file not found" or large file errors

**Symptoms:**
```
Error: File is stored in Git LFS but not available locally
```

**Solutions:**

1. **Install Git LFS:**
   ```bash
   git lfs install
   ```

2. **Pull LFS files:**
   ```bash
   git lfs pull
   ```

3. **Check LFS status:**
   ```bash
   git lfs status
   ```

---

## System-Specific Issues

### macOS Issues

**Issue: "Command not found: mamba"**
```bash
# Install mamba
brew install mambaforge
# or
conda install -c conda-forge mamba
```

**Issue: "Permission denied" on scripts**
```bash
chmod +x run_cluster.sh
```

---

### Linux Issues

**Issue: "Out of memory" on large simulations**
```bash
# Check swap
free -h
# Increase swap if needed
sudo fallocate -l 10G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

### Windows Issues (WSL2)

**Issue: "File not found" with Windows paths**
```bash
# Use WSL paths instead of Windows paths
# Instead of: C:\Users\...
# Use: /mnt/c/Users/...
```

**Issue: "Permission denied" on WSL**
```bash
# Fix permissions
chmod -R 755 /mnt/c/path/to/project
```

---

## Quick Diagnostic Script

```bash
#!/bin/bash
# Run this to diagnose issues

echo "🔍 Diagnostic Report"
echo "===================="

echo ""
echo "1. Environment"
echo "   Conda version: $(conda --version)"
echo "   Mamba version: $(mamba --version)"
echo "   Python version: $(python --version)"

echo ""
echo "2. MesoHOPS"
mamba run -n MesoHOP-sim python -c "import mesohops; print(f'   MesoHOPS version: {mesohops.__version__}')" 2>/dev/null || echo "   MesoHOPS: NOT FOUND"

echo ""
echo "3. Dependencies"
mamba run -n MesoHOP-sim python -c "import numpy, scipy, matplotlib; print('   numpy, scipy, matplotlib: OK')" 2>/dev/null || echo "   Dependencies: MISSING"

echo ""
echo "4. System Resources"
echo "   CPU cores: $(nproc)"
echo "   Total RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "   Available RAM: $(free -h | grep Mem | awk '{print $7}')"
echo "   Disk space: $(df -h . | tail -1 | awk '{print $4}')"

echo ""
echo "5. Project Structure"
echo "   Framework dir: $([ -d Redac_Paper1/quantum_simulations_framework_parallel_260509 ] && echo 'OK' || echo 'MISSING')"
echo "   Tests dir: $([ -d Redac_Paper1/quantum_simulations_framework_parallel_260509/tests ] && echo 'OK' || echo 'MISSING')"
echo "   Config file: $([ -f Redac_Paper1/quantum_simulations_framework_parallel_260509/parameters.yaml ] && echo 'OK' || echo 'MISSING')"

echo ""
echo "6. Test Status"
mamba run -n MesoHOP-sim pytest tests/test_laptop_suite.py -v --tb=no 2>&1 | tail -5

echo ""
echo "✅ Diagnostic complete"
```

---

## Getting Help

### If you're still stuck:

1. **Check documentation:**
   - TESTING_INDEX.md — Navigation guide
   - LAPTOP_TESTING_GUIDE.md — Quick start
   - TEST_FAILURES_AND_FIXES.md — Detailed fixes
   - QUICK_FIX_GUIDE.md — Copy-paste fixes

2. **Review logs:**
   ```bash
   tail -100 reproducibility/logs/tests_*.log
   ```

3. **Run diagnostic:**
   ```bash
   bash diagnostic.sh
   ```

4. **Check GitHub issues:**
   - Search for similar issues
   - Create new issue with diagnostic output

5. **Contact support:**
   - Include diagnostic output
   - Include error message and traceback
   - Include system information (OS, RAM, CPU)

---

## Summary

| Issue | Solution | Time |
|-------|----------|------|
| MesoHOPS not found | Install/verify environment | 5 min |
| Tests timeout | Use laptop suite or skip slow tests | 1 min |
| Out of memory | Reduce parameters or close apps | 5 min |
| Assertion failures | Check tolerance or use laptop suite | 1 min |
| Mock errors | Apply fixes from QUICK_FIX_GUIDE.md | 10 min |
| Config errors | Verify YAML syntax and keys | 5 min |
| Performance issues | Reduce L, K, n_traj, or t_max | 5 min |
| File not found | Check paths and working directory | 5 min |

**Most common fix:** Run laptop suite instead of full suite!
