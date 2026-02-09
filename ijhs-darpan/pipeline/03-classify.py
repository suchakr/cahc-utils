# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
#     "tqdm",
#     "google-generativeai",
#     "python-dotenv",
#     "pydantic",
# ]
# ///

"""
IJHS Paper Classifier
=====================

Purpose:
    Classifies IJHS papers into Subject (Astronomy, Math, etc.) and Category (Indic, Western, etc.)
    using Google's Gemini LLM.

Usage:
    $ uv run classify_ijhs.py

Logic:
    1. Reads `scraped/ijhs.tsv` (Source of Truth).
    2. Reads `scraped/ijhs-classified.tsv` (Already classified).
    3. Identifies new papers.
    4. Batches them and sends to Gemini for classification.
    5. Appends results to `scraped/ijhs-classified.tsv`.
    6. Generates a searchable HTML/Markdown report (`scraped/ijhs-classified.md`).
"""

import os
import json
import time
import pickle
import pandas as pd
from tqdm import tqdm
from time import sleep
import google.generativeai as genai
from google.generativeai.types import RequestOptions
from google.api_core import retry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Relative path to cache
CACHE_DIR = os.path.join(os.path.dirname(__file__), "../.cache")

# --- Caching Utility ---
class Cache2Disk(): 
  """Simple disk cache using pickle."""
  def __init__(self, *args):
    # Cache to /tmp or current folder's .cache needed? 
    # Using local .cache for persistence across runs if /tmp is ephemeral
    # cache_dir = os.path.join(os.getcwd(), ".cache")
    cache_dir = CACHE_DIR
    os.makedirs(cache_dir, exist_ok=True)
    filename = os.path.join(cache_dir, '_'.join(['cache'] + list(map(str, args))) + ".pkl")
    self.filename = filename

  def save(self, item):
    self.item = item  
    with open(self.filename, 'wb') as f:
      pickle.dump(self.item, f)
    return self.item

  def load(self):
    try :
      with open(self.filename, 'rb') as f:
        self.item = pickle.load(f)
    except:
      self.item = None

    if self.item is None : raise Exception("Cache miss")
    return self.item

# --- Classifier Logic ---
class TextGeminiClassifier():
  def __init__(self):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    
    genai.configure(api_key=api_key)
    self.model = genai.GenerativeModel(
      model_name="gemini-1.5-flash",
      generation_config=genai.GenerationConfig(
        temperature=0.0,
        top_p=0.95,
        top_k=5,
        max_output_tokens=8192,
        response_mime_type="text/plain",
      ),
    )
    self.label = "gemini_classify_text"

  def model_system_prompt(self):  
    return """
    You are an expert in history of science. 
    Classify each paper into its best Subject and best Category. Do not return empty classifications.

    Subject (choose exactly one string):
      Astronomy
      Math
      Medicine
      Agriculture
      Culture
      Metallurgy
      MindSciences
      Biology
      Philosophy
      Linguistics
      Music
      Other

    Category (choose exactly one string):
      Indic
      Arabic
      Western
      Fareast
      Other

    Please provide your classifications in strictly valid JSON format.
    Example of the expected JSON structure:
      {
        "classifications": [
          {
            "subject": "Math",
            "category": "Indic",
            "journal": "IJHS...",
            "paper": "Title of paper..."
          }
        ]
      }    
    """

  def prep_response_text(self, response_text):
    try:
      # Extract JSON from markdown block if present
      if "```json" in response_text:
          return response_text.split("```json")[1].split("```")[0].strip()
      if "```" in response_text:
           return response_text.split("```")[1].split("```")[0].strip()
      return response_text
    except Exception as e:
      return response_text

  def classify_one_batch(self, in_df):
    prompt = f"""{self.model_system_prompt()}
Papers: {in_df[['journal', 'paper']].to_dict(orient='records')}
"""
    retry_policy = RequestOptions(
        retry = retry.Retry(predicate=retry.if_transient_error, initial=10, multiplier=1.5, timeout=300)
    )
    return self.model.generate_content(prompt, request_options=retry_policy)

  def classify_df(self, df, batch_size=15):
    results = []
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    pbar = tqdm(enumerate(range(0, len(df), batch_size)), 
                desc="Classifying Papers", 
                total=total_batches, 
                unit='batch')
    
    for ix, i in pbar:
      # Define cache key based on batch items to be robust? 
      # Or mostly relying on index if deterministic sort. 
      # Let's use a hash of the first paper title + index for robustness
      # For now, simple index based cache key as per original notebook
      batch_key = f"{i}-{i+batch_size}"
      cache = Cache2Disk(self.label, batch_key)
      
      try:
        response = cache.load()
        # Validation checks could go here
      except Exception:
        # Generate
        batch_df = df.iloc[i:i+batch_size]
        try:
            response = self.classify_one_batch(batch_df)
            cache.save(response)
        except Exception as e:
            pbar.write(f"Error classifying batch {ix}: {e}")
            continue

      try:
        response_text = self.prep_response_text(response.text)
        data = json.loads(response_text)
        batch_results = pd.DataFrame(data['classifications'])
        results.append(batch_results)
      except Exception as e:
        pbar.write(f"Error parsing batch {ix}: {e}")
    
    if not results:
        return pd.DataFrame()
        
    return pd.concat(results).reset_index(drop=True)

