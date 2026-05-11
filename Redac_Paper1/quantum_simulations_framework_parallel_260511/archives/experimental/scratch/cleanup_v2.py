import os

paths = [
    "Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main2.py",
    "Redac_Paper1/quantum_simulations_framework_parallel_260509/core/hops_simulator2.py"
]

for path in paths:
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path):
        os.remove(abs_path)
        print(f"Deleted: {path}")
    else:
        print(f"Not found: {path}")
