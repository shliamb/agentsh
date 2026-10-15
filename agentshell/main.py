#agentshell/main.py
import argparse
import sys
from pathlib import Path

from bootstrap.bootstrap import Bootstrap
from config import VERSION


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

    if args.command == "run":
        return cmd_run(bootstrap)


def msg(key: str, lang: str, **kw) -> str:
    """Заглушка i18n. Позже — словари."""
    table = {
        "error.project_exists": {"ru": "Ошибка: {err}", "en": "Error: {err}"},
        "init.success": {"ru": "Проект инициализирован: {path}", "en": "Project initialized: {path}"},
    }
    return table[key][lang].format(**kw)


def cmd_init(bootstrap: Bootstrap) -> int:
    """Создать скелет .agentshell/ в текущей папке."""
    # сначала найти существующий проект (если есть)
    existing = bootstrap.find_project_root()
    if existing:
        # проект уже есть — можно прочитать его язык
        bootstrap.root = existing
    lang = bootstrap.resolve_lang()
    try:
        root = bootstrap.init()
    except FileExistsError as e:
        print(msg(key="error.project_exists", lang=lang, err=e))
        return 1
    print(msg(key="init.success", lang=lang,  path=f"{root / '.agentshell'}"))
    return 0


def cmd_run(bootstrap: Bootstrap) -> int:
    """Запустить агента. Пока — заглушка."""
    root = bootstrap.ensure_project()
    config = bootstrap.load_config()
    lang = bootstrap.resolve_lang()
    print(f"Проект: {root}") if lang == "ru" else print(f"Project: {root}")
    print(f"Конфиг: {config}") if lang == "ru" else print(f"Config: {config}")
    print("Агент запущен (заглушка). Основная логика — в L2.") if lang == "ru" else print("The agent is running (placeholder). The main logic is in L2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
