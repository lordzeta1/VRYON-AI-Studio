import re
from pathlib import Path

def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", name).strip("-")
    return cleaned[:60] or "vyron-project"

def ensure_output_dir():
    path = Path("outputs")
    path.mkdir(exist_ok=True)
    return path
