import logging
import os
import time
from pathlib import Path

import cv2

_TMP_DIR = Path(__file__).parent / "tmp"

log = logging.getLogger(__name__)


def capture_page(camera_index: int | None = None) -> str:
    test_image = os.environ.get("TEST_IMAGE")
    if test_image:
        log.info("TEST_IMAGE set — skipping webcam, using %s", test_image)
        return test_image

    if camera_index is None:
        camera_index = int(os.environ.get("CAMERA_INDEX", 0))

    log.debug("Opening camera index=%d", camera_index)
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        log.error("Cannot open camera %d", camera_index)
        raise RuntimeError(f"Cannot open camera {camera_index}")

    log.debug("Camera opened, warming up...")
    for _ in range(3):
        cap.read()  # flush buffered frames from the wrong camera

    log.debug("Capturing frame...")
    ret, frame = cap.read()
    cap.release()
    log.debug("Camera released")

    if not ret:
        log.error("Frame capture returned False")
        raise RuntimeError("Failed to capture frame from camera")

    _TMP_DIR.mkdir(exist_ok=True)
    path = str(_TMP_DIR / f"flipper_page_{int(time.time())}.jpg")
    cv2.imwrite(path, frame)
    log.info("Frame saved to %s (shape=%s)", path, frame.shape)
    return path
