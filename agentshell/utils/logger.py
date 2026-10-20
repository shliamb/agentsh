"""
Logger — file-only logging for the Agent Shell.

Usage:
    from utils.logger import log, setup
    
    setup(project_root)    # Call once in main()
    log.info("System started")
    log.error("Something broke")
"""
import logging
from pathlib import Path

LOGGER_NAME = "agentsh"
LOG_FILE = "agent.log"
LOG_DIR = "logs"
FMT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

# Предотвращает вывод в консоль, если setup() еще не вызван
logging.getLogger(LOGGER_NAME).addHandler(logging.NullHandler())


def setup(project_root: Path, *, level: int = logging.DEBUG) -> None:
    """Инициализация логгера. Вызывается один раз в main()."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    
    # Очищаем старые хендлеры (защита от дублей)
    logger.handlers.clear()
    
    formatter = logging.Formatter(FMT, datefmt=DATE_FMT)

    log_dir = project_root / ".agentshell" / LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Пишем только в файл. В консоль — ничего.
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