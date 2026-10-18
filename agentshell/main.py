#agentshell/main.py
import asyncio
import argparse
import sys
import os
from pathlib import Path

from bootstrap.bootstrap import Bootstrap
from transport.router import Router
from transport.terminal import TerminalTransport
from settings import VERSION, MAIN_TEXTS
from utils.logger import log, setup
from utils.common import t
from deps import is_in_venv, find_missing_deps


"""
Agent Shell — точка входа.
Разбирает аргументы командной строки и вызывает нужный метод Bootstrap.
"""



def main() -> int:
    parser = argparse.ArgumentParser(
        prog="agentshell",
        description="Agent Shell — a terminal AI agent",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["init", "run", "setup-keys"],
        default="run",
        help="command: init (create a project) | run (start the agent, default) | setup-keys",
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

    if args.command == "setup-keys":
        return cmd_setup_keys()

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


async def async_main():
    router = Router()
    terminal = TerminalTransport(router)

    # Запускаем Роутер в фоне
    router_task = asyncio.create_task(router.start())
    
    # Запускаем Терминал (он ждет ввода)
    await terminal.start()
    
    # Когда терминал закрылся (/exit), останавливаем роутер
    router.stop()
    await router_task


def cmd_run(bootstrap: Bootstrap) -> int:
    """Запустить агента. Пока — заглушка."""
    existing = bootstrap.find_project_root()
    if existing:
        bootstrap.root = existing
    lang = bootstrap.resolve_lang()

    if not is_in_venv():
        print(t(text=MAIN_TEXTS, lang=lang, key="error.not_in_venv"), file=sys.stderr)
        return 1

    missing = find_missing_deps()
    if missing:
        print(
            t(text=MAIN_TEXTS, lang=lang, key="error.missing_deps", mods=", ".join(missing)),
            file=sys.stderr,
        )
        return 1

    root = bootstrap.ensure_project()
    setup(project_root=root) # инициализация log
    config = bootstrap.load_config()
    lang = bootstrap.resolve_lang()
    log.info(t(text=MAIN_TEXTS, lang=lang, key="agent.start"))
    log.info(t(text=MAIN_TEXTS, lang=lang, key="run.info", root=root, config=config))


    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nBye.")
        os._exit(0) # Принудительный выход, чтобы не ждать зависший input()
    return 0


def cmd_setup_keys() -> int:
    """Интерактивная настройка API-ключей."""
    from keys import run_setup_keys
    run_setup_keys()
    return 0



if __name__ == "__main__":
    sys.exit(main())