# --- Main Flow ---

def main():
    # 1. Load Source
    source_path = os.path.join(CACHE_DIR, 'ijhs.tsv')
    if not os.path.exists(source_path):
        print(f"{source_path} not found.")
        return
    source_df = pd.read_csv(source_path, sep='\t')
    source_df['paper'] = source_df['paper'].str.strip()
    # Deduplicate source by URL
    source_df = source_df.drop_duplicates(subset=['url'])
    
    # 2. Load Existing Classifications
    classified_file = os.path.join(CACHE_DIR, 'ijhs-classified.tsv')
    if os.path.exists(classified_file):
        classified_df = pd.read_csv(classified_file, sep='\t')
        classified_df['paper'] = classified_df['paper'].str.strip()
        
        # Only treat as "already classified" if subject AND category are not null/empty
        is_classified = classified_df['subject'].notna() & classified_df['category'].notna()
        classified_subset = classified_df[is_classified]
        
        existing_keys = set(zip(classified_subset['journal'], classified_subset['paper']))
    else:
        classified_df = pd.DataFrame()
        existing_keys = set()
        
    print(f"Total Papers in Source: {len(source_df)}")
    print(f"Already Classified: {len(existing_keys)}")
    
    # 3. Filter New
    # We append 'to_classify' list
    to_classify_mask = source_df.apply(lambda x: (x['journal'], x['paper']) not in existing_keys, axis=1)
    to_classify_df = source_df[to_classify_mask].copy()
    
    print(f"Papers to Classify: {len(to_classify_df)}")
    
    # --- Noise Filter (Heuristic Classification) ---
    # Disabled Dropping, but we want to Auto-Classify them to save LLM calls
    noise_patterns = [
        'Contents', 'News', 'Announcements', 'Book Review', 'Reviews', 
        'Volume Contents', 'Office Bearers', 'Title Page'
    ]
    
    # Filter case-insensitive substring
    noise_mask = to_classify_df['paper'].str.lower().str.contains('|'.join([p.lower() for p in noise_patterns]), na=False)
    
    # Identify meta papers
    meta_df = to_classify_df[noise_mask].copy()
    if not meta_df.empty:
        print(f"Auto-classifying {len(meta_df)} Meta/Noise papers...")
        meta_df['subject'] = 'General'
        meta_df['category'] = 'Other'
        meta_df['reasoning'] = 'Heuristic: Meta content'
        
        # Add to results immediately
        # We need to structure it like the LLM output DF?
        # No, generate_markdown expects a DF with these cols. 
        # But classify_df returns a DF. We can concat later.
    
    # Remove from LLM queue
    to_classify_df = to_classify_df[~noise_mask]
    
    # Explicitly SAVE "Historical Notes" even if they match something (unlikely now that Notes is gone)
    
    # Filter case-insensitive substring
    # noise_mask = to_classify_df['paper'].str.lower().str.contains('|'.join([p.lower() for p in noise_patterns]), na=False)
    
    # Explicitly SAVE "Historical Notes" even if they match something (unlikely now that Notes is gone)
    # But just in case
    # save_mask = to_classify_df['paper'].str.contains('Historical Note', case=False)
    # final_mask = noise_mask & ~save_mask
    
    # to_classify_df = to_classify_df[~noise_mask]
    # print(f"Papers after Noise Filtering: {len(to_classify_df)} (Dropped {noise_mask.sum()} noise items)")

    new_results_df = pd.DataFrame()

    if len(to_classify_df) > 0:
        # 4. Classify
        classifier = TextGeminiClassifier()
        new_classifications = classifier.classify_df(to_classify_df)
        
        if not new_classifications.empty:
            new_results_df = new_classifications
        else:
            print("No valid classifications returned.")
            
    # Append the Auto-Classified Meta papers
    if not meta_df.empty:
         # Ensure columns match
         # classify_df returns [journal, paper, subject, category, reasoning] usually
         # We added these cols to meta_df already
         new_results_df = pd.concat([new_results_df, meta_df[['journal', 'paper', 'subject', 'category', 'reasoning']]])
    
    # 5. Merge and Save
    # We want to combine existing classifications with new ones, 
    # BUT we want to ensure we have the latest metadata (URL, Size, Author) from source_df.
    
    # Combine classifications (Just Subject/Category)
    all_classifications = pd.DataFrame()
    if not classified_df.empty:
        all_classifications = classified_df[['journal', 'paper', 'subject', 'category']].copy()
    
    if not new_results_df.empty:
        all_classifications = pd.concat([all_classifications, new_results_df[['journal', 'paper', 'subject', 'category']]])
    
    # Deduplicate classifications just in case
    all_classifications.drop_duplicates(subset=['journal', 'paper'], keep='last', inplace=True)
    
    # Merge with source to get rich metadata
    # Use right merge to ensure ALL papers from source_df are kept, even if classification match fails
    final_df = pd.merge(all_classifications, source_df, on=['journal', 'paper'], how='right')
    
    # Save TSV (Simpler version for data persistence)
    final_df.to_csv(classified_file, index=False, sep='\t')
    print(f"Saved {len(final_df)} classifications to {classified_file}")

    # 6. Generate Markdown/HTML Report
    if not final_df.empty:
        generate_markdown(final_df)

