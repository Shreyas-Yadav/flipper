import logging
import os
import threading
import time
from pathlib import Path

import cv2

_TMP_DIR = Path(__file__).parent / "tmp"
log = logging.getLogger(__name__)


class _CameraReader:
    """Continuously reads frames from a camera in a background thread."""

    def __init__(self, index: int):
        self._cap = cv2.VideoCapture(index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open camera {index}")
        for _ in range(3):          # flush stale AVFoundation frames
            self._cap.read()
        self._frame = None
        self._lock = threading.Lock()
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def _run(self):
        while True:
            ret, frame = self._cap.read()
            if ret:
                with self._lock:
                    self._frame = frame

    def get_frame(self):
        with self._lock:
            return self._frame

    def is_opened(self) -> bool:
        return self._cap.isOpened()


_readers: dict[int, _CameraReader] = {}


def get_reader(index: int) -> _CameraReader:
    if index not in _readers or not _readers[index].is_opened():
        _readers[index] = _CameraReader(index)
    return _readers[index]


def capture_page(camera_index: int | None = None) -> str:
    test_image = os.environ.get("TEST_IMAGE")
    if test_image:
        log.info("TEST_IMAGE set — skipping webcam, using %s", test_image)
        return test_image

    if camera_index is None:
        camera_index = int(os.environ.get("CAMERA_INDEX", 0))

    reader = get_reader(camera_index)

    # Wait up to 2 s for the first frame
    deadline = time.time() + 2.0
    frame = reader.get_frame()
    while frame is None and time.time() < deadline:
        time.sleep(0.05)
        frame = reader.get_frame()

    if frame is None:
        raise RuntimeError("Failed to capture frame from camera")

    _TMP_DIR.mkdir(exist_ok=True)
    path = str(_TMP_DIR / f"flipper_page_{int(time.time())}.jpg")
    cv2.imwrite(path, frame)
    log.info("Frame saved to %s (shape=%s)", path, frame.shape)
    return path
