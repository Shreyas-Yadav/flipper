import logging
import os

import requests
import sounddevice as sd
from scipy.io import wavfile

log = logging.getLogger(__name__)

_STT_PATH = "/tmp/flipper_stt.wav"
_SAMPLE_RATE = 16000
_STT_URL = "https://api.smallest.ai/waves/v1/pulse/get_text"


def listen_for_command(duration: float = 3.0) -> str:
    log.info("Recording %.1fs of audio at %dHz...", duration, _SAMPLE_RATE)
    audio = sd.rec(
        int(duration * _SAMPLE_RATE),
        samplerate=_SAMPLE_RATE,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    log.debug("Recording complete, shape=%s", audio.shape)

    wavfile.write(_STT_PATH, _SAMPLE_RATE, audio)
    log.debug("WAV saved to %s", _STT_PATH)

    log.info("Sending audio to Smallest.ai Pulse STT...")
    api_key = os.environ["SMALLEST_API_KEY"]
    with open(_STT_PATH, "rb") as f:
        response = requests.post(
            _STT_URL,
            params={"language": "en"},
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "audio/wav",
            },
            data=f.read(),
            timeout=30,
        )
    log.debug("STT response status=%d", response.status_code)
    response.raise_for_status()

    text = response.json().get("transcription", "").strip().lower()
    log.info("Transcription: %r", text)
    return text
