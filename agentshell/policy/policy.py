from dataclasses import dataclass
from enum import Enum
import re
from utils.logger import log


"""
L4 Policy — решает, можно ли выполнять команду в терминале.
Пока тупо: regex по строке. Позже — парсинг argv.
"""

class Decision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"   # задел на будущее, пока не используется


@dataclass
class Result:
    decision: Decision
    reason: str = ""


# Каждое правило: (regex, причина отказа)
# Проверяются по очереди. Первое сработавшее — стоп.
RULES = [
    (r"\.env\b",        "доступ к .env запрещён"),
    (r"\.ssh\b",        "доступ к .ssh запрещён"),
    (r"\.aws\b",        "доступ к .aws запрещён"),
    (r"\.pem\b",        "доступ к .pem запрещён"),
    (r"id_rsa",         "доступ к ssh-ключу запрещён"),
    (r"rm\s+-rf\s+/",   "рекурсивное удаление корня запрещено"),
    (r"rm\s+-rf\s+~",   "рекурсивное удаление домашней папки запрещено"),
]


def check(command: str) -> Result:
    """
    Проверить команду. Возвращает Result с решением.
    Пока — простой поиск по regex.
    """
    for pattern, reason in RULES:
        if re.search(pattern, command):
            return Result(Decision.DENY, reason)
    return Result(Decision.ALLOW)