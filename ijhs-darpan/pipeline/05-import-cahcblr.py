# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
# ]
# ///
import os
import re
import pandas as pd
import pathlib
import unicodedata

# Paths
BASE_DIR = pathlib.Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / ".cache"
TSV_PATH = CACHE_DIR / "ijhs.tsv"
CLASSIFIED_PATH = CACHE_DIR / "ijhs-classified.tsv"
P60_PATH = pathlib.Path(os.path.expanduser("~/projects/cahcblr.github.io/p60_papers.markdown"))
P85_PATH = pathlib.Path(os.path.expanduser("~/projects/cahcblr.github.io/p85_search.markdown"))

def normalize_title(title):
    if not isinstance(title, str): return ""
    # Remove accents
    title = "".join(c for c in unicodedata.normalize('NFD', title) if unicodedata.category(c) != 'Mn')
    # Lowercase and remove all non-alphanumeric
    title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
    return title

def parse_markdown_table(path, start_line_pattern="| # |", skip_rows=1):
    if not path.exists():
        print(f"Warning: {path} not found.")
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    table_lines = []
    found_table = False
    for line in lines:
        if start_line_pattern in line:
            found_table = True
            continue
        if found_table:
            if "|" in line:
                table_lines.append(line.strip())
            else:
                if table_lines: # End of table
                    break
    
    if not table_lines:
        return []
    
    actual_rows = table_lines[skip_rows:]
    data = []
    for row in actual_rows:
        cols = [c.strip() for c in row.split("|")][1:-1]
        data.append(cols)
    return data

def extract_link_and_title(markdown_val):
    match = re.search(r'\[\**(.+?)\**\]\((.+?)\)', markdown_val)
    if match:
        title = match.group(1).strip()
        url = match.group(2).strip()
        return title, url
    return markdown_val, None

def main():
    # 1. Load dataframes
    dfs = {}
    for name, path in [('source', TSV_PATH), ('classified', CLASSIFIED_PATH)]:
        if path.exists():
            df = pd.read_csv(path, sep='\t')
            if 'ju_url' not in df.columns:
                df['ju_url'] = ""
            df['ju_url'] = df['ju_url'].fillna("")
            dfs[name] = df
        else:
            if name == 'source':
                dfs[name] = pd.DataFrame(columns=['journal', 'paper', 'author', 'url', 'size_in_kb', 'year', 'ju_url'])
    
    if 'source' not in dfs:
        print("Error: Base ijhs.tsv not found.")
        return

    # Pre-calculate normalized titles for matching
    for df in dfs.values():
        df['_norm_title'] = df['paper'].apply(normalize_title)
        # Ensure year is string for matching
        df['year'] = df['year'].fillna("").astype(str).str.split('.').str[0]

    processed_urls = set()
    new_entries = []
    
    # helper to update JU URL in both files
    def update_ju_url(norm_title, year, ju_url):
        updated = False
        for name, df in dfs.items():
            mask = (df['_norm_title'] == norm_title)
            if not mask.any(): continue
            
            # Sub-mask for exact year match
            year_mask = (df['year'] == str(year))
            if year and (mask & year_mask).any():
                final_mask = mask & year_mask
            elif (mask & (df['year'] == "")).any():
                # Fallback to empty year
                final_mask = mask & (df['year'] == "")
            else:
                final_mask = mask
                
            if final_mask.any():
                idx = df[final_mask].index[0]
                if not df.at[idx, 'ju_url']:
                    df.at[idx, 'ju_url'] = ju_url
                    updated = True
        return updated

    # 2. Parse P60 (RNI Papers)
    print("Parsing P60...")
    p60_data = parse_markdown_table(P60_PATH, "| # | Year | Category |", skip_rows=1)
    for row in p60_data:
        if len(row) < 6: continue
        year = str(row[1]).strip()
        raw_title = row[3]
        author = row[4]
        source = row[5]
        
        title, url = extract_link_and_title(raw_title)
        if not url: continue
        
        # Absolute-ize link if relative
        if url.startswith("../assets/"):
            url = url.replace("../assets/", "https://cahc.jainuniversity.ac.in/assets/")
        
        processed_urls.add(url)
        norm_t = normalize_title(title)
        
        # Check if it's already a primary link in source
        if url in set(dfs['source']['url']):
            continue
            
        # Try to link as JU mirror
        if "jainuniversity" in url:
            if update_ju_url(norm_t, year, url):
                print(f"Linked JU URL for: {title}")
                continue

        # If not linked, it's a new paper
        new_entries.append({
            'journal': source,
            'paper': title,
            'author': author,
            'url': url,
            'ju_url': url if "jainuniversity" in url else "",
            'size_in_kb': 0,
            'year': year
        })

    # 3. Parse P85 (Search Table)
    print("Parsing P85...")
    p85_data = parse_markdown_table(P85_PATH, "| #    | Journal                 |", skip_rows=1)
    for row in p85_data:
        if len(row) < 7: continue
        journal = row[1]
        raw_paper = row[4]
        author = row[5]
        size = row[6]
        
        title, url = extract_link_and_title(raw_paper)
        if not url: continue
        
        if url in processed_urls or url in set(dfs['source']['url']):
            continue
            
        processed_urls.add(url)
        norm_t = normalize_title(title)
        year_match = re.search(r'(\d{4})', journal)
        year = year_match.group(1) if year_match else ""

        # Try to link
        if "jainuniversity" in url:
            if update_ju_url(norm_t, year, url):
                print(f"Linked JU URL for: {title}")
                continue

        new_entries.append({
            'journal': journal,
            'paper': title,
            'author': author,
            'url': url,
            'ju_url': url if "jainuniversity" in url else "",
            'size_in_kb': size,
            'year': year
        })

    # 4. Finalize and Save
    if new_entries:
        print(f"Adding {len(new_entries)} new entries.")
        df_new = pd.DataFrame(new_entries)
        dfs['source'] = pd.concat([dfs['source'], df_new], ignore_index=True)
        # Note: classified will be updated by 03-classify incrementally
        # but we already added 'ju_url' column to it at the start.
    
    # Save back (remove helper col)
    for name, df in dfs.items():
        if '_norm_title' in df.columns:
            df.drop(columns=['_norm_title'], inplace=True)
        
        path = TSV_PATH if name == 'source' else CLASSIFIED_PATH
        df.to_csv(path, sep='\t', index=False)
        print(f"Saved {name} to {path}")

if __name__ == "__main__":
    main()
