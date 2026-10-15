DEFAULT_CLAUDE_MD = """# Инструкции проекта

Пиши здесь правила, которые агент должен соблюдать в этом проекте.
Например: язык общения, стиль кода, что не делать, важные пути.
"""

DEFAULT_MEMORY_MD = """# Индекс памяти

Список ссылок на файлы памяти. Агент читает их по требованию.
Пример строки:
- [auth system](memory/auth.md) — JWT, refresh tokens
"""

DEFAULT_CONFIG = {
    "model": "claude-sonnet-4-5",
    "max_iterations": 50,
    "lang": "en"
}
