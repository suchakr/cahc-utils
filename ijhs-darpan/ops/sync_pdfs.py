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

def sync_pdfs(force_yes=False, diff_only=False, delete_orphans=False, deep=False, report_misplaced=False, detailed=False):
    print(f"Connecting to GCS bucket: {BUCKET_NAME} in project {PROJECT_ID}...")
    print("Using Application Default Credentials (ADC).")
    
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        
        if deep:
            remote_prefix = "assets/"
            local_base = os.path.expanduser("~/projects/cahcblr.github.io/assets")
            print(f"\n[DEEP MODE] Comparing entire '{remote_prefix}' prefix...")
        else:
            remote_prefix = "assets/ijhs/"
            local_base = None
            print(f"\n[STANDARD MODE] Comparing IJHS assets ({remote_prefix})...")

        # List existing blobs
        print(f"Listing blobs in bucket with prefix '{remote_prefix}'...")
        blobs = list(bucket.list_blobs(prefix=remote_prefix))
        
        if deep:
            existing_remote = {blob.name: blob for blob in blobs}
        else:
            existing_remote = {os.path.basename(blob.name): blob for blob in blobs}
            
        print(f"Found {len(existing_remote)} items in GCS.")
        
        # Scan local files
        local_files = []
        if deep:
            print(f"Scanning local directory recursively: {local_base}")
            for root, _, files in os.walk(local_base):
                for f in files:
                    abs_path = os.path.join(root, f)
                    rel_path = os.path.relpath(abs_path, os.path.dirname(local_base))
                    if not rel_path.startswith("assets/"):
                        rel_path = os.path.join("assets", os.path.relpath(abs_path, local_base))
                    local_files.append((rel_path, abs_path, rel_path))
        else:
            for dir_path in LOCAL_DIRS:
                abs_dir = os.path.expanduser(dir_path)
                if not os.path.exists(abs_dir):
                    print(f"Warning: Directory not found: {abs_dir}")
                    continue
                print(f"Scanning local directory: {abs_dir}")
                files = glob.glob(os.path.join(abs_dir, "**/*.pdf"), recursive=True)
                for f in files:
                    filename = os.path.basename(f)
                    target_rel_path = f"assets/ijhs/{filename}"
                    local_files.append((target_rel_path, f, filename))
                
        print(f"Found {len(local_files)} local files.")
        
        # Comparison logic
        to_upload = []
        up_to_date = 0
        
        local_by_path = {rel: abs_p for rel, abs_p, _ in local_files}
        local_by_name = {}
        for rel, abs_p, _ in local_files:
            name = os.path.basename(rel)
            if name not in local_by_name:
                local_by_name[name] = []
            local_by_name[name].append((rel, abs_p))

        true_orphans = []
        misplaced = []
        
        for remote_path, blob in existing_remote.items():
            name = os.path.basename(remote_path)
            
            # 1. Exact Path Match
            if remote_path in local_by_path:
                local_abs = local_by_path[remote_path]
                if blob.size == os.path.getsize(local_abs):
                    up_to_date += 1
                else:
                    to_upload.append(("UPDATE", remote_path, local_abs))
                    
            # 2. Filename Match (Misplaced)
            elif name in local_by_name:
                local_matches = [m[0] for m in local_by_name[name]]
                misplaced.append((remote_path, local_matches))
                if not report_misplaced:
                    # Unless reporting misplaced specifically, consider it "safe" or up-to-date
                    up_to_date += 1
                
            # 3. True Orphan
            else:
                true_orphans.append((remote_path, blob))

        # Check for Local files that don't exist in GCS at all
        for target_rel, abs_path, _ in local_files:
            if target_rel not in existing_remote:
                to_upload.append(("NEW", target_rel, abs_path))

        print("\n--- Sync Summary ---")
        print(f"Total Local Files: {len(local_files)}")
        print(f"Already Up-to-date: {up_to_date}")
        if report_misplaced:
            print(f"Misplaced in GCS:  {len(misplaced)}")
        print(f"Pending Uploads:   {len(to_upload)}")
        print(f"True Orphans in GCS: {len(true_orphans)}")
        
        if misplaced and report_misplaced:
            print("\nFiles misplaced in GCS (matching name, different path):")
            limit = None if detailed else 15
            for remote_path, locals in (misplaced[:limit] if limit else misplaced):
                print(f" [MISPLACED] {remote_path}")
                print(f"    -> Locally at: {', '.join(locals)}")
            if not detailed and len(misplaced) > 15:
                print(f" ... and {len(misplaced) - 15} more. (Use --detailed to see all)")

        if true_orphans:
            print("\nTrue Orphans (in GCS but not found locally at all):")
            limit = None if detailed else 15
            for path, _ in (true_orphans[:limit] if limit else true_orphans):
                print(f" [TRUE ORPHAN] {path}")
            if not detailed and len(true_orphans) > 15:
                print(f" ... and {len(true_orphans) - 15} more. (Use --detailed to see all)")

        if to_upload:
            print("\nBreakdown of pending uploads:")
            new_count = len([x for x in to_upload if x[0] == "NEW"])
            update_count = len([x for x in to_upload if x[0] == "UPDATE"])
            print(f" - [NEW]    {new_count} files")
            print(f" - [UPDATE] {update_count} files (size mismatch)")
            
            if diff_only:
                print("\nSample of pending files:")
                limit = None if detailed else 15
                for action, target, _ in (to_upload[:limit] if limit else to_upload):
                    print(f" [{action}] {target}")
                if not detailed and len(to_upload) > 15:
                    print(f"... and {len(to_upload) - 15} more. (Use --detailed to see all)")

        if diff_only:
            print("\nDiff complete. No changes were made.")
            return

        # Handle Uploads
        if to_upload:
            if not force_yes:
                resp = input(f"\nProceed to upload {len(to_upload)} files to GCS? [y/N]: ")
                if resp.lower() != 'y':
                    print("Upload aborted.")
                else:
                    print("\nStarting Upload...")
                    uploaded_count = 0
                    for action, target, abs_path in to_upload:
                        print(f"({action}) Uploading: {target}")
                        blob = bucket.blob(target)
                        blob.upload_from_filename(abs_path)
                        uploaded_count += 1
                    print(f"Successfully uploaded {uploaded_count} files.")
        else:
            print("\nNo pending uploads.")

        # Handle Deletions (Orphans)
        all_removals = true_orphans + ([(m[0], None) for m in misplaced] if report_misplaced else [])
        if all_removals and delete_orphans:
            print(f"\nWARNING: Found {len(all_removals)} items to delete from GCS.")
            if not force_yes:
                resp = input(f"Proceed to DELETE {len(all_removals)} items? [y/N]: ")
                if resp.lower() != 'y':
                    print("Deletion aborted.")
                else:
                    print("\nStarting Deletion...")
                    deleted_count = 0
                    for path, blob in all_removals:
                        print(f" (DELETE) Deleting: {path}")
                        if not blob:
                            blob = bucket.blob(path)
                        blob.delete()
                        deleted_count += 1
                    print(f"Successfully deleted {deleted_count} files.")
        elif true_orphans or (misplaced and report_misplaced):
            print("\nRun with --delete-orphans to remove true orphans (and misplaced if reporting) from GCS.")

        print("\nSync operations complete.")

    except Exception as e:
        print(f"Error: {e}")
        print("\nIf you see a 403 or Auth error, ensure you have ran:")
        print("  gcloud auth application-default login")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Synchronize local PDFs/assets to GCS bucket.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # See what's missing in IJHS prefix
  python ops/sync_pdfs.py --diff
  
  # See everything missing/orphaned across all assets
  python ops/sync_pdfs.py --diff-deep --report-misplaced
  
  # Clean up orphans only
  python ops/sync_pdfs.py --diff-deep --delete-orphans
"""
    )
    parser.add_argument("-y", "--yes", action="store_true", help="Bypass confirmation prompts.")
    parser.add_argument("--diff", action="store_true", help="Dry-run: Only show differences within IJHS scope.")
    parser.add_argument("--diff-deep", action="store_true", help="Dry-run: Compare entire assets/ directory recursively.")
    parser.add_argument("--report-misplaced", action="store_true", help="Reveal files that exist locally but at a different path.")
    parser.add_argument("--detailed", action="store_true", help="Show all files in the report (no trimming).")
    parser.add_argument("--delete-orphans", action="store_true", help="Delete files in GCS that are missing locally.")
    
    args = parser.parse_args()
    
    # --diff or --diff-deep implies dry-run
    is_diff = args.diff or args.diff_deep
    
    sync_pdfs(
        force_yes=args.yes, 
        diff_only=is_diff, 
        delete_orphans=args.delete_orphans, 
        deep=args.diff_deep,
        report_misplaced=args.report_misplaced,
        detailed=args.detailed
    )
