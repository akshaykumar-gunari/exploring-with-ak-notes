import os
import io
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials

# === CONFIG ===
STAGING_PATH = "staging"
META_PATH = "meta"
DRIVE_FOLDER_ID = "10RMT08oF-uU1Xk6cAYkvF6eyswC_Udp7"

# Path to your Service Account JSON key
SERVICE_ACCOUNT_FILE = "service_account.json"

def get_drive_service():
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    service = build('drive', 'v3', credentials=creds)
    return service

def download_file(service, file_id, filename):
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(STAGING_PATH, filename)
    fh = io.FileIO(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"⬇️ Downloading {filename}: {int(status.progress() * 100)}%")

def main():
    os.makedirs(STAGING_PATH, exist_ok=True)
    os.makedirs(META_PATH, exist_ok=True)

    service = get_drive_service()

    # List PDF files in folder
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType='application/pdf'"
    results = service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
    files = results.get('files', [])

    if not files:
        print("⚠️ No PDF files found in Drive folder.")
    else:
        for file in files:
            file_id = file['id']
            filename = file['name']
            modified_time = file['modifiedTime']

            base_name, _ = os.path.splitext(filename)
            meta_file = os.path.join(META_PATH, f"{base_name}.json")

            if os.path.exists(meta_file):
                with open(meta_file) as f:
                    meta = json.load(f)
                if meta.get("modifiedTime") == modified_time:
                    print(f"✅ Skipping unchanged: {filename}")
                    continue

            print(f"⬇️ Downloading new or updated: {filename}")
            download_file(service, file_id, filename)

            with open(meta_file, "w") as f:
                json.dump({"modifiedTime": modified_time}, f)

if __name__ == "__main__":
    main()
