# Patra Darpan

Patra Darpan (Mirror of Documents) is a project to index, classify, and serve the archives of the Indian Journal of History of Science (IJHS) and other scholarly collections of the CAHC.

## Project Structure

This project has been refactored (Jan 2026) into the following components:

- **`pipeline/`**: Data ingestion and processing scripts.
  - `01-scrape.py`: Scrapes metadata from INSA portal.
  - `02-patch.py`: Fixes metadata errors.
  - `03-classify.py`: Uses Gemini LLM to classify new papers.
  - `04-compare.py`: Compares classification with legacy p85 search.
  - `05-import-cahcblr.py`: Imports non-IJHS metadata from Prof. R.N. Iyengar's collection (`p60`).
- **`web/`**: The web application (Netlify).
  - Contains `index.html`, `assets/`, and `netlify/` functions.
- **`ops/`**: Operational and maintenance utilities.
  - `build_data.py`: Generates `data.js` for the web app.
  - `sync_pdfs.py`: Syncs local PDFs to private GCS bucket.
  - `analyze_tsv.py`: Diagnostic tool to identify duplicates and metadata anomalies.
  - `dedupe_tsv.py`: Surgical utility to clean duplicates from `.cache` files.
- **`.cache/`**: Local data store.
  - Contains `ijhs.tsv` (Source of Truth), `ijhs-classified.tsv`, and intermediate artifacts.

## Data Flow Architecture

```mermaid
graph TD
    %% Define Subgraphs (Order influences layout)

    %% 1. Main Project (Left)
    subgraph Project ["Project: ijhs-darpan"]
        subgraph Pipeline
            S1[01-scrape.py]
            S5[05-import-cahcblr.py]
            S2[02-patch.py]
            S3[03-classify.py]
        end

        subgraph LocalStore ["Local Store (.cache)"]
            RawTSV(ijhs.tsv)
            ClassTSV(ijhs-classified.tsv)
            ClassMD(ijhs-classified.md)
        end

        subgraph Ops
            Build[build_data.py]
            Sync[sync_pdfs.py]
            Diag[analyze_tsv.py]
            Dedup[dedupe_tsv.py]
        end

        subgraph WebApp ["Web App"]
            DataJS[data.js]
            NetFunc[Netlify Auth Function]
            NetApp[Darpan UI]
        end
    end

    %% 2. Cloud (Right/Top)
    subgraph Cloud ["Cloud Infrastructure"]
        INSA[INSA Website]
        GCS[Private GCS Bucket]
    end

    %% 3. External (Bottom/Side)
    subgraph External ["External Repo: cahcblr.github.io"]
        Assets["Assets (ijhs_potentials & rni)"]
        P60[p60_papers.md]
        P85[p85_search.md]
        LiveSite((cahc.ju.ac.in))
    end

    %% Data Ingestion
    INSA -->|Scrape Metadata| S1
    INSA -->|Download PDFs| S1
    P60 -->|Parse Metadata| S5
    P85 -->|Parse Metadata| S5
    S1 -->|Save Files| Assets
    S1 -->|Write Metadata| RawTSV
    S5 -->|Merge Metadata| RawTSV

    %% Metadata Refinement
    RawTSV -->|Read| S2 -->|Patch| RawTSV
    RawTSV -->|Read| S3 -->|Classify| ClassTSV
    S3 -->|Generate Report| ClassMD
    ClassTSV -->|Read| Build -->|Generate| DataJS

    %% Legacy Workflow (Manual)
    ClassMD -.->|Manual Copy| P85
    P85 -.->|Jekyll Build| LiveSite

    %% Modern Darpan Workflow (Automated)
    DataJS --> NetApp

    %% Asset Sync & Serving
    Assets -->|Sync Missing| Sync -->|Upload| GCS
    Assets -.->|Dev Mode Serve| NetApp
    GCS -.->|Signed URL| NetFunc -.->|Redirect| NetApp

    %% Subgraph Styles
    style External fill:#e8f5e9,stroke:#66bb6a,stroke-width:2px
    style Cloud fill:#e3f2fd,stroke:#29b6f6,stroke-width:2px
    style Project fill:#fff3e0,stroke:#ffa726,stroke-width:2px

    style Pipeline fill:#fff,stroke:#ccc,stroke-dasharray: 5 5
    style LocalStore fill:#fffde7,stroke:#ccc,stroke-dasharray: 5 5
    style Ops fill:#f3e5f5,stroke:#ccc,stroke-dasharray: 5 5
    style WebApp fill:#e0f2f1,stroke:#ccc,stroke-dasharray: 5 5

    %% Node Styles
    style INSA fill:#f8bbd0,stroke:#333
    style GCS fill:#b39ddb,stroke:#333
    style LiveSite fill:#69f0ae,stroke:#333
    style Assets fill:#fff59d,stroke:#333
```

