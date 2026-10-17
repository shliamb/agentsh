# agentshell/settings.py
from pathlib import Path

VERSION = "0.1.0"
PROJECT_DIR_NAME = ".agentshell"
GLOBAL_DIR = Path.home() / PROJECT_DIR_NAME
REQUIREMENTS_FILE = Path(__file__).resolve().parent.parent / "requirements.txt"
ENV_FILE = GLOBAL_DIR / ".env"

# Переносится по умолчанию в 
# <project>/.agentshell/config.json
DEFAULT_CONFIG = {
    "model": "deepseek/deepseek-v4-flash",   # дефолтная модель, если ключ DeepSeek есть
    "default_provider": "deepseek",          # какой провайдер использовать по умолчанию
    "max_iterations": 50,
    "lang": "en",
}

LLM_PROVIDERS = [
    {"name": "deepseek",  "env_var": "DEEPSEEK_API_KEY",  "url": "https://platform.deepseek.com/api_keys"},
    {"name": "anthropic", "env_var": "ANTHROPIC_API_KEY", "url": "https://console.anthropic.com/settings/keys"},
    {"name": "openai",    "env_var": "OPENAI_API_KEY",    "url": "https://platform.openai.com/api-keys"},
    {"name": "gemini",    "env_var": "GEMINI_API_KEY",    "url": "https://aistudio.google.com/apikey"},
    {"name": "grok",      "env_var": "XAI_API_KEY",       "url": "https://console.x.ai/"},
]

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
        "error.not_in_venv": "Ошибка: agentsh запущен вне своего виртуального окружения.\nЗапусти установщик: ./install.sh",
        "error.missing_deps": "Ошибка: не установлены зависимости: {mods}.\nЗапусти: ./install.sh",
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
        "error.not_in_venv": "Error: agentsh is not running inside its virtual environment.\nRun the installer: ./install.sh",
        "error.missing_deps": "Error: missing dependencies: {mods}.\nRun: ./install.sh",
    },
}
