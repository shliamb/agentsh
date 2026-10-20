# /agentshell/bootstrap/bootstrap.py
"""
Bootstrap — project environment and configuration setup.

Why it exists:
    Before the agent starts thinking or executing tools, it needs to know 
    WHERE it is and HOW it should behave. Bootstrap handles the pre-flight checks.

Responsibilities:
    1. Find the project root (looks for a `.agentshell/` folder up the directory tree).
    2. Create the project skeleton (`init`) if it doesn't exist.
    3. Load configuration (merges global `~/.agentshell/config.json` with local project config).
    4. Resolve the current language (CLI flag -> config -> default).

Boundaries:
    Knows NOTHING about LLMs, tools, or the Core loop. 
    It only deals with files, paths, and JSON.

Flow:
    main() -> Bootstrap.ensure_project() -> Bootstrap.load_config() -> start agent.
"""

import os
import json
from pathlib import Path
from settings import PROJECT_DIR_NAME, GLOBAL_DIR, DEFAULT_CONFIG, MAIN_TEXTS
from bootstrap.strings import DEFAULT_CLAUDE_MD, DEFAULT_MEMORY_MD
from typing import Optional
from utils.logger import log
from utils.common import t


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
            text_error = t(text=MAIN_TEXTS, lang=self.lang_override, key="init.project_exists", path=target)
            log.error(text_error, console=False)
            raise FileExistsError(text_error)
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

    def _read_json(self, path: Path) -> dict:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            text_error = t(text=MAIN_TEXTS, lang=self.lang_override, key="error.cantread", path=path, e=e)
            log.error(text_error, console=False)
            raise RuntimeError(text_error)