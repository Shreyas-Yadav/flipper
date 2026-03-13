import logging
import os
import sys

import readchar
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
# silence noisy third-party loggers
for _noisy in ("httpcore", "httpx", "openai", "urllib3"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)

from capture import capture_page
from drive import append_to_doc
from ocr import extract_text
from tts import speak

_REQUIRED_ENV = ["FEATHERLESS_API_KEY", "SMALLEST_API_KEY"]


def _check_env() -> None:
    missing = [k for k in _REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        print(f"Error: missing environment variables: {', '.join(missing)}")
        sys.exit(1)


def main() -> None:
    _check_env()

    page_num = 0
    last_text = ""

    print("Robotic Book Reader ready.")
    print("  Enter — next page  |  r — read aloud  |  q — quit")

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
            append_to_doc(last_text, page_num)
            page_num += 1
            print("Reading aloud...")
            speak(last_text)

        elif key == "r":
            if last_text:
                print("Reading aloud...")
                speak(last_text)
            else:
                print("No page captured yet.")


if __name__ == "__main__":
    main()
