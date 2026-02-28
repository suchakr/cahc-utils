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
        # Helper to clean numeric strings (remove .0)
        def clean_num(v):
            if pd.isna(v) or str(v).lower() == 'nan': return ""
            s = str(v)
            if s.endswith('.0'): return s[:-2]
            return s

        paper = {
            "journal": clean_num(row.get("journal", "")),
            "title": clean_num(row.get("paper", "Untitled")),
            "author": clean_num(row.get("author", "Unknown")),
            "category": clean_num(row.get("category", "Uncategorized")),
            "subject": clean_num(row.get("subject", "General")),
            "year": clean_num(row.get("year", "")),
            "remoteUrl": row.get("url", ""),
            "juUrl": clean_num(row.get("ju_url", "")),
            "size": row.get("size_in_kb", 0)
        }

        # Normalization: If primary is JU but secondary is empty, use primary for JU features
        if "jainuniversity" in str(paper["remoteUrl"]) and not paper["juUrl"]:
            paper["juUrl"] = paper["remoteUrl"]
        
        # Fix size: Ensure it's numeric and non-NaN
        try:
            if pd.isna(paper["size"]) or str(paper["size"]).lower() == 'nan':
                paper["size"] = 0
            else:
                paper["size"] = float(paper["size"])
        except:
            paper["size"] = 0
        
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
            
            # If size is 0/missing in metadata, try to get it from local disk
            if paper["size"] <= 0:
                # local_path is 'assets/pdfs/...', symlink 'assets/pdfs' -> ASSETS_ROOT
                rel_to_assets = local_path.replace("assets/pdfs/", "")
                abspath = ASSETS_ROOT / rel_to_assets
                if abspath.exists():
                    paper["size"] = abspath.stat().st_size / 1024.0
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
