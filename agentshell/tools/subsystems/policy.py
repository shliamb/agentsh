"""
L4 Policy — решает, можно ли выполнять команду в терминале.
Класс позволяет легко расширять правила и добавлять новые проверки.
"""
from dataclasses import dataclass
from enum import Enum
import re


class Decision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"   # задел на будущее


@dataclass
class Result:
    decision: Decision
    reason: str = ""


class Policy:
    def __init__(self):
        # Каждое правило: (regex, причина отказа)
        self.rules = [
            (r"\.env\b",        "access to .env is denied"),
            (r"\.ssh\b",        "access to .ssh is denied"),
            (r"\.aws\b",        "access to .aws is denied"),
            (r"\.pem\b",        "access to .pem keys is denied"),
            (r"id_rsa",         "access to an SSH key is denied"),
            (r"rm\s+-rf\s+/",   "recursive delete of a root path is denied"),
            (r"rm\s+-rf\s+~",   "recursive delete of the home directory is denied"),
        ]

    def check(self, command: str) -> Result:
        """
        Главный метод проверки. Проходит по всем правилам.
        """
        # 1. Проверка по базовым паттернам (regex)
        regex_result = self._check_regex_rules(command)
        if regex_result.decision == Decision.DENY:
            return regex_result

        # 2. Сюда мы потом добавим другие проверки:
        # path_result = self._check_paths(command)
        # net_result = self._check_network(command)

        return Result(Decision.ALLOW)

    def _check_regex_rules(self, command: str) -> Result:
        """Внутренний метод: проверка по списку регулярных выражений."""
        for pattern, reason in self.rules:
            if re.search(pattern, command):
                return Result(Decision.DENY, reason)
        return Result(Decision.ALLOW)









# from dataclasses import dataclass
# from enum import Enum
# import re
# from utils.logger import log


# """
# L4 Policy — решает, можно ли выполнять команду в терминале.
# Пока тупо: regex по строке. Позже — парсинг argv.
# """

# class Decision(Enum):
#     ALLOW = "allow"
#     DENY = "deny"
#     ASK = "ask"   # задел на будущее, пока не используется


# @dataclass
# class Result:
#     decision: Decision
#     reason: str = ""


# # Каждое правило: (regex, причина отказа)
# # Проверяются по очереди. Первое сработавшее — стоп.
# RULES = [
#     (r"\.env\b",        "доступ к .env запрещён"),
#     (r"\.ssh\b",        "доступ к .ssh запрещён"),
#     (r"\.aws\b",        "доступ к .aws запрещён"),
#     (r"\.pem\b",        "доступ к .pem запрещён"),
#     (r"id_rsa",         "доступ к ssh-ключу запрещён"),
#     (r"rm\s+-rf\s+/",   "рекурсивное удаление корня запрещено"),
#     (r"rm\s+-rf\s+~",   "рекурсивное удаление домашней папки запрещено"),
# ]


# def check(command: str) -> Result:
#     """
#     Проверить команду. Возвращает Result с решением.
#     Пока — простой поиск по regex.
#     """
#     for pattern, reason in RULES:
#         if re.search(pattern, command):
#             return Result(Decision.DENY, reason)
#     return Result(Decision.ALLOW)