def generate_markdown(df, output_path=None):
    if output_path is None:
        output_path = os.path.join(CACHE_DIR, "ijhs-classified.md")
    """Generates a searchable HTML/Markdown report."""
    
    # Get distinct categories for the dropdown
    # Fill N/A for safe sorting
    df['category'] = df['category'].fillna('N/A').astype(str)
    categories = sorted(df['category'].unique())
    
    # Use a flat string to avoid Markdown code block indentation issues (4 spaces)
    js_css_template = """
<style>
/* Search and Filter Styles */
.controls-container {
margin-bottom: 20px;
display: flex;
gap: 10px;
align_items: center;
flex-wrap: wrap;
}
#myInput {
background-image: url('https://w7.pngwing.com/pngs/399/963/png-transparent-magnifying-glass-computer-icons-magnifying-glass-glass-search-engine-optimization-detective.png');
background-position: 10px 10px;
background-repeat: no-repeat;
background-size: 20px;
width: 100%;
max-width: 300px;
font-size: 16px;
padding: 12px 20px 12px 40px;
border: 1px solid #ddd;
border-radius: 4px;
}
#categoryFilter {
padding: 12px;
font-size: 16px;
border: 1px solid #ddd;
border-radius: 4px;
min-width: 150px;
}
#exportBtn {
padding: 12px 20px;
background-color: #4CAF50;
color: white;
border: none;
border-radius: 4px;
cursor: pointer;
font-size: 16px;
}
#exportBtn:hover {
background-color: #45a049;
}
.highlight {
background-color: yellow;
}
/* Ensure the table is styled if not handled by global CSS */
table {
border-collapse: collapse;
width: 100%;
margin-top: 20px;
}
th, td {
text-align: left;
padding: 12px;
border-bottom: 1px solid #ddd;
}
tr.header, tr:hover {
background-color: #f1f1f1;
}
</style>

<div class="controls-container">
<input type="text" id="myInput" onkeyup="debounceSearch()" placeholder="Search papers, authors...">
<select id="categoryFilter" onchange="filterTable()">
<option value="">All Categories</option>
PLACEHOLDER_OPTIONS
</select>
<button id="exportBtn" onclick="exportTableAsMarkdown()">Export as Markdown</button>
</div>

<script>
let debounceTimer;
function debounceSearch() {
clearTimeout(debounceTimer);
debounceTimer = setTimeout(filterTable, 200);
}
function filterTable() {
var input, filter, table, tr, td, i, txtValue;
input = document.getElementById("myInput");
filter = input.value.toUpperCase();
categorySelect = document.getElementById("categoryFilter");
categoryFilter = categorySelect.value.toUpperCase();
table = document.querySelector("table");
if (!table) return;
tr = table.getElementsByTagName("tr");
for (i = 0; i < tr.length; i++) {
if (tr[i].getElementsByTagName("th").length > 0) {
continue;
}
var cells = tr[i].getElementsByTagName("td");
for (var c = 0; c < cells.length; c++) {
var cell = cells[c];
if (cell.innerHTML.indexOf('span class="highlight"') !== -1) {
cell.innerHTML = cell.innerHTML.replace(/<span class="highlight">([^<]*)<\/span>/g, '$1');
}
}
var showRow = true;
var rowText = tr[i].textContent || tr[i].innerText;
if (filter && rowText.toUpperCase().indexOf(filter) === -1) {
showRow = false;
}
var categoryTd = cells[3]; 
if (categoryTd) {
var categoryText = categoryTd.textContent || categoryTd.innerText;
if (categoryFilter && categoryText.toUpperCase().indexOf(categoryFilter) === -1) {
showRow = false;
}
}
if (showRow) {
tr[i].style.display = "";
if (filter) {
highlightMatch(tr[i], filter);
}
} else {
tr[i].style.display = "none";
}
}
}
function highlightMatch(row, filter) {
var cells = row.getElementsByTagName("td");
for (var j = 0; j < cells.length; j++) {
var cell = cells[j];
if (cell.innerHTML.indexOf('<a') === -1) {
var innerHTML = cell.innerHTML;
var index = innerHTML.toUpperCase().indexOf(filter);
if (index >= 0) { 
var regex = new RegExp('(' + filter + ')', 'gi');
cell.innerHTML = innerHTML.replace(regex, '<span class="highlight">$1</span>');
}
}
}
}
function exportTableAsMarkdown() {
const table = document.querySelector("table");
const rows = Array.from(table.getElementsByTagName("tr"));
let markdown = "";
const ths = Array.from(rows[0].getElementsByTagName("th"));
if (ths.length > 0) {
const headers = ths.map(th => th.innerText.trim());
markdown += "| " + headers.join(" | ") + " |\\n";
markdown += "| " + headers.map(() => "---").join(" | ") + " |\\n";
}
rows.forEach((row) => {
if (row.style.display !== "none" && row.getElementsByTagName("td").length > 0) {
const cells = Array.from(row.getElementsByTagName("td"));
const rowData = cells.map(cell => {
if (cell.querySelector('a')) {
return `[${cell.innerText}](${cell.querySelector('a').href})`;
}
return cell.innerText.trim();
});
markdown += "| " + rowData.join(" | ") + " |\\n";
}
});
const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
const url = window.URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = "ijhs-papers-export.md";
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
}
</script>
"""
    
    # Generate Options options
    options_html = ""
    for cat in categories:
        options_html += f'<option value="{cat}">{cat}</option>\n'
    
    js_css_template = js_css_template.replace("PLACEHOLDER_OPTIONS", options_html)

    md = "# IJHS Classified Papers\n\n"
    md += f"**Total Papers**: {len(df)}\n\n"
    md += "Type in the input field to search the table by Paper title or Author.\n\n"
    
    md += js_css_template + "\n\n"
    
    # Markdown Table Generation
    md += "| # | Journal | Subject | Category | Paper | Author | Size (KB) |\n"
    md += "|---|---|---|---|---|---|---|\n"
    
    for i, row in df.reset_index().iterrows():
        title = str(row.get('paper', '')).replace('|', '-')
        url = row.get('url', '#')
        if isinstance(url, str):
            url = url.replace(' ', '%20')
            
        subject = row.get('subject', 'N/A')
        category = row.get('category', 'N/A')
        author = row.get('author', '')
        size = row.get('size_in_kb', '')
        if pd.isna(size) or str(size).lower() == 'nan':
            size = ''
        else:
             try:
                 size = str(int(float(size)))
             except:
                 pass
            
        journal = row.get('journal', 'IJHS') 
        journal_display = journal.replace('Indian Journal of History of Science', 'IJHS').replace('Vol ', 'Vol.')
        
        md += f"| {i+1} | {journal_display} | {subject} | {category} | [{title}]({url}) | {author} | {size} |\n"
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Markdown report generated: {output_path}")


if __name__ == "__main__":
    main()
