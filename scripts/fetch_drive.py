import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# === CONFIG ===
STAGING_PATH = "staging"
DRIVE_FOLDER_ID = "10RMT08oF-uU1Xk6cAYkvF6eyswC_Udp7"

CLIENT_ID = os.environ["GDRIVE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GDRIVE_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["GDRIVE_REFRESH_TOKEN"]

def get_drive_service():
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    creds.refresh(Request())
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
        print(f"Downloading {filename}: {int(status.progress() * 100)}%")

def main():
    os.makedirs(STAGING_PATH, exist_ok=True)

    service = get_drive_service()

    # List files in your folder
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType='application/pdf'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        print("No PDF files found in Drive folder.")
    else:
        for file in files:
            print(f"Downloading: {file['name']}")
            download_file(service, file['id'], file['name'])

if __name__ == "__main__":
    main()

