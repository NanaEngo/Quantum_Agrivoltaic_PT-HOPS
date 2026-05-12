#!/bin/bash
# Script to run laptop tests within the MesoHOP-sim mamba environment
export PATH="/home/taamangtchu/miniforge3/bin:$PATH"
export PATH="/home/taamangtchu/anaconda3/bin:$PATH"

echo "Attempting to run tests with mamba..."
mamba run -n MesoHOP-sim pytest /media/taamangtchu/MYDATA/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel_260509/tests/test_laptop_suite.py -v -s
