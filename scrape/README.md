# Scraper Utilities for CAHC Projects

This directory contains utility scripts for scraping and processing Sanskrit texts, historical journals (IJHS), and astronomical data.

## 1. IJHS Workflow (Indian Journal of History of Science)

The processing of IJHS data follows a strict numerical sequence to ensure data integrity.

### Workflow Scripts
1.  **`ijhs-01-scrape.py`** (formerly `ijhs-scraper.py`)
    *   **Function**: Scrapes the INSA website using Selenium.
    *   **Output**: Downloads raw HTML to `scraped/ijhs/html~/` and creates `scraped/ijhs.tsv`.
2.  **`ijhs-02-patch.py`** (formerly `patch_ijhs.py`)
    *   **Function**: Corrects known metadata errors in the source (e.g., mislabeled years/volumes).
    *   **Usage**: Run immediately after scraping to clean `ijhs.tsv`.
3.  **`ijhs-03-classify.py`** (formerly `classify_ijhs.py`)
    *   **Function**: Classifies papers using LLMs (Gemini) and generates the final output.
    *   **Output**: `scraped/ijhs-classified.md` (Searchable Table) and `ijhs-classified.tsv`.
4.  **`ijhs-04-compare.py`** (formerly `compare_journals.py`)
    *   **Function**: Validation tool to compare the new dataset against the legacy `p85` list.

---

## 2. Puranas & Wikisource Scrapers

Scripts targeting `sa.wikisource.org` for various classical texts.

*   **`skanda-purana-scrape.py`**: Recursive scraper for Skanda Purana, Naishadhiya Charitam, etc. Outputs to `scraped/skanda/`.
*   **`brahmanda-purana-scrape.py`**: Scrapes Brahmanda Purana. Outputs to `~scraped-topic/`.
*   **`rv-scrape.py`**: Scrapes Rigveda Mandalas. Outputs to `~scraped-rv/`.
*   **`vishnu-purana-scrape.py`**: Scrapes Vishnu Purana text.
*   **`kss_scrape.ipynb`**: Notebook for Kathasaritsagara.

## 3. Other Utilities

*   **`ramayana-iitk-scrape.py`**: Scrapes Valmiki Ramayana from IIT Kanpur.
*   **`astropixels-moon-phase.py`**: Scrapes moon phase data.
*   **`verb-extractor.ipynb`**: NLP analysis of Sanskrit verb forms.

## 4. Directory Structure

*   `scraped/`: Primary output directory.
    *   `ijhs/`: IJHS specific data (HTMLs).
    *   `skanda/`: Text outputs from Skanda Purana scraper.
    *   `logs/`: Log files.
*   `archive~/`: Archived scripts and notebooks.
*   `~scraped-*/`: Legacy specific output folders.
