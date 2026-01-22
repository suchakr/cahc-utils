# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-cloud-storage",
# ]
# ///
import os
import glob
from google.cloud import storage

# Configuration
BUCKET_NAME = "cahcblr-pdfs"
PROJECT_ID = "gen-lang-client-0854320022"
# Configuration
BUCKET_NAME = "cahcblr-pdfs"
PROJECT_ID = "gen-lang-client-0854320022"

# Auto-load credentials if gcs-key.json exists in this directory
key_path = os.path.join(os.path.dirname(__file__), 'gcs-key.json')
if os.path.exists(key_path) and 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
    print(f"Using credentials from {key_path}")

# IMPORTANT: Update these paths to point to your local PDF repositories
# I checked `../../assets/pdfs` but it was empty. 
# Please verify where 'ijhs_potentials' resides on your machine.
LOCAL_DIRS = [
    "/Users/sunder/projects/cahcblr.github.io/assets/ijhs_potentials",
    "/Users/sunder/projects/cahcblr.github.io/assets/cached_papers/rni"
]

def sync_pdfs():
    print(f"Connecting to GCS bucket: {BUCKET_NAME} in project {PROJECT_ID}...")
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        
        # List existing blobs
        print("Listing existing files in bucket...")
        blobs = list(bucket.list_blobs())
        existing_files = {blob.name for blob in blobs}
        print(f"Found {len(existing_files)} files in bucket.")
        
        # Scan local files
        local_files = []
        for dir_path in LOCAL_DIRS:
            abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), dir_path))
            print(f"Scanning local directory: {abs_path}")
            if not os.path.exists(abs_path):
                 print(f"Warning: Directory not found: {abs_path}")
                 continue
                 
            files = glob.glob(os.path.join(abs_path, "**/*.pdf"), recursive=True)
            for f in files:
                filename = os.path.basename(f)
                local_files.append((filename, f))
                
        print(f"Found {len(local_files)} local PDF files.")
        
        # Gap Analysis
        print("\n--- Gap Analysis ---")
        missing_ops = []
        for filename, filepath in local_files:
            target_blob_name = f"assets/ijhs/{filename}"
            if target_blob_name not in existing_files:
                missing_ops.append((target_blob_name, filepath))

        print(f"Total Local Files: {len(local_files)}")
        print(f"Total Bucket Objects (All Paths): {len(existing_files)}")
        print(f"Files to be Uploaded (Missing in assets/ijhs/): {len(missing_ops)}")

        if not missing_ops:
            print("Bucket is fully synchronized! No actions needed.")
            return

        print("\nSample of missing files:")
        for name, _ in missing_ops[:10]:
            print(f" - {name}")
        
        if len(missing_ops) > 100:
             print(f"... and {len(missing_ops) - 10} more.")

        print("\nStarting Upload (Auto-Resume)...")
        
        # Sync
        uploaded_count = 0
        for target_blob_name, filepath in missing_ops:
            print(f"Uploading: {target_blob_name}")
            blob = bucket.blob(target_blob_name)
            blob.upload_from_filename(filepath)
            uploaded_count += 1
                
        print(f"Sync complete. Uploaded {uploaded_count} files.")

    except Exception as e:
        print(f"Error: {e}")
        print("Ensure you have authenticated with 'gcloud auth application-default login' or set GOOGLE_APPLICATION_CREDENTIALS.")

if __name__ == "__main__":
    sync_pdfs()
