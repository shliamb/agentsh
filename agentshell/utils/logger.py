import logging
from pathlib import Path
from settings import LOGGER_NAME, LOG_FILE, LOG_DIR, FMT, DATE_FMT

"""
Logger — file logging for the Agent Shell.

Usage:
    from utils.logger import log, setup
    
    setup(project_root)    # Call once in main()
    log.info("System started")
    log.error("Something broke")
"""

# Prevents output to the console if setup() not called yet
logging.getLogger(LOGGER_NAME).addHandler(logging.NullHandler())


def setup(project_root: Path, *, level: int = logging.DEBUG) -> None:
    """Initializing the logger. Called once in main()."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    
    # Cleaning up old handlers (protection from duplicates)
    logger.handlers.clear()
    
    formatter = logging.Formatter(FMT, datefmt=DATE_FMT)

    log_dir = project_root / ".agentshell" / LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # We write only to the file. In the console, nothing.
    fh = logging.FileHandler(log_dir / LOG_FILE, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)


class _Log:
    _logger = logging.getLogger(LOGGER_NAME)

    def _emit(self, level: int, msg: str) -> None:
        self._logger.log(level, msg)

    def debug(self, msg: str) -> None:
        self._emit(logging.DEBUG, msg)

    def info(self, msg: str) -> None:
        self._emit(logging.INFO, msg)

    def warn(self, msg: str) -> None:
        self._emit(logging.WARNING, msg)

    def error(self, msg: str) -> None:
        self._emit(logging.ERROR, msg)


log = _Log()