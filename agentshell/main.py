#agentshell/main.py
import argparse
import sys
from pathlib import Path

from bootstrap.bootstrap import Bootstrap
from settings import VERSION, MAIN_TEXTS
from utils.logger import log, setup
from utils.common import t


"""
Agent Shell — точка входа.
Разбирает аргументы командной строки и вызывает нужный метод Bootstrap.
"""



def main() -> int:
    parser = argparse.ArgumentParser(
        prog="agentsh",
        description="Agent Shell — a terminal AI agent",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["init", "run"],
        default="run",
        help="command: init (create a project) or run (start the agent, default)",
    )
    parser.add_argument(
        "-p", "--project",
        type=Path,
        default=None,
        help="The path to the project folder (by default, the current one)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"agentshell {VERSION}",
    )
    parser.add_argument(
        "--lang",
        choices=["en", "ru"],
        default=None,
        help="language: ru/en (overrides config)",
    )

    args = parser.parse_args()

    bootstrap = Bootstrap(cwd=args.project, lang_override=args.lang)

    if args.command == "init":
        return cmd_init(bootstrap)

    return cmd_run(bootstrap)


def cmd_init(bootstrap: Bootstrap) -> int:
    """Создать скелет .agentshell/ в текущей папке."""
    # сначала найти существующий проект (если есть)
    existing = bootstrap.find_project_root() or bootstrap.cwd
    setup(project_root=existing) # инициализация log
    if existing:
        # проект уже есть — можно прочитать его язык
        bootstrap.root = existing
    lang = bootstrap.resolve_lang()
    try:
        root = bootstrap.init()
    except FileExistsError as e:
        log.error(t(text=MAIN_TEXTS, lang=lang, key="error.error", e=e))
        return 1
    log.info(t(text=MAIN_TEXTS, lang=lang, key="init.success", path=f"{root / '.agentshell'}"))
    return 0


def cmd_run(bootstrap: Bootstrap) -> int:
    """Запустить агента. Пока — заглушка."""
    root = bootstrap.ensure_project()
    setup(project_root=root) # инициализация log
    config = bootstrap.load_config()
    lang = bootstrap.resolve_lang()
    log.info(t(text=MAIN_TEXTS, lang=lang, key="agent.start"))
    log.info(t(text=MAIN_TEXTS, lang=lang, key="run.info", root=root, config=config))
    return 0


if __name__ == "__main__":
    sys.exit(main())
