"""Quick script to capture one image from each available camera."""
import time
import cv2

for index in range(5):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        continue

    # warm up
    for _ in range(3):
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print(f"Camera {index}: opened but failed to read frame")
        continue

    path = f"tmp/test_camera_{index}_{int(time.time())}.jpg"
    cv2.imwrite(path, frame)
    print(f"Camera {index}: saved → {path}  (shape={frame.shape})")
