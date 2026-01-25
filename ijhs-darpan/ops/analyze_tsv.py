# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
# ]
# ///

import pandas as pd
import os
import re
import pathlib

# Configuration
BASE_DIR = pathlib.Path(__file__).parent.parent
TSV_PATH = BASE_DIR / ".cache" / "ijhs.tsv"

if not TSV_PATH.exists():
    print(f"TSV not found at {TSV_PATH}")
    exit(1)

df = pd.read_csv(TSV_PATH, sep='\t', dtype=str).fillna('')

def normalize_title(t):
    return re.sub(r'[^a-zA-Z0-9]', '', t.lower())

def get_filename(url):
    if not url: return ''
    return url.split('/')[-1].split('?')[0].split('#')[0]

df['norm_title'] = df['paper'].map(normalize_title)
df['filename'] = df['url'].map(get_filename)

# Group by filename
filename_dupes = df[df.duplicated('filename', keep=False)].sort_values('filename')

# Group by title + author
df['norm_author'] = df['author'].map(normalize_title)
df['title_author_key'] = df['norm_title'] + "|" + df['norm_author']

# Noise filter: ignore very short titles like "Supplement"
def is_noise(t):
    return len(t) < 15

print('--- CROSS-SOURCE OVERLAPS (Same Filename) ---')
filename_count = 0
for name, group in filename_dupes.groupby('filename'):
    if not name: continue
    if len(group) > 1:
        sources = set()
        for _, row in group.iterrows():
            if 'insa.nic.in' in row['url']: sources.add('INSA')
            if 'cahc.jainuniversity' in row['url']: sources.add('CAHC')
        
        if len(sources) > 1:
            filename_count += (len(group) - 1)
            print(f'\nFilename: {name}')
            for _, row in group.iterrows():
                print(f'  - Journal: {row["journal"]} | Source: {"INSA" if "insa" in row["url"] else "CAHC"}')

print(f'\nTotal items to remove (Filename match): {filename_count}')

print('\n--- CROSS-SOURCE OVERLAPS (Same Title + Author, excludes filename match) ---')
title_auth_count = 0
unique_filenames = {f for f in filename_dupes['filename'] if f}

title_auth_dupes = df[df.duplicated('title_author_key', keep=False)].sort_values('title_author_key')

for key, group in title_auth_dupes.groupby('title_author_key'):
    if is_noise(group.iloc[0]['norm_title']):
        continue
        
    sources = set()
    for _, row in group.iterrows():
        if 'insa.nic.in' in row['url']: sources.add('INSA')
        if 'cahc.jainuniversity' in row['url']: sources.add('CAHC')
    
    # Only if it spans both sources and wasn't caught by filename
    if len(sources) > 1:
        all_caught = all(row['filename'] in unique_filenames for _, row in group.iterrows() if row['filename'])
        if not all_caught:
            title_auth_count += (len(group) - 1)
            print(f'\nTitle: {group.iloc[0]["paper"]}')
            print(f'Author: {group.iloc[0]["author"]}')
            for _, row in group.iterrows():
                 print(f'  - Journal: {row["journal"]} | URL: {row["url"]}')

print(f'\nTotal items to remove (Title+Author match): {title_auth_count}')
print(f'\nGRAND TOTAL: {filename_count + title_auth_count}')
