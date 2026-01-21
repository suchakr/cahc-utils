# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
# ]
# ///

import pandas as pd

tsv_path = 'scraped/ijhs.tsv'
print(f"Reading {tsv_path}...")
df = pd.read_csv(tsv_path, sep='\t')

# Logic to fix Issue 2 -> Issue 3 for Vol 49
# Also fix IJHS-47 (2012) mislabeled as 2011/Vol 46
# Also fix IJHS-42 (2007) mislabeled as 2006/Vol 41 (if applicable)
# Also fix IJHS-24 (1989) mislabeled

corrections = [
    # (Wrong Journal Name, URL pattern, Correct Journal Name)
    ('IJHS-49-2014-Issue-2', 'Vol49_3', 'IJHS-49-2014-Issue-3'),
    ('IJHS-46-2011-Issue-3', 'Vol47_3', 'IJHS-47-2012-Issue-3'), # Fix Manda Puzzle etc
    ('IJHS-41-2006-Issue-2', 'Vol42_2', 'IJHS-42-2007-Issue-2'), # Historical Note BG Tilak
    ('IJHS-24-1989-Issue-2', 'Vol24_3', 'IJHS-24-1989-Issue-3'), # Fix issue 3 overlap
]

count = 0
for wrong_journal, url_pattern, correct_journal in corrections:
    try:
        mask = (df['journal'] == wrong_journal) & (df['url'].str.contains(url_pattern, na=False))
        matches = mask.sum()
        if matches > 0:
            print(f"Patching {matches} rows: {wrong_journal} -> {correct_journal}")
            df.loc[mask, 'journal'] = correct_journal
            count += matches
    except Exception as e:
        print(f"Error checking {wrong_journal}: {e}")

if count > 0:
    df.to_csv(tsv_path, sep='\t', index=False)
    print(f"Total patched and saved: {count}")
else:
    print("No rows found to patch.")
