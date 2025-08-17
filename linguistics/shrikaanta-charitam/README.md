# Shrikaanta Charitam — text processing outputs

This folder contains processing and compiled outputs for the Shrikaanta Charitam text.

Key files

- `01-sams-merged-raw.txt` — merged raw Sanskrit text used as input.
- `02-eng-trans-fn-raw.txt` — English translation / alignment notes.
- `sc-compile.ipynb` — notebook used to compile and clean the text.
- `sc-compiled.tsv` — compiled tsv output (primary processed data).
- `sc-second-cut.csv` — a secondary processed CSV used for downstream analysis.
- `sc.html`, `sc.pdf` — rendered HTML and PDF versions for reading and distribution.

Quick start

1. Open `sc-compile.ipynb` to inspect the processing steps.
2. Use `sc-compiled.tsv` as the canonical processed text for further analysis.

Notes

- Files are relatively large; work with them using streamed readers or pandas with appropriate memory settings.
