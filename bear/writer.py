import subprocess
import time
from pathlib import Path
from urllib.parse import quote, urlencode


def create_note(title: str, text: str = "", tags: list[str] | None = None) -> None:
    params = {"title": title, "text": text}
    if tags:
        params["tags"] = ",".join(tags)
    params_urlencode = urlencode(params, quote_via=quote)
    url = f"bear://x-callback-url/create?{params_urlencode}"
    run(url)


def import_file(file_path: str) -> None:
    path = Path(file_path)
    content = path.read_text()
    title = path.stem  # fallback

    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    create_note(title="", text=content)


def trash_note(note_id: str) -> None:
    params = urlencode({"id": note_id}, quote_via=quote)
    url = f"bear://x-callback-url/trash?{params}"
    run(url)


def run(url: str) -> None:
    subprocess.run(["open", url], check=True)
    time.sleep(1)


def open_note(note_id: str) -> None:
    params = urlencode({"id": note_id}, quote_via=quote)
    url = f"bear://x-callback-url/open-note?{params}"
    run(url)
