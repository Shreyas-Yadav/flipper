import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel

load_dotenv(Path(__file__).parent.parent / ".env")

_logs_enabled = "--logs" in sys.argv
logging.basicConfig(
    level=logging.DEBUG if _logs_enabled else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
if _logs_enabled:
    for _noisy in ("httpcore", "httpx", "openai", "urllib3"):
        logging.getLogger(_noisy).setLevel(logging.WARNING)

import cv2

from capture import capture_page
from ocr import extract_text
from tts import speak, synthesize

app = FastAPI(title="Flipper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SpeakRequest(BaseModel):
    text: str


async def _mjpeg_frames(camera_index: int):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
            )
            await asyncio.sleep(1 / 15)  # ~15 fps
    finally:
        cap.release()


@app.get("/stream")
def stream(camera: int = Query(default=0)):
    return StreamingResponse(
        _mjpeg_frames(camera),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/cameras")
def list_cameras():
    available = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
    return {"cameras": available, "active": int(os.environ.get("CAMERA_INDEX", 0))}


@app.post("/flip")
def flip():
    """Run the arm flip script."""
    script = os.environ.get("FLIP_SCRIPT")
    if not script:
        raise HTTPException(status_code=501, detail="FLIP_SCRIPT env var not set")

    conda_env = os.environ.get("FLIP_CONDA_ENV", "lerobot")
    result = subprocess.run(
        ["conda", "run", "-n", conda_env, "python3", script],
        capture_output=True, text=True,
        cwd=str(Path(script).parent),
    )
    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"Flip script failed:\n{result.stderr.strip()}",
        )

    return {"ok": True}


@app.post("/capture")
def capture(camera: int = Query(default=None)):
    idx = camera if camera is not None else None
    path = capture_page(camera_index=idx)
    text = extract_text(path)
    return {"imagePath": path, "text": text}


@app.post("/speak", status_code=204)
def speak_endpoint(req: SpeakRequest):
    speak(req.text)


@app.post("/tts")
def tts_endpoint(req: SpeakRequest):
    audio = synthesize(req.text)
    return Response(content=audio, media_type="audio/wav")


@app.get("/image")
def serve_image(path: str):
    resolved = Path(path).resolve()
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(resolved, media_type="image/jpeg")
