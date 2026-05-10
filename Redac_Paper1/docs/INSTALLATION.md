# Installation (MesoHOPS environment)

This repository targets a MesoHOPS simulation environment. To create a reproducible environment:

1. Create the `MesoHOP-sim` environment:

```bash
mamba create -n MesoHOP-sim python=3.10
mamba activate MesoHOP-sim
```

2. Install all dependencies:

```bash
mamba run -n MesoHOP-sim pip install -r requirements.txt
mamba run -n MesoHOP-sim pip install -r requirements-mesohops.txt
```

4. Run tests (will skip mesohops tests if mesohops not installed):

```bash
pytest -q
```

Notes:
- Pin `mesohops` to a compatible version if your environment requires a different release.
- If `mesohops` installation requires system libraries, consult the MesoHOPS project documentation.
