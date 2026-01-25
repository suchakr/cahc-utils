# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-cloud-storage",
# ]
# ///
import os
import glob
import argparse
from google.cloud import storage

# Configuration
BUCKET_NAME = "cahcblr-pdfs"
PROJECT_ID = "gen-lang-client-0854320022"

# IMPORTANT: These paths point to local PDF repositories
# They are resolved relative to the user's home directory.
LOCAL_DIRS = [
    "~/projects/cahcblr.github.io/assets/ijhs_potentials",
    "~/projects/cahcblr.github.io/assets/cached_papers/rni"
]

def sync_pdfs(force_yes=False):
    print(f"Connecting to GCS bucket: {BUCKET_NAME} in project {PROJECT_ID}...")
    print("Using Application Default Credentials (ADC).")
    
    try:
        # Client will automatically use ADC from environment (e.g. gcloud auth)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        
        # List existing blobs
        print("Listing existing files in bucket (this may take a moment)...")
        blobs = list(bucket.list_blobs(prefix="assets/ijhs/"))
        # Create a map of filename -> blob for size comparison
        existing_blobs = {os.path.basename(blob.name): blob for blob in blobs}
        print(f"Found {len(existing_blobs)} files in 'assets/ijhs/' prefix.")
        
        # Scan local files
        local_files = []
        for dir_path in LOCAL_DIRS:
            abs_path = os.path.expanduser(dir_path)
            print(f"Scanning local directory: {abs_path}")
            if not os.path.exists(abs_path):
                 print(f"Warning: Directory not found: {abs_path}")
                 continue
                 
            files = glob.glob(os.path.join(abs_path, "**/*.pdf"), recursive=True)
            for f in files:
                filename = os.path.basename(f)
                local_files.append((filename, f))
                
        print(f"Found {len(local_files)} local PDF files.")
        
        # Gap Analysis (By existence and size)
        to_upload = []
        up_to_date = 0
        
        for filename, filepath in local_files:
            local_size = os.path.getsize(filepath)
            
            if filename not in existing_blobs:
                to_upload.append(("NEW", filename, filepath))
            else:
                remote_blob = existing_blobs[filename]
                if remote_blob.size != local_size:
                    to_upload.append(("UPDATE", filename, filepath))
                else:
                    up_to_date += 1

        print("\n--- Sync Summary ---")
        print(f"Total Local Files: {len(local_files)}")
        print(f"Already Up-to-date: {up_to_date}")
        print(f"Pending Actions: {len(to_upload)}")
        
        if not to_upload:
            print("Bucket is fully synchronized! No actions needed.")
            return

        print("\nBreakdown of actions:")
        new_count = len([x for x in to_upload if x[0] == "NEW"])
        update_count = len([x for x in to_upload if x[0] == "UPDATE"])
        print(f" - [NEW]    {new_count} files")
        print(f" - [UPDATE] {update_count} files (size mismatch)")

        print("\nSample of pending files:")
        for action, name, _ in to_upload[:10]:
            print(f" [{action}] {name}")
        
        if len(to_upload) > 10:
             print(f"... and {len(to_upload) - 10} more.")

        # Interactive Consent
        if not force_yes:
            resp = input(f"\nProceed to upload {len(to_upload)} files to GCS? [y/N]: ")
            if resp.lower() != 'y':
                print("Aborted.")
                return

        print("\nStarting Upload...")
        
        # Sync
        uploaded_count = 0
        for action, filename, filepath in to_upload:
            target_blob_name = f"assets/ijhs/{filename}"
            print(f"({action}) Uploading: {target_blob_name}")
            blob = bucket.blob(target_blob_name)
            blob.upload_from_filename(filepath)
            uploaded_count += 1
                
        print(f"\nSync complete. Successfully processed {uploaded_count} files.")

    except Exception as e:
        print(f"Error: {e}")
        print("\nIf you see a 403 or Auth error, ensure you have ran:")
        print("  gcloud auth application-default login")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize local PDFs to GCS.")
    parser.add_argument("-y", "--yes", action="store_true", help="Bypass confirmation prompt.")
    args = parser.parse_args()
    
    sync_pdfs(force_yes=args.yes)
