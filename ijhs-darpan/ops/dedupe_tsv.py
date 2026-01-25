# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
# ]
# ///

import os
import re
import pathlib
import pandas as pd

# Configuration
BASE_DIR = pathlib.Path(__file__).parent.parent
TSV_FILES = [
    BASE_DIR / ".cache" / "ijhs.tsv",
    BASE_DIR / ".cache" / "ijhs-classified.tsv"
]

def get_filename(url):
    if not url: return ''
    # Match the last part of path before ? or #
    fname = url.split('/')[-1].split('?')[0].split('#')[0]
    return fname

def dedupe():
    for f_path in TSV_FILES:
        if not f_path.exists():
            print(f"Skipping missing file: {f_path}")
            continue
            
        print(f"Processing {f_path}...")
        
        # Load with pandas to handle tab-separation and potential quoting issues
        df = pd.read_csv(f_path, sep='\t', dtype=str).fillna('')
        
        initial_count = len(df)
        
        # Identify URL column
        if 'url' not in df.columns:
            print(f"Error: 'url' column not found in {f_path}")
            continue
            
        # Create helper columns
        df['filename'] = df['url'].map(get_filename)
        df['is_insa'] = df['url'].str.contains('insa.nic.in').astype(int)
        
        # Sort so INSA comes first for the same filename
        df = df.sort_values(by=['filename', 'is_insa'], ascending=[True, False])
        
        # Split into rows with and without filenames
        mask_has_filename = df['filename'] != ''
        df_files = df[mask_has_filename].copy()
        df_no_files = df[~mask_has_filename].copy()
        
        # Deduplicate the ones with filenames
        df_files_unique = df_files.drop_duplicates(subset=['filename'], keep='first')
        
        # Re-merge
        final_df = pd.concat([df_files_unique, df_no_files]).sort_index()
        
        # Drop helper columns
        final_df = final_df.drop(columns=['filename', 'is_insa'])
        
        final_count = len(final_df)
        if final_count < initial_count:
            final_df.to_csv(f_path, sep='\t', index=False)
            print(f"Cleaned {f_path.name}: removed {initial_count - final_count} duplicates.")
        else:
            print(f"No duplicates found in {f_path.name}.")

if __name__ == "__main__":
    dedupe()
