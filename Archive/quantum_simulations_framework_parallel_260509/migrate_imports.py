#!/usr/bin/env python3
"""
Automated Import Migration Script
Migrates all imports from old paths to new src/ structure
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import shutil
from datetime import datetime

# Migration mapping: old_pattern -> new_pattern
IMPORT_MAPPINGS = {
    # Core module imports
    r'from core\.constants import': 'from src.core.constants import',
    r'from core\.hamiltonian_factory import': 'from src.core.hamiltonian_factory import',
    r'from core\.hops_simulator import': 'from src.core.hops_simulator import',
    r'from core\.gpu_dynamics import': 'from src.core.gpu_dynamics import',
    
    # Extensions imports
    r'from extensions\.stochastic_bundling import': 'from src.extensions.stochastic_bundling import',
    r'from extensions\.mesohops_adapters import': 'from src.extensions.mesohops_adapters import',
    
    # Models -> Agrivoltaic imports
    r'from models\.agrivoltaic_coupling_model import': 'from src.agrivoltaic.coupling_model import',
    r'from models\.environmental_factors import': 'from src.agrivoltaic.environmental_factors import',
    r'from models\.biodegradability_analyzer import': 'from src.agrivoltaic.biodegradability_analyzer import',
    r'from models\.eco_design_analyzer import': 'from src.agrivoltaic.eco_design_analyzer import',
    r'from models\.lca_analyzer import': 'from src.agrivoltaic.lca_analyzer import',
    r'from models\.techno_economic_model import': 'from src.agrivoltaic.techno_economic_model import',
    
    # Models -> Quantum imports
    r'from models\.quantum_dynamics_simulator import': 'from src.quantum.analysis import',
    r'from models\.simple_quantum_dynamics_simulator import': 'from src.quantum.analysis import',
    r'from models\.quantum_analysis import': 'from src.quantum.analysis import',
    r'from models\.spectral_optimizer import': 'from src.quantum.spectral_optimization import',
    r'from models\.spectroscopy_2des import': 'from src.quantum.spectroscopy import',
    r'from models\.multi_scale_transformer import': 'from src.quantum.multi_scale import',
    
    # Utils -> src/io imports
    r'from utils\.csv_data_storage import': 'from src.io.csv_storage import',
    
    # Utils -> src/visualization imports
    r'from utils\.figure_generator import': 'from src.visualization.figure_generator import',
    
    # Reproducibility imports (keep in reproducibility for now)
    # These can be updated later if needed
}

# Files to skip (archives, venv, etc.)
SKIP_PATTERNS = [
    '.venv',
    '__pycache__',
    '.git',
    'Archive',
    'archives/obsolete',
    'archives/incomplete_tests',
]

class ImportMigrator:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.changes = []
        self.errors = []
        self.skipped = []
        
    def should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        path_str = str(file_path)
        for pattern in SKIP_PATTERNS:
            if pattern in path_str:
                return True
        return False
    
    def migrate_file(self, file_path: Path) -> bool:
        """Migrate imports in a single file"""
        if self.should_skip(file_path):
            self.skipped.append(str(file_path.relative_to(self.base_path)))
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all import mappings
            for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
                content = re.sub(old_pattern, new_pattern, content)
            
            # Check if any changes were made
            if content != original_content:
                # Backup original file
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                shutil.copy2(file_path, backup_path)
                
                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.changes.append({
                    'file': str(file_path.relative_to(self.base_path)),
                    'backup': str(backup_path.relative_to(self.base_path))
                })
                return True
            
            return False
            
        except Exception as e:
            self.errors.append({
                'file': str(file_path.relative_to(self.base_path)),
                'error': str(e)
            })
            return False
    
    def migrate_all(self) -> Dict:
        """Migrate all Python files in the codebase"""
        print(f"Starting import migration in {self.base_path}")
        print("=" * 80)
        
        py_files = list(self.base_path.rglob('*.py'))
        total_files = len(py_files)
        migrated_count = 0
        
        for i, py_file in enumerate(py_files, 1):
            if self.migrate_file(py_file):
                migrated_count += 1
                print(f"[{i}/{total_files}] ✓ {py_file.relative_to(self.base_path)}")
            elif not self.should_skip(py_file):
                print(f"[{i}/{total_files}] - {py_file.relative_to(self.base_path)} (no changes)")
        
        return {
            'total_files': total_files,
            'migrated': migrated_count,
            'skipped': len(self.skipped),
            'errors': len(self.errors),
            'changes': self.changes,
            'errors_list': self.errors,
            'skipped_list': self.skipped
        }

def main():
    base_path = Path("/home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel_260509")
    
    migrator = ImportMigrator(base_path)
    results = migrator.migrate_all()
    
    print("\n" + "=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    print(f"Total files scanned:     {results['total_files']}")
    print(f"Files migrated:          {results['migrated']}")
    print(f"Files skipped:           {results['skipped']}")
    print(f"Errors:                  {results['errors']}")
    
    if results['errors'] > 0:
        print("\nErrors encountered:")
        for error in results['errors_list']:
            print(f"  - {error['file']}: {error['error']}")
    
    print("\n" + "=" * 80)
    print("MIGRATION COMPLETE")
    print("=" * 80)
    
    # Generate report
    report_path = base_path.parent / f"MIGRATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, 'w') as f:
        f.write("IMPORT MIGRATION REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Total files scanned: {results['total_files']}\n")
        f.write(f"Files migrated: {results['migrated']}\n")
        f.write(f"Files skipped: {results['skipped']}\n")
        f.write(f"Errors: {results['errors']}\n\n")
        
        if results['changes']:
            f.write("MIGRATED FILES:\n")
            f.write("-" * 80 + "\n")
            for change in results['changes']:
                f.write(f"  {change['file']}\n")
                f.write(f"    Backup: {change['backup']}\n")
        
        if results['errors_list']:
            f.write("\nERRORS:\n")
            f.write("-" * 80 + "\n")
            for error in results['errors_list']:
                f.write(f"  {error['file']}: {error['error']}\n")
    
    print(f"Report saved to: {report_path}")

if __name__ == '__main__':
    main()
