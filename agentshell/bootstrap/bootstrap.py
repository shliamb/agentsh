# /agentshell/bootstrap/bootstrap.py
import os
import json
from pathlib import Path
from constants import PROJECT_DIR_NAME, GLOBAL_DIR
from bootstrap.constants import DEFAULT_CLAUDE_MD, DEFAULT_MEMORY_MD, DEFAULT_CONFIG
from typing import Optional


"""
Bootstrap — подготовка окружения агента.

Что делает:
  1. Находит корень проекта (папку с .agentshell/) вверх по дереву.
  2. Если проекта нет — может создать (ensure) или создать явно (init).
  3. Загружает конфиг: глобальный (~/.agentshell/) + проектный (.agentshell/).
     Проектный переопределяет глобальный.

Правило: Bootstrap ничего не знает про LLM, тулы, policy. Только файлы и папки.

agentsh --version
agentsh --help
agentsh init            # создать проект
agentsh                 # должен найти проект и напечатать конфиг
run                     # запустить агента (пока заглушка — просто печатает «агент запущен»).

"""


class Bootstrap:
    """Управляет окружением проекта: поиск, создание, загрузка конфига."""

    def __init__(self, cwd: Optional[Path] = None, lang_override: Optional[str]=None):
        """
        cwd — откуда искать проект. По умолчанию — текущая директория.
        """
        self.lang_override = lang_override
        self.cwd = (cwd or Path.cwd()).resolve()
        self.root: Optional[Path] = None
        self.config: dict = {}

    def find_project_root(self) -> Optional[Path]:
        """
        Идёт от cwd вверх по дереву, ищет папку .agentshell/.
        Возвращает путь к корню проекта или None, если не нашёл.
        """
        for parent in [self.cwd, *self.cwd.parents]:
            if (parent / PROJECT_DIR_NAME).is_dir():
                return parent
        return None

    def init(self) -> Path:
        """
        Явное создание проекта: agentsh init.
        Если проект уже есть — ошибка (не трогаем существующее).
        """
        target = self.cwd / PROJECT_DIR_NAME
        if target.exists():
            raise FileExistsError(f"Проект уже инициализирован: {target}")
        self._create_skeleton(self.cwd)
        if self.lang_override:
            self._update_config({"lang": self.lang_override})
        self.root = self.cwd
        return self.cwd

    def ensure_project(self) -> Path:
        """
        Мягкая проверка: найти проект или создать в текущей папке.
        Вызывается при обычном запуске агента.
        """
        root = self.find_project_root()
        if root is None:
            root = self.cwd
            self._create_skeleton(root)
        self.root = root
        return root


    def _update_config(self, updates: dict) -> None:
        """Обновить .agentshell/config.json (мерж поверх существующего)."""
        cfg_path = self.cwd / PROJECT_DIR_NAME / "config.json"
        cfg = self._read_json(cfg_path) if cfg_path.exists() else {}
        cfg.update(updates)
        cfg_path.write_text(
            json.dumps(cfg, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    

    def load_config(self) -> dict:
        """
        Грузит глобальный конфиг (~/.agentshell/config.json),
        затем проектный (.agentshell/config.json) поверх.
        Итог сохраняется в self.config и возвращается.
        """
        config: dict = {}

        global_cfg = GLOBAL_DIR / "config.json"
        if global_cfg.exists():
            config.update(self._read_json(global_cfg))

        if self.root:
            proj_cfg = self.root / PROJECT_DIR_NAME / "config.json"
            if proj_cfg.exists():
                config.update(self._read_json(proj_cfg))

        self.config = config
        return config

    def resolve_lang(self) -> str:
        """Приоритет: override > config > 'en'."""
        if self.lang_override:
            return self.lang_override
        cfg = self.load_config()
        if cfg.get("lang") in ("en", "ru"):
            return cfg["lang"]
        return "en"

    def _create_skeleton(self, root: Path) -> None:
        """Создаёт .agentshell/ со скелетом: CLAUDE.md, MEMORY.md, memory/, config.json."""
        d = root / PROJECT_DIR_NAME
        d.mkdir(exist_ok=True)
        (d / "memory").mkdir(exist_ok=True)

        if not (d / "CLAUDE.md").exists():
            (d / "CLAUDE.md").write_text(DEFAULT_CLAUDE_MD, encoding="utf-8")

        if not (d / "MEMORY.md").exists():
            (d / "MEMORY.md").write_text(DEFAULT_MEMORY_MD, encoding="utf-8")

        if not (d / "config.json").exists():
            (d / "config.json").write_text(
                json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    @staticmethod
    def _read_json(path: Path) -> dict:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise RuntimeError(f"Не могу прочитать {path}: {e}")