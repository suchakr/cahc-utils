#!/usr/bin/env python3
"""
Complete CAHC Utils Dataset Reorganization
Handles both dataset organization and notebook path migration
"""

import json
import re
import os
import shutil
from pathlib import Path
import argparse
from typing import Dict, List, Tuple

class DatasetReorganizer:
    def __init__(self, datasets_dir, jyotisha_dir, dry_run=True):
        self.datasets_dir = Path(datasets_dir)
        self.jyotisha_dir = Path(jyotisha_dir)
        self.dry_run = dry_run
        
        # Define new directory structure
        self.new_structure = {
            'raw': ['catalogs', 'references'],
            'intermediate': ['moon_phases', 'planet_positions', 'kuru_calculations', 
                           'nakshatras', 'full_moons', 'eclipses', 'calculations'],
            'final': ['analysis_ready'],
            'archive': ['backups', 'old_versions'],
            'temp': [],
            'metadata': []
        }
        
        # File categorization patterns
        self.file_patterns = {
            # Raw data
            'raw/catalogs': [r'.*catalog.*', r'5MKLEcatalog.*', r'amara-kosha.*'],
            'raw/references': [r'n\d+_.*meta.*', r'.*-units-.*', r'tara-circumpolarity.*'],
            
            # Intermediate processing
            'intermediate/moon_phases': [r'moon.*', r'.*moon.*', r'nasa-moon-phases.*'],
            'intermediate/planet_positions': [r'.*planet.*', r'sun_moon_pos.*', r'.*-planet-pos.*'],
            'intermediate/kuru_calculations': [r'kuru_.*', r'kb_.*'],
            'intermediate/nakshatras': [r'n\d+_.*', r'.*naks.*'],
            'intermediate/full_moons': [r'astropy-.*', r'fm_.*', r'full.*moon.*'],
            'intermediate/eclipses': [r'.*eclipse.*', r'jaipur-.*eclipse.*'],
            'intermediate/calculations': [r'.*\.pickle', r'.*\.pkl', r'best_fit.*'],
            
            # Archive (old versions)
            'archive/backups': [r'.*~$', r'.*backup.*'],
            'archive/old_versions': [r'.*-old~.*', r'.*_saved.*'],
            
            # Temp files (can be deleted)
            'temp': [r'^_.*', r'Untitled.*', r'.*cache.*']
        }
    
    def create_directory_structure(self):
        """Create the new organized directory structure"""
        print("Creating new directory structure...")
        
        for main_dir, subdirs in self.new_structure.items():
            main_path = self.datasets_dir / main_dir
            if not self.dry_run:
                main_path.mkdir(exist_ok=True)
            print(f"  📁 {main_path}")
            
            for subdir in subdirs:
                sub_path = main_path / subdir
                if not self.dry_run:
                    sub_path.mkdir(exist_ok=True)
                print(f"    📁 {sub_path}")
    
    def categorize_files(self) -> Tuple[Dict[str, List[str]], List[str]]:
        """Categorize existing files based on patterns"""
        categorized = {path: [] for path in self.file_patterns.keys()}
        uncategorized = []
        
        for file_path in self.datasets_dir.iterdir():
            if file_path.is_file():
                filename = file_path.name
                matched = False
                
                for category, patterns in self.file_patterns.items():
                    for pattern in patterns:
                        if re.match(pattern, filename, re.IGNORECASE):
                            categorized[category].append(str(file_path))
                            matched = True
                            break
                    if matched:
                        break
                
                if not matched:
                    uncategorized.append(str(file_path))
        
        return categorized, uncategorized
    
    def move_files(self, categorized_files: Dict[str, List[str]]):
        """Move files to their new locations"""
        moved_files = {}  # old_path -> new_path mapping
        
        for category, files in categorized_files.items():
            if not files:
                continue
                
            target_dir = self.datasets_dir / category
            print(f"\nMoving files to {category}/:")
            
            for old_path in files:
                old_file = Path(old_path)
                new_path = target_dir / old_file.name
                
                print(f"  {old_file.name} -> {new_path}")
                moved_files[str(old_path)] = str(new_path)
                
                if not self.dry_run:
                    try:
                        shutil.move(str(old_path), str(new_path))
                    except Exception as e:
                        print(f"    ❌ Error moving {old_file.name}: {e}")
        
        return moved_files
    
    def update_notebook_paths(self, moved_files: Dict[str, str]):
        """Update file paths in notebooks"""
        print("\n" + "="*60)
        print("UPDATING NOTEBOOK PATHS")
        print("="*60)
        
        for notebook_path in self.jyotisha_dir.rglob('*.ipynb'):
            if '.ipynb_checkpoints' in str(notebook_path):
                continue
                
            self.update_single_notebook(notebook_path, moved_files)
    
    def update_single_notebook(self, notebook_path: Path, moved_files: Dict[str, str]):
        """Update paths in a single notebook"""
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = json.load(f)
        except Exception as e:
            print(f"❌ Error reading {notebook_path}: {e}")
            return
        
        changes_made = False
        changes = []
        
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'code':
                source_lines = cell.get('source', [])
                new_source = []
                
                for line in source_lines:
                    new_line = line
                    # Update relative paths to datasets
                    for old_path, new_path in moved_files.items():
                        old_rel = str(Path(old_path).relative_to(self.datasets_dir))
                        new_rel = str(Path(new_path).relative_to(self.datasets_dir))
                        
                        # Replace various path formats
                        patterns = [
                            f"../datasets/{old_rel}",
                            f"datasets/{old_rel}",
                            old_rel
                        ]
                        
                        for pattern in patterns:
                            if pattern in line:
                                new_line = new_line.replace(pattern, f"../datasets/{new_rel}")
                                if new_line != line:
                                    changes_made = True
                                    changes.append(f"  {pattern} -> ../datasets/{new_rel}")
                    
                    new_source.append(new_line)
                
                cell['source'] = new_source
        
        if changes_made:
            print(f"\n📝 Updating {notebook_path.name}:")
            for change in changes:
                print(change)
            
            if not self.dry_run:
                # Backup original
                backup_path = str(notebook_path) + '.pre-reorg.backup'
                shutil.copy2(notebook_path, backup_path)
                
                # Write updated notebook
                with open(notebook_path, 'w', encoding='utf-8') as f:
                    json.dump(nb, f, indent=2, ensure_ascii=False)
                
                print(f"  ✅ Updated (backup: {backup_path})")
        else:
            print(f"  ➡️  {notebook_path.name} (no changes needed)")
    
    def create_migration_documentation(self, moved_files: Dict[str, str]):
        """Create documentation of the migration"""
        doc_path = self.datasets_dir / 'metadata' / 'reorganization_log.md'
        
        content = f"""# Dataset Reorganization Log

## Overview
Reorganized CAHC Utils datasets from flat structure to organized hierarchy.

## New Structure
```
datasets/
├── raw/                    # Original, unprocessed data
│   ├── catalogs/          # Star catalogs, reference data
│   └── references/        # Lookup tables, metadata
├── intermediate/           # Processing outputs
│   ├── moon_phases/       # Moon rise/set events
│   ├── planet_positions/  # Planetary position data
│   ├── kuru_calculations/ # Kuru-specific computations
│   ├── nakshatras/        # Nakshatra calculations
│   ├── full_moons/        # Full moon data
│   ├── eclipses/          # Eclipse data
│   └── calculations/      # Large computation files (.pickle)
├── archive/               # Old versions and backups
│   ├── backups/          # Files with ~ suffix
│   └── old_versions/     # Dated snapshots
├── final/                 # Clean, analysis-ready datasets
└── metadata/              # Documentation
```

## File Migrations
"""
        
        for old_path, new_path in moved_files.items():
            old_name = Path(old_path).name
            new_rel = str(Path(new_path).relative_to(self.datasets_dir))
            content += f"- `{old_name}` → `{new_rel}`\n"
        
        content += f"""

## Notebooks Updated
Updated file paths in {len(list(self.jyotisha_dir.rglob('*.ipynb')))} notebooks to reflect new structure.

## Next Steps
1. Clean notebook outputs to reduce file sizes
2. Archive old notebook versions
3. Create data dictionary documentation
4. Set up automated cleanup scripts
"""
        
        if not self.dry_run:
            with open(doc_path, 'w') as f:
                f.write(content)
        
        print(f"\n📄 Documentation: {doc_path}")
    
    def run_full_reorganization(self):
        """Execute complete reorganization process"""
        print("CAHC Utils Dataset Reorganization")
        print("="*60)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        print(f"Datasets: {self.datasets_dir}")
        print(f"Notebooks: {self.jyotisha_dir}")
        print()
        
        # Step 1: Create directory structure
        self.create_directory_structure()
        
        # Step 2: Categorize files
        print("\nCategorizing files...")
        categorized, uncategorized = self.categorize_files()
        
        for category, files in categorized.items():
            if files:
                print(f"  {category}: {len(files)} files")
        
        if uncategorized:
            print(f"  ⚠️  Uncategorized: {len(uncategorized)} files")
            for file in uncategorized[:5]:  # Show first 5
                print(f"    - {Path(file).name}")
            if len(uncategorized) > 5:
                print(f"    ... and {len(uncategorized) - 5} more")
        
        # Step 3: Move files
        print(f"\n{'='*60}")
        print("MOVING FILES")
        print("="*60)
        moved_files = self.move_files(categorized)
        
        # Step 4: Update notebook paths
        self.update_notebook_paths(moved_files)
        
        # Step 5: Create documentation
        print(f"\n{'='*60}")
        print("CREATING DOCUMENTATION")
        print("="*60)
        self.create_migration_documentation(moved_files)
        
        print(f"\n{'='*60}")
        print("REORGANIZATION COMPLETE")
        print("="*60)
        if self.dry_run:
            print("⚠️  This was a DRY RUN. Use --execute to perform actual changes.")
        else:
            print("✅ Dataset reorganization completed successfully!")

def main():
    parser = argparse.ArgumentParser(description='Reorganize CAHC utils datasets')
    parser.add_argument('--datasets-dir', default='.',
                       help='Path to datasets directory')
    parser.add_argument('--jyotisha-dir', default='../jyotisha',
                       help='Path to jyotisha directory with notebooks')
    parser.add_argument('--execute', action='store_true',
                       help='Execute changes (default is dry run)')
    
    args = parser.parse_args()
    
    reorganizer = DatasetReorganizer(
        datasets_dir=args.datasets_dir,
        jyotisha_dir=args.jyotisha_dir,
        dry_run=not args.execute
    )
    
    reorganizer.run_full_reorganization()

if __name__ == "__main__":
    main()
