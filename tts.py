import logging
import os
import subprocess

from smallestai.waves import WavesClient

log = logging.getLogger(__name__)

_client: WavesClient | None = None
_TTS_PATH = "/tmp/flipper_tts.wav"


def _get_client() -> WavesClient:
    global _client
    if _client is None:
        log.debug("Initialising Smallest.ai WavesClient")
        _client = WavesClient(api_key=os.environ["SMALLEST_API_KEY"])
    return _client


def speak(text: str) -> None:
    voice_id = os.environ.get("SMALLEST_VOICE_ID")
    kwargs = {"sample_rate": 24000, "speed": 1.0}
    if voice_id:
        kwargs["voice_id"] = voice_id
        log.debug("Using voice_id=%s", voice_id)

    log.info("Synthesising speech for %d chars...", len(text))
    audio_bytes = _get_client().synthesize(text, **kwargs)
    log.debug("Received %d audio bytes", len(audio_bytes))

    with open(_TTS_PATH, "wb") as f:
        f.write(audio_bytes)
    log.debug("Audio saved to %s", _TTS_PATH)

    log.info("Playing audio via afplay...")
    subprocess.run(["afplay", _TTS_PATH], check=True)
    log.info("Playback complete")
