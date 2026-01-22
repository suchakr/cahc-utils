# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
# ]
# ///

import pandas as pd
import json
import os
import pathlib
import sys

# Paths
# Paths
BASE_DIR = pathlib.Path(__file__).parent.parent # ijhs-darpan root
TSV_PATH = BASE_DIR / ".cache" / "ijhs-classified.tsv"
OUTPUT_JS_PATH = BASE_DIR / "web" / "assets" / "js" / "data.js"
SYMLINK_DIR = BASE_DIR / "web" / "assets" / "pdfs"

# Source directories for PDFs (where we look for files)
# Assets are in a sibling repo `cahcblr.github.io`.
# Use absolute path to be robust against directory nesting
ASSETS_ROOT = pathlib.Path(os.path.expanduser("~/projects/cahcblr.github.io/assets"))
POTENTIALS_DIR = ASSETS_ROOT / "ijhs_potentials"
CACHED_DIR = ASSETS_ROOT / "cached_papers" / "rni"

def setup_symlink():
    """Creates a symlink assets/pdfs -> .../cahcblr.github.io/assets"""
    if not ASSETS_ROOT.exists():
        print(f"Warning: Assets root not found at {ASSETS_ROOT}")
        return

    # Check if symlink exists
    target_link = SYMLINK_DIR
    
    # If it exists (even as broken link) or is file, remove it
    if target_link.exists() or target_link.is_symlink():
        target_link.unlink()
        
    try:
        # Create symlink: ijhs-darpan/assets/pdfs -> .../assets
        target_link.symlink_to(ASSETS_ROOT)
        print(f"Symlink created: {target_link} -> {ASSETS_ROOT}")
    except Exception as e:
        print(f"Failed to create symlink: {e}")

def find_local_path(url_filename):
    """
    Tries to find the file in the known PDF directories.
    Returns the path RELATIVE to the 'pdfs' symlink (which points to 'assets').
    """
    if not isinstance(url_filename, str):
        return None
    
    # Extract filename from URL if it is a URL
    filename = url_filename.split('/')[-1]
    
    # Check in ijhs_potentials (underscore)
    if (ASSETS_ROOT / "ijhs_potentials" / filename).exists():
        return f"assets/pdfs/ijhs_potentials/{filename}"
    
    # Check in cached_papers/rni
    if (ASSETS_ROOT / "cached_papers" / "rni" / filename).exists():
        return f"assets/pdfs/cached_papers/rni/{filename}"
        
    return None

def main():
    print(f"Reading TSV from {TSV_PATH}")
    if not TSV_PATH.exists():
        print("TSV file not found!")
        sys.exit(1)

    df = pd.read_csv(TSV_PATH, sep='\t')
    
    papers = []
    found_count = 0
    
    for _, row in df.iterrows():
        # Basic metadata
        paper = {
            "journal": row.get("journal", ""),
            "title": row.get("paper", "Untitled"),
            "author": row.get("author", "Unknown"),
            "category": row.get("category", "Uncategorized"),
            "subject": row.get("subject", "General"),
            "year": str(row.get("year", "")), # Ensure string if exists, else parse from journal
            "remoteUrl": row.get("url", ""),
            "size": row.get("size_in_kb", 0)
        }
        
        # Try to parse year from journal string if missing (e.g. IJHS-1-1966-Issue-1)
        if not paper["year"] or paper["year"] == "nan":
            parts = paper["journal"].split('-')
            for part in parts:
                if part.isdigit() and len(part) == 4:
                    paper["year"] = part
                    break
        
        # Resolve local path
        local_path = find_local_path(paper["remoteUrl"])
        if local_path:
            paper["localPath"] = local_path
            found_count += 1
        else:
            paper["localPath"] = None
            
        papers.append(paper)

    print(f"Processed {len(papers)} papers. Found local PDF for {found_count} of them.")
    
    # Write to JS
    js_content = f"const PAPERS = {json.dumps(papers, indent=2)};\n"
    
    with open(OUTPUT_JS_PATH, "w") as f:
        f.write(js_content)
    
    print(f"Data written to {OUTPUT_JS_PATH}")
    
    # Setup Symlink
    setup_symlink()

if __name__ == "__main__":
    main()
