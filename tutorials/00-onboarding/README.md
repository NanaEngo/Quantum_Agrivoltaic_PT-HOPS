# Onboarding (Tutorial 00)

This onboarding tutorial shows how to set up a local environment for the tutorials and run the provided demos.

Steps

1. Install Miniconda or Anaconda if you don't already have it.
2. Create the environment:

   conda env create -f tutorials/00-onboarding/environment.yaml
   conda activate qa_pt_hops_tutorial

3. Run a demo script (for example the PT-HOPS minimal demo):

   python ../03_pt_hops/03_pt_hops_minimal_demo.py

Notes

- The environment.yaml is intentionally conservative and kept small for student machines. Pin versions only where necessary.
- Later tutorials will be provided as Jupyter notebooks under their numbered directories.
