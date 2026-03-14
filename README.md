# Flipper

A robotic book reader. Point a webcam at a book, press a button, and Flipper captures the page, extracts the text via VLM OCR, and reads it aloud. An optional robotic arm (SO-100) automatically turns the pages.

---

## How it works

1. **Camera preview** — live MJPEG feed from your webcam in the browser
2. **Capture** — snapshot is sent to a vision model (OpenRouter) for OCR
3. **TTS** — extracted text is synthesized to audio and played in the browser
4. **Flip** — triggers the SO-100 robotic arm to turn the page, then captures automatically

---

## Project structure

```text
flipper/
├── backend/          # FastAPI server + Python modules
│   ├── server.py     # HTTP API (capture, flip, stream, tts)
│   ├── capture.py    # Webcam capture with shared frame reader
│   ├── ocr.py        # VLM-based OCR via OpenRouter
│   ├── tts.py        # Text-to-speech via SmallestAI
│   ├── main.py       # CLI entry point (keyboard-driven)
│   └── tmp/          # Captured images (gitignored)
├── frontend/         # Next.js app
│   └── app/
│       ├── page.tsx  # Main UI
│       └── api/      # Proxy routes → backend
└── arm/              # SO-100 arm motion scripts
    └── SO100-Motion-Recorder-Playback/
        ├── record_poses.py   # Record waypoints to poses.json
        └── replay_poses.py   # Replay saved waypoints
```

---

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Node.js 18+
- A webcam
- OpenRouter API key (for OCR)
- SmallestAI API key (for TTS)
- *(Optional)* SO-100 arm + `lerobot` conda environment

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/Shreyas-Yadav/flipper.git
cd flipper

# Backend
uv sync

# Frontend
cd frontend && npm install
```

### 2. Configure environment

Create a `.env` file at the project root:

```env
# OCR
OCR_API_KEY=your_openrouter_key
OCR_BASE_URL=https://openrouter.ai/api/v1
OCR_MODEL=google/gemini-flash-1.5

# TTS
SMALLEST_API_KEY=your_smallestai_key
SMALLEST_VOICE_ID=magnus

# Camera (0 = default webcam)
CAMERA_INDEX=0

# Arm (optional)
FLIP_SCRIPT=/path/to/flipper/arm/SO100-Motion-Recorder-Playback/replay_poses.py
FLIP_CONDA_ENV=lerobot
```

### 3. Run

**Terminal 1 — backend:**

```bash
cd backend
uv run uvicorn server:app --reload
```

**Terminal 2 — frontend:**

```bash
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## API endpoints

| Method | Path                | Description                      |
| ------ | ------------------- | -------------------------------- |
| GET    | `/stream?camera=0`  | MJPEG live camera feed           |
| GET    | `/cameras`          | List available cameras           |
| POST   | `/capture?camera=0` | Capture page + OCR               |
| POST   | `/flip?camera=0`    | Trigger arm flip + capture + OCR |
| POST   | `/tts`              | Synthesize text → WAV audio      |
| GET    | `/image?path=...`   | Serve a captured image           |

---

## Robotic arm setup

The arm scripts live in `arm/SO100-Motion-Recorder-Playback/`.

**Record a flip motion:**

```bash
conda run -n lerobot python3 arm/SO100-Motion-Recorder-Playback/record_poses.py
```

**Test replay manually:**

```bash
conda run -n lerobot python3 arm/SO100-Motion-Recorder-Playback/replay_poses.py
```

Once verified, set `FLIP_SCRIPT` in `.env` to the absolute path of `replay_poses.py` and the Flip button will trigger it automatically.

---

## CLI mode

Run Flipper without the frontend:

```bash
cd backend
uv run python main.py          # normal mode
uv run python main.py --logs   # with debug logging
```

Keyboard shortcuts: `c` capture · `p` play · `q` quit