## Data Lifecycle (Sequence)

This sequence diagram illustrates the step-by-step flow from data ingestion to user serving.

```mermaid
sequenceDiagram
    participant Admin as Developer
    participant INSA as INSA Website
    participant Pipe as Pipeline Scripts
    participant Assets as Local PDFs (Ext)
    participant Cache as .cache (Int)
    participant Cloud as GCS Bucket
    participant Web as Web App

    Note over Admin, Cloud: 1. Ingestion Phase
    Admin->>Pipe: Run 01-scrape / 05-import
    Pipe->>INSA: Fetch HTML & PDFs
    Pipe->>Assets: Download New PDFs
    Pipe->>Cache: Write/Merge ijhs.tsv (Metadata)

    Note over Admin, Cache: 2. Processing Phase
    Admin->>Pipe: Run 02-patch / 03-classify
    Pipe->>Cache: Read & Update Metadata
    Pipe->>Cache: Generate Classified TSV

    Note over Admin, Cloud: 3. Operations Phase
    Admin->>Pipe: Run sync_pdfs.py
    Pipe->>Assets: Scan Local Files
    Pipe->>Cloud: Upload Missing Files
    Admin->>Pipe: Run build_data.py
    Pipe->>Cache: Read Classified TSV
    Pipe->>Web: Generate data.js

    Note over Admin, Web: 4. Serving Phase
    Admin->>Web: Deploy to Netlify
    User->>Web: View Paper
    alt Production
        Web->>Cloud: Request Signed URL
        Cloud-->>Web: Return URL (15m validity)
        Web-->>User: Redirect to Private PDF
    else Local Dev
        Web-->>User: Serve Local PDF directly
    end
```

## Usage

### 1. Data Pipeline

The pipeline scripts should be run in sequence to ensure data integrity:

```bash
uv run pipeline/01-scrape.py   # Scrape new metadata
uv run pipeline/05-import-cahcblr.py # Import non-IJHS metadata
uv run pipeline/02-patch.py    # Fix known metadata errors
uv run pipeline/03-classify.py # Classify new papers
```

### 2. Operations

To regenerate the web application data:

```bash
uv run ops/build_data.py
```

To sync PDFs to GCS (uses local ADC/gcloud credentials):

```bash
uv run ops/sync_pdfs.py       # Summarize and ask for confirmation
uv run ops/sync_pdfs.py -y    # Bypass confirmation (non-interactive)
```

### 3. Diagnostics & Maintenance

Use these tools to maintain the health of the local metadata store:

```bash
uv run ops/analyze_tsv.py   # Find potential duplicates/anomalies
uv run ops/dedupe_tsv.py    # Surgically remove duplicates from .cache
```

### 4. Web Development & Deployment

The Netlify CLI usage differs slightly depending on your objective:

- **Local Development**: Run `dev` from the `web/` directory for a direct local preview.
  ```bash
  cd web
  netlify dev
  ```
- **Local Mode Toggle**: When running `netlify dev`, look for the **Simulation Mode** badge in the header. Click it to toggle between:
  - **Simulation Mode**: Uses INSA for "Read" and GCS (Cloud) for "Archive".
  - **Local Mode**: Uses your local PDF files for "Read" and INSA for "Archive".
- **Production Deployment**: Run `deploy` from the **project root**.
  ```bash
  netlify deploy --prod
  ```

> [!NOTE]
> The root `netlify.toml` serves as the primary configuration for the entire pipeline, while the `web/` directory is treated as a specialized context for local serving.
