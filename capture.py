import logging
import time

import cv2

log = logging.getLogger(__name__)


def capture_page(camera_index: int = 0) -> str:
    log.debug("Opening camera index=%d", camera_index)
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        log.error("Cannot open camera %d", camera_index)
        raise RuntimeError(f"Cannot open camera {camera_index}")

    log.debug("Camera opened, capturing frame...")
    ret, frame = cap.read()
    cap.release()
    log.debug("Camera released")

    if not ret:
        log.error("Frame capture returned False")
        raise RuntimeError("Failed to capture frame from camera")

    path = f"/tmp/flipper_page_{int(time.time())}.jpg"
    cv2.imwrite(path, frame)
    log.info("Frame saved to %s (shape=%s)", path, frame.shape)
    return path
