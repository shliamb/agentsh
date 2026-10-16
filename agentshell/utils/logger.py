"""
Тонкая обёртка над stdlib logging.

Использование:
    from utils.logger import log, setup

    setup(project_root=Path("/path/to/project"))   # один раз в main()
    log.info("проект найден")                      # в консоль + в файл
    log.info("много мусора", console=False)        # только в файл
    log.error("сломалось")                         # в консоль + в файл
"""
import logging
import sys
from pathlib import Path


LOGGER_NAME = "agentsh"
LOG_FILE = "agent.log"
LOG_DIR = "logs"
FMT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"


class _ConsoleFilter(logging.Filter):
    """Пропускает запись в консоль только если no_console=False."""
    def filter(self, record: logging.LogRecord) -> bool:
        return not getattr(record, "no_console", False)


def setup(project_root: Path, *, level: str = "DEBUG") -> None:
    """Инициализация. Вызывается один раз в main()."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(getattr(logging, level))
    logger.handlers.clear()
    formatter = logging.Formatter(FMT, datefmt=DATE_FMT)

    # Консоль
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    ch.addFilter(_ConsoleFilter())
    logger.addHandler(ch)

    # Файл
    log_dir = project_root / ".agentshell" / LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_dir / LOG_FILE, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)


class _Log:
    _logger = logging.getLogger(LOGGER_NAME)

    def _emit(self, level: int, msg: str, console: bool) -> None:
        self._logger.log(level, msg, extra={"no_console": not console})

    def debug(self, msg: str, console: bool = True) -> None:
        self._emit(logging.DEBUG, msg, console)

    def info(self, msg: str, console: bool = True) -> None:
        self._emit(logging.INFO, msg, console)

    def warn(self, msg: str, console: bool = True) -> None:
        self._emit(logging.WARNING, msg, console)

    def error(self, msg: str, console: bool = True) -> None:
        self._emit(logging.ERROR, msg, console)


log = _Log()



# log.info("проект найден")               # терминал + файл
# log.info("читаю 500 файлов", console=False)  # только файл
# log.error("упало")                      # терминал + файл