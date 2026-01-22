# Scraper Utilities for CAHC Projects

This directory contains utility scripts for scraping and processing Sanskrit texts, historical journals (IJHS), and astronomical data.

## 1. IJHS Workflow (Moved)

The IJHS "Darpan" project has been moved to `../ijhs-darpan/`. Please refer to the [README](../ijhs-darpan/README.md) in that directory.

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
    *   `ijhs/`: IJHS specific data (HTMLs). ( Moved? )
    *   `skanda/`: Text outputs from Skanda Purana scraper.
    *   `logs/`: Log files.
*   `archive~/`: Archived scripts and notebooks.
*   `~scraped-*/`: Legacy specific output folders.
