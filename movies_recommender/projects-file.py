# download_artifacts.py
import os
import gdown
import time

BASE_PATH = "/var/data"  # Render Disk mount path (must attach a Disk and mount at this path)
os.makedirs(BASE_PATH, exist_ok=True)

# Google Drive file IDs (from your links)
FILES = {
    "vectorizer.joblib": "1j7v9OFNLVN766S1Yf6D6Y0hYpwYOZkn8",
    "movies.pkl": "1poE_gX5xyrtGR314bYuJfb5poRbntFMy",
    "similarity.joblib": "15l4YHYnN-z4sTlG5upGKLcVnRce9lKhg"
}

def download_file_from_drive(file_id: str, dest_path: str):
    """
    Uses gdown which handles Google Drive large-file confirmation automatically.
    """
    url = f"https://drive.google.com/uc?id={file_id}"
    # gdown will follow and get the file even for large files that need confirmation
    tries = 3
    for attempt in range(1, tries + 1):
        try:
            print(f"[{attempt}/{tries}] Downloading {dest_path} from {file_id} ...")
            gdown.download(url, dest_path, quiet=False)
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                print(f"✔ Download completed: {dest_path} ({os.path.getsize(dest_path)} bytes)")
                return True
            else:
                print("! Download completed but file missing or zero-size, retrying...")
        except Exception as e:
            print(f"! Error downloading {file_id}: {e}")
        time.sleep(2)
    return False

def main():
    for name, fid in FILES.items():
        dest = os.path.join(BASE_PATH, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            print(f"Skipping {name} — already exists at {dest}")
            continue

        ok = download_file_from_drive(fid, dest)
        if not ok:
            print(f"ERROR: Failed to download {name}.")
            # Do not raise — we let the app decide; but print for logs.
    print("All attempts finished.")

if __name__ == "__main__":
    main()
