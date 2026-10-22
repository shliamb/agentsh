import re
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from settings import REQUIREMENTS_FILE

"""Pre-flight checks: virtual environment and required dependencies."""

def is_in_venv() -> bool:
    """True if Python runs inside a virtual environment."""
    return sys.prefix != sys.base_prefix


def _parse_requirements(path: Path) -> list[str]:
    """Read requirements.txt, return list of distribution names."""
    if not path.exists():
        return []
    names = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith(("-", "--")):
            continue  # -r, -e, --index-url — пока пропускаем
        line = line.split(";", 1)[0].strip()       # убрать env markers
        line = re.sub(r"\[.*?\]", "", line)        # убрать extras: httpx[http2]
        name = re.split(r"[<>=!~ ]", line, maxsplit=1)[0]
        if name:
            names.append(name)
    return names


def find_missing_deps() -> list[str]:
    """Return names of packages from requirements.txt that are not installed."""
    missing = []
    for name in _parse_requirements(REQUIREMENTS_FILE):
        try:
            version(name)
        except PackageNotFoundError:
            missing.append(name)
    return missing