#!/usr/bin/env python3
"""
Notebook Output Cleaner and Size Manager
Removes outputs, execution counts, and metadata to reduce file sizes
"""
import json
import os
import shutil
from pathlib import Path
import argparse

def clean_notebook_outputs(notebook_path, backup=True):
    """Remove outputs and execution counts from notebook"""
    if backup:
        backup_path = str(notebook_path) + '.backup'
        shutil.copy2(notebook_path, backup_path)
        print(f"Backup created: {backup_path}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    original_size = os.path.getsize(notebook_path)
    
    # Clean each cell
    for cell in nb.get('cells', []):
        # Remove outputs
        if 'outputs' in cell:
            cell['outputs'] = []
        
        # Remove execution count
        if 'execution_count' in cell:
            cell['execution_count'] = None
    
    # Clean notebook metadata
    if 'metadata' in nb:
        # Keep essential metadata, remove execution info
        essential_keys = ['kernelspec', 'language_info']
        nb['metadata'] = {k: v for k, v in nb['metadata'].items() if k in essential_keys}
    
    # Write cleaned notebook
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    
    new_size = os.path.getsize(notebook_path)
    reduction = ((original_size - new_size) / original_size) * 100
    
    print(f"Cleaned {notebook_path}")
    print(f"Size: {original_size:,} -> {new_size:,} bytes ({reduction:.1f}% reduction)")
    
    return original_size, new_size

def analyze_notebook_content(notebook_path):
    """Analyze what's taking space in the notebook"""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    total_cells = len(nb.get('cells', []))
    code_cells = sum(1 for cell in nb['cells'] if cell.get('cell_type') == 'code')
    output_cells = sum(1 for cell in nb['cells'] if cell.get('outputs'))
    
    # Estimate output size
    notebook_str = json.dumps(nb)
    total_size = len(notebook_str.encode('utf-8'))
    
    # Create version without outputs
    nb_no_outputs = nb.copy()
    for cell in nb_no_outputs.get('cells', []):
        if 'outputs' in cell:
            cell['outputs'] = []
        if 'execution_count' in cell:
            cell['execution_count'] = None
    
    no_output_str = json.dumps(nb_no_outputs)
    no_output_size = len(no_output_str.encode('utf-8'))
    output_size = total_size - no_output_size
    
    return {
        'total_cells': total_cells,
        'code_cells': code_cells,
        'output_cells': output_cells,
        'total_size': total_size,
        'output_size': output_size,
        'code_size': no_output_size
    }

def main():
    parser = argparse.ArgumentParser(description='Clean Jupyter notebook outputs')
    parser.add_argument('notebooks', nargs='*', help='Notebook files to clean')
    parser.add_argument('--directory', '-d', help='Directory containing notebooks')
    parser.add_argument('--analyze', '-a', action='store_true', help='Analyze notebook sizes')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backups')
    
    args = parser.parse_args()
    
    if args.directory:
        notebook_paths = list(Path(args.directory).rglob('*.ipynb'))
    else:
        notebook_paths = [Path(nb) for nb in args.notebooks]
    
    if not notebook_paths:
        print("No notebooks specified")
        return
    
    total_original = 0
    total_cleaned = 0
    
    for nb_path in notebook_paths:
        if '.ipynb_checkpoints' in str(nb_path) or '~' in nb_path.name:
            continue
            
        print(f"\n{'='*60}")
        print(f"Processing: {nb_path}")
        
        if args.analyze:
            analysis = analyze_notebook_content(nb_path)
            print(f"Cells: {analysis['total_cells']} total, {analysis['code_cells']} code, {analysis['output_cells']} with outputs")
            print(f"Size breakdown: {analysis['total_size']:,} total ({analysis['output_size']:,} outputs, {analysis['code_size']:,} code)")
        
        if not args.analyze:
            try:
                orig, new = clean_notebook_outputs(nb_path, backup=not args.no_backup)
                total_original += orig
                total_cleaned += new
            except Exception as e:
                print(f"Error processing {nb_path}: {e}")
    
    if not args.analyze and total_original > 0:
        total_reduction = ((total_original - total_cleaned) / total_original) * 100
        print(f"\n{'='*60}")
        print(f"Total reduction: {total_original:,} -> {total_cleaned:,} bytes ({total_reduction:.1f}%)")

if __name__ == "__main__":
    main()
