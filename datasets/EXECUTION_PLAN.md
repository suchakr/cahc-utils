# Dataset Reorganization Execution Plan

## Overview
This document outlines the complete plan for reorganizing the CAHC Utils datasets from a flat 850MB directory with 382 files into a well-organized hierarchical structure.

## Current Situation
- **Location**: `/Users/sunder/projects/cahc/cahc-utils/datasets`
- **Size**: 850MB across 382 files
- **Issues**: 
  - Flat structure making files hard to find
  - 129 temporary/backup files with `~` suffixes  
  - 9 notebooks with broken paths after reorganization
  - Bloated notebook files (39MB main notebook due to outputs)

## Goals
1. **Organized Structure**: Hierarchical directories by data type and processing stage
2. **Maintained Functionality**: All notebooks continue working with updated paths
3. **Reduced Size**: Clean notebook outputs to reclaim hundreds of MB
4. **Documentation**: Clear migration log and data dictionary

## Tools Created
1. **`reorganization_plan.py`** - Analyzes file dependencies in notebooks
2. **`notebook_cleaner.py`** - Removes outputs to reduce notebook sizes
3. **`complete_reorganization.py`** - Full automated reorganization system

## New Directory Structure
```
datasets/
├── raw/                    # Original, unprocessed data
│   ├── catalogs/          # Star catalogs, reference data (3 files)
│   └── references/        # Lookup tables, metadata (28 files)
├── intermediate/           # Processing outputs (can be regenerated)
│   ├── moon_phases/       # Moon rise/set events (52 files)
│   ├── planet_positions/  # Planetary position data (1 file)
│   ├── kuru_calculations/ # Kuru-specific computations (82 files)
│   ├── nakshatras/        # Nakshatra calculations (36 files)
│   ├── full_moons/        # Full moon data (17 files)
│   ├── eclipses/          # Eclipse data (5 files)
│   └── calculations/      # Large computation files (.pickle) (3 files)
├── archive/               # Old versions and backups
│   ├── backups/          # Files with ~ suffix (1 file)
│   └── old_versions/     # Dated snapshots
├── final/                 # Clean, analysis-ready datasets
│   └── analysis_ready/   # For final processed datasets
├── temp/                  # Temporary files (24 files, can be cleaned)
└── metadata/              # Documentation and migration logs
```

## Affected Notebooks
The following 9 notebooks will have their file paths automatically updated:
- `cahc_explore.ipynb` (39MB → ~400KB after cleaning)
- `cahc_explore_may_2023~.ipynb` (12MB → ~200KB)  
- `lunar-events-calculator.ipynb` (11MB → ~40KB)
- `cahc_explore_saved~.ipynb` (9MB → ~150KB)
- `cahc_explore_saved2~.ipynb` (5.5MB → ~200KB)
- `vgj_ac_rs.ipynb` (5MB → ~10KB)
- `gruha_chaara.ipynb` (1MB → ~10KB)
- `lagadha_units.ipynb` (120KB → ~50KB)
- `c2~.ipynb` (400KB → ~400KB)

## Execution Steps

### Phase 1: Backup and Preparation
```bash
# 1. Ensure we're in the right branch
git status  # Should show "dataset-reorganization-2025-08"

# 2. Create a full backup
cd ..
tar -czf datasets-backup-$(date +%Y%m%d).tar.gz datasets/
cd datasets

# 3. Test the reorganization system (already done)
python3 complete_reorganization.py  # Dry run
```

### Phase 2: Execute Reorganization
```bash
# 1. Execute the full reorganization
python3 complete_reorganization.py --execute

# 2. Verify structure
ls -la  # Check new directories created
find . -name "*.csv" | head -10  # Verify files moved correctly

# 3. Test a notebook
cd ../jyotisha
jupyter notebook cahc_explore.ipynb  # Quick test that paths work
```

### Phase 3: Clean Notebook Outputs
```bash
# Return to datasets directory
cd ../datasets

# 1. Clean all notebook outputs
python3 notebook_cleaner.py --directory ../jyotisha

# 2. Check size reduction
du -sh ../jyotisha/*.ipynb | sort -hr
```

### Phase 4: Final Organization
```bash
# 1. Review uncategorized files (58 files need manual categorization)
cat metadata/reorganization_log.md  # Review migration log

# 2. Clean up temp files if appropriate
# ls temp/  # Review temp files
# rm temp/_*  # Remove if safe to do so

# 3. Commit all changes
git add .
git commit -m "Execute complete dataset reorganization

- Moved 310+ files into hierarchical structure
- Updated paths in 9 notebooks with automatic backup
- Cleaned notebook outputs reducing size by ~90%
- Created comprehensive migration documentation"

# 4. Push branch for review
git push origin dataset-reorganization-2025-08
```

## Expected Results

### File Organization
- **Before**: 382 files in flat structure
- **After**: Same files organized in 10 categories with 58 requiring manual review

### Size Reduction
- **Notebooks**: ~80MB → ~1MB (95%+ reduction from output cleaning)
- **Structure**: Better findability and maintenance
- **Documentation**: Clear audit trail of all changes

### Functionality
- **Notebooks**: All continue working with updated paths
- **Backups**: Comprehensive backup system for safety
- **Reversibility**: Can revert changes if needed

## Manual Review Required
58 files were uncategorized and need manual placement:
- Various planet position files (mars, jupiter, mercury, venus, saturn)
- Specialized analysis files (magsam, n83-mars, mercury-visibility, etc.)
- Unit files and other reference data

These should be reviewed and moved to appropriate directories after execution.

## Safety Measures
1. **Git Branch**: All work isolated in `dataset-reorganization-2025-08`
2. **Backups**: Automatic `.backup` files for all modified notebooks
3. **Tar Archive**: Full system backup before execution
4. **Dry Run Verified**: Complete system tested without changes
5. **Revert Plan**: Can checkout previous commit to undo changes

## Success Criteria
- [ ] All 9 notebooks run without path errors
- [ ] Files are logically organized by scientific domain
- [ ] Notebook sizes reduced by 90%+
- [ ] Migration documentation complete
- [ ] No data loss or corruption
- [ ] Project structure is maintainable going forward

## Next Steps After Execution
1. Review and categorize the 58 uncategorized files
2. Create data dictionary documentation in `metadata/`
3. Set up automated cleanup scripts for temp files
4. Merge branch back to main development branch
5. Update project README with new structure

---

**Branch**: `dataset-reorganization-2025-08`  
**Ready for execution**: ✅  
**Backup required**: ✅  
**Estimated time**: 15-20 minutes for full execution
