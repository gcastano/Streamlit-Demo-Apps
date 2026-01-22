import cv2
import os
import io

def blur_video(cascade_path, video_source):
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print(f"Error: Could not load cascade at {cascade_path}")
        return

    cap = cv2.VideoCapture(video_source.getvalue())
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    videoBytes = io.BytesIO()
    out = cv2.VideoWriter(videoBytes, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Blur the face ROI
            frame[y:y+h, x:x+w] = cv2.GaussianBlur(frame[y:y+h, x:x+w], (25, 25), 0)
        out.write(frame)
        cv2.imshow('Face Blurring Live', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # Finally, add this:
    out.release()
    cv2.destroyAllWindows()
    return videoBytes

# Example usage:
# Make sure to provide the correct path to your XML cascade file
video_path = os.path.join(os.path.dirname(__file__), "video1.mp4")
cascade_path = os.path.join(os.path.dirname(__file__), "modelo/haarcascade_frontalface_default.xml")
blur_video(cascade_path, video_path)
