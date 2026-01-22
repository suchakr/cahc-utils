import os
import re

def normalize_text(text):
    return re.sub(r'\s+', ' ', str(text).strip().lower())

def parse_markdown_table(filepath):
    papers = {} # Key: (Journal, Title), Value: Full Row Data
    duplicates = []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    start_table = False
    header_indices = {}
    
    for line in lines:
        if "| # | Journal |" in line or "| # | Journal |" in line:
            start_table = True
            # Parse header to find indices matching known columns
            # Standard: | # | Journal | Subject | Category | Paper | Author | ...
            headers = [h.strip() for h in line.split('|') if h.strip()]
            try:
                header_indices['journal'] = headers.index('Journal')
                header_indices['paper'] = headers.index('Paper')
                header_indices['author'] = headers.index('Author')
            except ValueError:
                print(f"Error parsing headers in {filepath}: {headers}")
                return {}, []
            continue
            
        if not start_table:
            continue
        if "|---" in line:
            continue
        if not line.strip().startswith("|"):
            continue
            
        parts = [p.strip() for p in line.split('|')[1:-1]] # Remove empty start/end logic from split('|')
        
        if len(parts) < max(header_indices.values()) + 1:
            continue
            
        journal = parts[header_indices['journal']]
        
        # Extract title from markdown link if present [Title](url)
        raw_paper = parts[header_indices['paper']]
        title_match = re.search(r'\[(.*?)\]\(.*?\)', raw_paper)
        title = title_match.group(1) if title_match else raw_paper
        
        author = parts[header_indices['author']]
        
        key = (journal.strip(), normalize_text(title))
        
        if key in papers:
            duplicates.append(key)
        else:
            papers[key] = {
                'journal': journal,
                'title': title,
                'author': author,
                'original_line': line.strip()
            }
            
    return papers, duplicates

p85_path = "/Users/sunder/projects/cahcblr.github.io/p85_search.markdown"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "../.cache")
ijhs_path = os.path.join(CACHE_DIR, "ijhs-classified.md")

print(f"--- Processing p85 ---")
p85_papers, p85_dupes = parse_markdown_table(p85_path)
print(f"Total Unique Entries: {len(p85_papers)}")
if p85_dupes:
    print(f"Duplicates found: {len(p85_dupes)}")

print(f"\n--- Processing IJHS Classified ---")
ijhs_papers, ijhs_dupes = parse_markdown_table(ijhs_path)
print(f"Total Unique Entries: {len(ijhs_papers)}")
if ijhs_dupes:
    print(f"Duplicates found: {len(ijhs_dupes)}")

# Comparison
p85_keys = set(p85_papers.keys())
ijhs_keys = set(ijhs_papers.keys())

only_in_p85 = p85_keys - ijhs_keys
only_in_ijhs = ijhs_keys - p85_keys

# Check for "Moved" papers (Same Title, Different Journal)
# Index ijhs by Title
ijhs_by_title = {}
for k, v in ijhs_papers.items():
    ijhs_by_title[v['title']] = v

moved_papers = []
truly_missing = []

for k in only_in_p85:
    entry = p85_papers[k]
    title = entry['title']
    
    # Try to find title in ijhs (normalized check already done in key, but let's be sure)
    # The key is (Journal, NormalizedTitle). 
    # Check if any IJHS entry has the same NormalizedTitle
    found_match = False
    for ijhs_k, ijhs_v in ijhs_papers.items():
         if ijhs_k[1] == k[1]: # Same normalized title
             moved_papers.append((entry, ijhs_v))
             found_match = True
             break
    
    if not found_match:
        truly_missing.append(entry)

print(f"\n--- GAP ANALYSIS RESULTS ---")

if moved_papers:
    print(f"\nMOVED / RENAMED PAPERS ({len(moved_papers)}):")
    print("(Present in both, but Journal ID changed)")
    for old, new in sorted(moved_papers, key=lambda x: x[0]['title']):
        print(f"  Title: {old['title']}")
        print(f"    p85 : {old['journal']}")
        print(f"    New : {new['journal']}")

print(f"\nTRULY MISSING IN NEW LIST ({len(truly_missing)}):")
for entry in sorted(truly_missing, key=lambda x: x['journal']):
    print(f"  [{entry['journal']}] {entry['title']}")

print(f"\nEntries ONLY in ijhs-classified ({len(only_in_ijhs)}):")
# Group by Journal for cleaner output
from collections import defaultdict
new_by_journal = defaultdict(list)
for k in only_in_ijhs:
    entry = ijhs_papers[k]
    new_by_journal[entry['journal']].append(entry['title'])

for journal in sorted(new_by_journal.keys()):
    print(f"  {journal}:")
    for title in sorted(new_by_journal[journal]):
        print(f"    - {title}")
