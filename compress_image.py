import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from PIL import Image
import hashlib
import json
import requests
import imagehash
# Your Google API credentials as a dictionary
CREDENTIALS_JSON = {

}
# Scopes required for accessing Google Photos
SCOPES = ['https://www.googleapis.com/auth/photoslibrary']
def authenticate_with_credentials(credentials_json):
    # Load credentials from the JSON directly
    flow = InstalledAppFlow.from_client_config(credentials_json, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

# Authenticate and initialize the Google Photos API service
def initialize_photos_service(creds):
    with open('newfile.json', 'r') as discovery_file:
        discovery_doc = json.load(discovery_file)

    service = build_from_document(discovery_doc, credentials=creds)
    return service
from googleapiclient.discovery import build_from_document
# Retrieve all photos from Google Photos
def get_photos(service, page_size=100):
    photos = []
    next_page_token = None

    while True:
        results = service.mediaItems().list(
            pageSize=page_size,
            pageToken=next_page_token
        ).execute()
        
        media_items = results.get('mediaItems', [])
        photos.extend(media_items)

        next_page_token = results.get('nextPageToken')
        if not next_page_token:
            break

    return photos

# Download an image
def download_image(url, download_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

# Compress the image
def compress_image(input_path, output_path, quality=85):
    try:
        with Image.open(input_path) as img:
            img = img.convert("RGB")
            img.save(output_path, "JPEG", optimize=True, quality=quality)
        return True
    except Exception as e:
        print(f"Error compressing image: {e}")
        return False

# Upload an image to Google Photos
def upload_image(service, file_path):
    try:
        headers = {
            'Authorization': f"Bearer {service._http.credentials.token}",
            'Content-Type': 'application/octet-stream',
            'X-Goog-Upload-Protocol': 'raw',
        }
        with open(file_path, 'rb') as file:
            upload_response = requests.post(
                "https://photoslibrary.googleapis.com/v1/uploads",
                headers=headers,
                data=file
            )
        upload_token = upload_response.text
        if upload_response.status_code == 200 and upload_token:
            # Add the uploaded image to Google Photos
            request_body = {
                "newMediaItems": [
                    {
                        "simpleMediaItem": {
                            "uploadToken": upload_token
                        }
                    }
                ]
            }
            service.mediaItems().batchCreate(body=request_body).execute()
            return True
        else:
            print(f"Error uploading image: {upload_response.text}")
            return False
    except Exception as e:
        print(f"Error uploading image: {e}")
        return False
# Delete original photos
def delete_original_photos(service, photo_ids):
    try:
        for photo_id in photo_ids:
            service.mediaItems().delete(mediaItemId=photo_id).execute()
        print(f"Deleted {len(photo_ids)} original photos.")
    except Exception as e:
        print(f"Error deleting photos: {e}")

# Main function
def main():
       # Assume `creds` is obtained via OAuth
    creds = authenticate_with_credentials(CREDENTIALS_JSON)
    service = initialize_photos_service(creds)

    # Retrieve all photos
    photos = get_photos(service)

    download_dir = "downloads"
    compressed_dir = "compressed"
    original_photo_ids = []
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(compressed_dir, exist_ok=True)

    for photo in photos:
        image_url = photo['baseUrl'] + "=d"  # Downloadable URL
        image_id = photo['id']
        filename = f"{image_id}.jpg"

        download_path = os.path.join(download_dir, filename)
        compressed_path = os.path.join(compressed_dir, filename)

        print(f"Processing {filename}...")

        # Download, compress, and upload
        if download_image(image_url, download_path):
            if compress_image(download_path, compressed_path):
                if upload_image(service, compressed_path):
                    original_photo_ids.append(image_id)
    print(original_photo_ids)
    if original_photo_ids:
        delete_original_photos(service, original_photo_ids)

    print("All images processed and uploaded successfully.")

if __name__ == "__main__":
    main()
