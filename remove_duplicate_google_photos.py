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

def calculate_image_hash_from_url(image_url):
    """Generate a hash for an image from its URL."""
    try:
        # from io import BytesIO
        # from urllib.request import urlopen
        # response = urlopen(image_url)
        # img = Image.open(BytesIO(response.read())).resize((128, 128)).convert('RGB')
        # hash_md5 = hashlib.md5(img.tobytes())
        # return hash_md5.hexdigest()
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        image = Image.open(response.raw).convert('RGB')
        # Use perceptual hashing
        return str(imagehash.phash(image))
    except Exception as e:
        print(f"Error processing {image_url}: {e}")
        return None
# Find duplicates based on filename or other metadata
def find_duplicates(photos):
    seen = {}
    duplicates = []

    for photo in photos:
        filename = photo.get('filename')
        if filename in seen:
            print(filename,'filename')
            duplicates.append(photo)
        else:
            seen[filename] = photo

    return duplicates

# Delete duplicates
def delete_duplicates(service, duplicates):
    for photo in duplicates:
        media_item_id = photo.get('id')
        try:
            service.mediaItems().delete(mediaItemId=media_item_id).execute()
            print(f"Deleted: {photo.get('filename')}")
        except Exception as e:
            print(f"Failed to delete {photo.get('filename')}: {e}")

# Main script
if __name__ == '__main__':
    # Assume `creds` is obtained via OAuth
    creds = authenticate_with_credentials(CREDENTIALS_JSON)
    service = initialize_photos_service(creds)

    # Retrieve all photos
    photos = get_photos(service)
    hashes = {}
    duplicates = []
    print(f"Total photos retrieved: {len(photos)}")
    for photo in photos:
            image_url = photo['baseUrl'] + "=w240-h240"  # Lower resolution (240x240)
            image_id = photo['id']
            img_hash = calculate_image_hash_from_url(image_url)
            print(img_hash,'img_hash')
            if img_hash:
                if img_hash in hashes:
                    duplicates.append(image_id)
                    print(img_hash,'duplicates')
                else:
                    hashes[img_hash] = image_id

    print(f"Total duplicates found: {len(duplicates)}")
    # Find duplicates
    # duplicates = find_duplicates(photos)
    # print(f"Total duplicates found: {len(duplicates)}")

    # Delete duplicates
    # delete_duplicates(service, duplicates)
