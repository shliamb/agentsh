#agentshell/main.py
import argparse
import sys
from pathlib import Path
from bootstrap.bootstrap import Bootstrap
from transport.router import Router
from core.loop import Agent 
from transport.terminal import TerminalTransport
from settings import VERSION, MAIN_TEXTS
from dotenv import load_dotenv
from utils.logger import log, setup
from utils.common import t
from deps import is_in_venv, find_missing_deps


"""
Agent Shell — точка входа.
Разбирает аргументы командной строки и вызывает нужный метод Bootstrap.
"""



def main() -> int:
    """ Главный запуск + команды и аргументы в терминале"""
    parser = argparse.ArgumentParser(
        prog="agentshell",
        description="Agent Shell — a terminal AI agent",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["init", "run", "setup-keys", "help"],
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

    if args.command == "help":
        return print("instruction")

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
        print(t(text=MAIN_TEXTS, lang=lang, key="error.error", e=e))
        log.error(t(text=MAIN_TEXTS, lang=lang, key="error.error", e=e))
        return 1
    print(t(text=MAIN_TEXTS, lang=lang, key="init.success", path=f"{root / '.agentshell'}"))
    log.info(t(text=MAIN_TEXTS, lang=lang, key="init.success", path=f"{root / '.agentshell'}"))
    return 0



def cmd_run(bootstrap: Bootstrap) -> int:
    """Запустить агента."""
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


    # 1. Загружаем ключи из ~/.agentshell/.env
    env_path = Path.home() / ".agentshell" / ".env"
    load_dotenv(env_path)
    
    # 2. Инициализируем Агента (L2)
    print("Initializing LLM core...")
    log.info("Initializing LLM core...")
    agent = Agent(config=config, project_root=root)
    
    # 3. Передаем Агента в Роутер
    router = Router(agent=agent)

    terminal = TerminalTransport(
        router=router, 
        t_func=t, 
        lang=lang, 
        config=config, 
        root_path=root
    )
    terminal.start()

    return 0


def cmd_setup_keys() -> int:
    """Интерактивная настройка API-ключей."""
    from keys import run_setup_keys
    run_setup_keys()
    return 0



if __name__ == "__main__":
    sys.exit(main())
