import os
import hashlib
from PIL import Image

def calculate_image_hash(image_path):
    """Generate a hash for an image file."""
    try:
        with Image.open(image_path) as img:
            img = img.resize((128, 128)).convert('RGB')  # Standardize size and color mode
            hash_md5 = hashlib.md5(img.tobytes())
            return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def find_and_delete_duplicates(folder_path):
    """Find and delete duplicate images in a folder."""
    hashes = {}
    duplicates = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp')):
                img_hash = calculate_image_hash(file_path)
                if img_hash:
                    if img_hash in hashes:
                        duplicates.append(file_path)
                    else:
                        hashes[img_hash] = file_path
                img_hash = calculate_image_hash(file_path)
    # Delete duplicates
    # for duplicate in duplicates:
    #     try:
    #         os.remove(duplicate)
    #         print(f"Deleted duplicate: {duplicate}")
    #     except Exception as e:
    #         print(f"Could not delete {duplicate}: {e}")

    # print(f"Total duplicates found and deleted: {len(duplicates)}")

# Folder containing images
folder_path = "/Users/gmi/Downloads"  # Replace with the folder path where your images are stored
find_and_delete_duplicates(folder_path)
