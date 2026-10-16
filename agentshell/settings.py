# agentshell/settings.py
from pathlib import Path

VERSION = "0.1.0"
PROJECT_DIR_NAME = ".agentshell"
GLOBAL_DIR = Path.home() / PROJECT_DIR_NAME

DEFAULT_CONFIG = {
    "model": "claude-sonnet-4-5",
    "max_iterations": 50,
    "lang": "en",
}


MAIN_TEXTS = {
    "ru": {
        "agent.start": "Агент запущен",
        "error.error": "{e}",
        "init.success": "Проект инициализирован: {path}",
        "init.project_exists": "Проект уже существует: {path}",
        "error.cantread": "Не могу прочитать: {path}: {e}",
        "run.info": (
            "Проект: {root}\n"
            "Конфиг: {config}\n"
            "Агент запущен (заглушка). Основная логика — в L2."
        ),
    },
    "en": {
        "agent.start": "agent started",
        "error.error": "{e}",
        "init.success": "Project initialized: {path}",
        "init.project_exists": "The project already exists: {path}",
        "error.cantread": "I can't read it: {path}: {e}",
        "run.info": (
            "Project: {root}\n"
            "Config: {config}\n"
            "The agent is running (placeholder). The main logic is in L2."
        ),
    },
}
