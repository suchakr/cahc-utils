#!/usr/bin/env python3
"""
Dataset Reorganization Dependency Analyzer
Scans notebooks for file references and creates migration plan
"""
import json
import re
import os
from pathlib import Path
import glob

def extract_file_references(notebook_path):
    """Extract all file references from a notebook"""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        print(f"Error reading {notebook_path}: {e}")
        return []
    
    file_refs = []
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            # Look for file references
            patterns = [
                r'["\']([^"\']*\.(?:csv|tsv|pickle|pkl|txt))["\']',  # Quoted filenames
                r'pd\.read_csv\(["\']([^"\']+)["\']',                # pandas read
                r'pd\.read_pickle\(["\']([^"\']+)["\']',             # pandas pickle
                r'open\(["\']([^"\']+\.(?:csv|tsv|pickle|pkl|txt))["\']',  # open() calls
            ]
            for pattern in patterns:
                matches = re.findall(pattern, source, re.IGNORECASE)
                file_refs.extend(matches)
    
    # Filter for dataset-related files
    dataset_refs = [ref for ref in file_refs if 
                   'datasets/' in ref or 
                   ref.endswith(('.csv', '.tsv', '.pickle', '.pkl'))]
    
    return list(set(dataset_refs))  # Remove duplicates

def analyze_notebooks(jyotisha_dir):
    """Analyze all notebooks for file dependencies"""
    notebook_deps = {}
    
    for nb_path in Path(jyotisha_dir).rglob('*.ipynb'):
        if '.ipynb_checkpoints' in str(nb_path):
            continue
            
        file_refs = extract_file_references(nb_path)
        if file_refs:
            notebook_deps[str(nb_path)] = file_refs
    
    return notebook_deps

def create_migration_mapping():
    """Create mapping from old paths to new organized paths"""
    # This will be customized based on your organization strategy
    mapping = {}
    
    # Example mappings - customize these
    patterns = {
        r'kuru_.*\.csv': 'intermediate/kuru_calculations/',
        r'astropy-.*\.tsv': 'intermediate/full_moons/',
        r'moon.*\.csv': 'intermediate/moon_phases/',
        r'.*planet.*\.csv': 'intermediate/planet_positions/',
        r'n\d+.*\.csv': 'intermediate/nakshatras/',
        r'.*eclipse.*\.csv': 'intermediate/eclipses/',
        r'.*\.pickle': 'intermediate/calculations/',
        r'.*catalog.*': 'reference/catalogs/',
    }
    
    return patterns

if __name__ == "__main__":
    # Analyze current dependencies
    deps = analyze_notebooks('../jyotisha')
    
    print("=== NOTEBOOK FILE DEPENDENCIES ===")
    for notebook, files in deps.items():
        print(f"\n{notebook}:")
        for file_ref in files:
            print(f"  - {file_ref}")
    
    # Summary
    all_files = set()
    for files in deps.values():
        all_files.update(files)
    
    print(f"\n=== SUMMARY ===")
    print(f"Notebooks with dependencies: {len(deps)}")
    print(f"Unique file references: {len(all_files)}")
    print(f"Referenced files:")
    for file_ref in sorted(all_files):
        print(f"  - {file_ref}")
