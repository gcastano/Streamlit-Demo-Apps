import cv2
import numpy as np
import os

def detect_and_blur_faces(image_path, cascade_path):
    # Load the image and convert to grayscale
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image at {image_path}")
        return
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Load the Haar cascade classifier
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print(f"Error: Could not load cascade at {cascade_path}")
        return

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))

    # Iterate over detected faces and blur them
    for (x, y, w, h) in faces:
        # Extract the face ROI
        face_roi = img[y:y+h, x:x+w]
        
        # Apply a Gaussian blur (adjust kernel size for more/less blur)
        # The kernel size (ksize) must be odd, e.g., (25, 25)
        blurred_face = cv2.GaussianBlur(face_roi, (25, 25), 0)
        
        # Put the blurred face back into the original image
        img[y:y+h, x:x+w] = blurred_face

    # Display the result
    cv2.imshow("Blurred Faces", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Optionally save the output image
    # cv2.imwrite("output_blurred_face.jpg", img)

# Example usage:
# Make sure to provide the correct paths to your image and XML cascade file
image_path = os.path.join(os.path.dirname(__file__), "foto1.jpg")
cascade_path = os.path.join(os.path.dirname(__file__), "modelo/haarcascade_frontalface_default.xml")
detect_and_blur_faces(image_path, cascade_path)
