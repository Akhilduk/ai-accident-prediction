from __future__ import annotations

from datetime import datetime
from pathlib import Path


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def timestamped_name(name: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = name.replace(" ", "_")
    return f"{stamp}_{safe}"
