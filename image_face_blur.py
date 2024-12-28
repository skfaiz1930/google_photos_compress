import cv2
import numpy as np
import os

def detect_and_blur_faces(image_path, save_path, overwrite=False):
    """
    Detects faces in an image and blurs them.

    Args:
        image_path (str): Path to the input image.
        save_path (str): Path to save the output image.
        overwrite (bool): Whether to overwrite the original image.

    Returns:
        str: Path to the saved image.
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read the image at {image_path}")

    # Load the pre-trained Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert the image to grayscale for face detection
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Blur each detected face
    for (x, y, w, h) in faces:
        # Extract the face region
        face_region = image[y:y+h, x:x+w]

        # Apply a Gaussian blur
        blurred_face = cv2.GaussianBlur(face_region, (51, 51), 30)

        # Replace the original face region with the blurred one
        image[y:y+h, x:x+w] = blurred_face

    # Determine the save path
    if overwrite:
        save_path = image_path

    # Save the output image
    cv2.imwrite(save_path, image)
    return save_path

# Example usage
input_image = "face.jpg"  # Path to your input image
output_image = "output.jpg"  # Path to save the blurred image
save_path = detect_and_blur_faces(input_image, output_image, overwrite=False)
print(f"Blurred image saved to: {save_path}")
