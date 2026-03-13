import logging
import os
import subprocess
from pathlib import Path

import requests

log = logging.getLogger(__name__)

_TMP_DIR = Path(__file__).parent / "tmp"
_TTS_PATH = _TMP_DIR / "flipper_tts.wav"


def _synthesize_direct(text: str, voice_id: str) -> bytes:
    """Direct HTTP call to lightning-v3.1 endpoint, bypassing the SDK."""
    url = "https://api.smallest.ai/waves/v1/lightning-v3.1/get_speech"
    headers = {
        "Authorization": f"Bearer {os.environ['SMALLEST_API_KEY']}",
        "Content-Type": "application/json",
    }
    payload = {"text": text, "voice_id": voice_id,
               "sample_rate": 24000, "output_format": "wav"}
    log.debug("Direct POST to %s with voice_id=%s", url, voice_id)
    res = requests.post(url, json=payload, headers=headers)
    log.debug("Response status=%d, size=%d bytes",
              res.status_code, len(res.content))
    if res.status_code != 200:
        raise RuntimeError(f"TTS API error {res.status_code}: {res.text}")
    return res.content


def synthesize(text: str) -> bytes:
    """Return WAV bytes without playing — for streaming to clients."""
    voice_id = os.environ.get("SMALLEST_VOICE_ID") or "magnus"
    text = " ".join(text.split())
    log.info("Synthesising speech for %d chars...", len(text))
    return _synthesize_direct(text, voice_id)


def speak(text: str) -> None:
    voice_id = os.environ.get("SMALLEST_VOICE_ID") or "magnus"
    log.debug("Using voice_id=%s", voice_id)

    text = " ".join(text.split())  # collapse newlines/whitespace
    log.info("Synthesising speech for %d chars...", len(text))
    log.debug("TTS input text: %r", text)
    audio_bytes = _synthesize_direct(text, voice_id)
    log.debug("Received %d audio bytes — first 20: %s",
              len(audio_bytes), audio_bytes[:20])

    _TMP_DIR.mkdir(exist_ok=True)
    with open(_TTS_PATH, "wb") as f:
        f.write(audio_bytes)
    log.debug("Audio saved to %s", _TTS_PATH)

    log.info("Playing audio via afplay...")
    subprocess.run(["afplay", _TTS_PATH], check=True)
    log.info("Playback complete")
