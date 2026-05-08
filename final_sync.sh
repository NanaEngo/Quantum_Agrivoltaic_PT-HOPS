#!/bin/bash
git status
git add -A
git commit -m "Final hardening of test suite and parameter verification"
git checkout main
git merge Codebase_modifications -m "Merge final hardening commits into main"
git push origin main
git checkout Codebase_modifications
rm /media/taamangtchu/MYDATA/Github/Quantum_Agrivoltaic_PT-HOPS/final_sync.sh
