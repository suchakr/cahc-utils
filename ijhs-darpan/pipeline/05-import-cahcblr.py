# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
#     "lxml",
# ]
# ///

import os
import pandas as pd
import re
import pathlib

# Configuration
PROJECT_ROOT = pathlib.Path(os.path.expanduser("~/projects/cahcblr.github.io"))
CACHE_DIR = pathlib.Path(__file__).parent.parent / ".cache"
TSV_PATH = CACHE_DIR / "ijhs.tsv"

def parse_markdown_table(filepath):
    """
    Rudimentary markdown table parser.
    Expects table rows starting with | and a header separator |---|
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    rows = []
    header = None
    started = False
    
    for line in lines:
        line = line.strip()
        if not line.startswith('|'):
            continue
        
        # Split and clean parts
        parts = [p.strip() for p in line.split('|') if p.strip() or p == '']
        # If it's the separator |---|---| ignore it
        if started and all(re.match(r'^-+$', p) for p in parts if p):
            continue
            
        if not started:
            header = parts
            started = True
            continue
            
        # Data row
        if len(parts) >= len(header):
            rows.append(parts)
            
    return pd.DataFrame(rows, columns=header)

def extract_link(md_link):
    """Extracts URL and Text from [Title](URL)"""
    match = re.search(r'\[\s*\*\*(.*?)\*\*\s*\]\((.*?)\)', md_link)
    if not match:
        match = re.search(r'\[(.*?)\]\((.*?)\)', md_link)
    
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return md_link, None

def import_p60():
    p60_path = PROJECT_ROOT / "p60_papers.markdown"
    if not p60_path.exists():
        print(f"p60 not found at {p60_path}")
        return []
    
    print(f"Parsing {p60_path}...")
    df_p60 = parse_markdown_table(p60_path)
    
    # Columns: # | Year | Category | Paper Title | Author | Source
    # Note: Paper Title is usually a link
    imported = []
    for _, row in df_p60.iterrows():
        title_raw = row.get('Paper Title', '')
        title, url = extract_link(title_raw)
        
        if not url:
            # Fallback if no link in title
            continue
            
        # Normalize URL to absolute if relative
        if url.startswith('../'):
            # e.g. ../assets/cached_papers/rni/paper.pdf
            # The web site serves from cahc.jainuniversity.ac.in/assets/...
            url = "https://cahc.jainuniversity.ac.in/" + url.replace('../', '')

        entry = {
            'journal': row.get('Source', 'Non-IJHS'),
            'paper': title,
            'author': row.get('Author', ''),
            'url': url,
            'year': row.get('Year', '')
        }
        imported.append(entry)
        
    print(f"Extracted {len(imported)} entries from p60.")
    return imported

def main():
    if not TSV_PATH.exists():
        print(f"Error: Master TSV not found at {TSV_PATH}")
        return

    # Load existing
    master_df = pd.read_csv(TSV_PATH, sep='\t')
    
    # Track existing identifiers
    existing_urls = set(master_df['url'].tolist())
    
    def get_filename(url):
        if not url: return None
        return url.split('/')[-1].split('?')[0]
        
    existing_filenames = {get_filename(url) for url in master_df['url'] if url}
    
    # Import new items
    new_items = import_p60()
    
    added_count = 0
    to_append = []
    
    for item in new_items:
        fname = get_filename(item['url'])
        # Deduplicate by URL or Filename
        if item['url'] not in existing_urls and fname not in existing_filenames:
            to_append.append(item)
            added_count += 1
            existing_urls.add(item['url'])
            if fname: existing_filenames.add(fname)
            
    if to_append:
        append_df = pd.DataFrame(to_append)
        # Ensure columns match master (may need size_in_kb)
        for col in master_df.columns:
            if col not in append_df.columns:
                append_df[col] = None
        
        # Merge
        final_df = pd.concat([master_df, append_df], ignore_index=True)
        
        # Clean formatting before saving
        # Convert year to string and strip .0 if it exists
        if 'year' in final_df.columns:
            final_df['year'] = final_df['year'].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '')
            
        final_df.to_csv(TSV_PATH, sep='\t', index=False)
        print(f"Successfully added {added_count} new entries to {TSV_PATH}")
    else:
        print("No new entries to add.")

if __name__ == "__main__":
    main()
