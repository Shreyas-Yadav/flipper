import logging
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent

import readchar
from dotenv import load_dotenv

load_dotenv()

_logs_enabled = "--logs" in sys.argv

logging.basicConfig(
    level=logging.DEBUG if _logs_enabled else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
if _logs_enabled:
    for _noisy in ("httpcore", "httpx", "openai", "urllib3"):
        logging.getLogger(_noisy).setLevel(logging.WARNING)

from capture import capture_page
from ocr import extract_text
from tts import speak

_REQUIRED_ENV = ["OCR_API_KEY", "SMALLEST_API_KEY"]


def _check_env() -> None:
    missing = [k for k in _REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        print(f"Error: missing environment variables: {', '.join(missing)}")
        sys.exit(1)


def main() -> None:
    _check_env()

    if "--test-tts" in sys.argv:
        os.environ.setdefault("TEST_IMAGE", str(_PROJECT_ROOT / "test-img.png"))
        print("[test-tts] Using test image:", os.environ["TEST_IMAGE"])

    page_num = 0
    last_text = ""

    print("Robotic Book Reader ready.")
    print("  Enter — next page  |  r — read aloud  |  q — quit")

    try:
        while True:
            key = readchar.readkey()

            if key == "q":
                print("Goodbye.")
                break

            elif key in (readchar.key.ENTER, "\r", "\n", " "):
                print("Capturing page...")
                path = capture_page()
                print(f"Extracting text from {path}...")
                last_text = extract_text(path)
                print("\n--- Page text ---")
                print(last_text)
                print("-----------------\n")
                page_num += 1
                speak(last_text)
                print(f"✓ Page {page_num} complete — captured, extracted, read aloud.\n")

            elif key == "r":
                if last_text:
                    speak(last_text)
                    print("✓ Done reading.\n")
                else:
                    print("No page captured yet.")

    except KeyboardInterrupt:
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
