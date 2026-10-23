# /agentshell/bootstrap/bootstrap.py
import json
from pathlib import Path
from settings import PROJECT_DIR_NAME, GLOBAL_DIR, DEFAULT_CONFIG
from bootstrap.strings import DEFAULT_CLAUDE_MD, DEFAULT_MEMORY_MD
from typing import Optional
from utils.logger import log

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


class Bootstrap:
    """Manages the project environment: search, create, download config."""

    def __init__(self, cwd: Optional[Path] = None, lang_override: Optional[str]=None):
        """ cwd — where to look for the project. By default, it is the current directory. """
        self.lang_override = lang_override
        self.cwd = (cwd or Path.cwd()).resolve()
        self.root: Optional[Path] = None
        self.config: dict = {}


    def find_project_root(self) -> Optional[Path]:
        """ Goes from cwd up the tree, searches for the .agentshell/ folder.
            Returns the path to the root of the project, or None if not found.

            ~/.agentshell is the global config directory, not a project, so the
            home directory is never reported as a project root."""
        for parent in [self.cwd, *self.cwd.parents]:
            if parent / PROJECT_DIR_NAME == GLOBAL_DIR:
                continue  # this is the global config, not a project marker
            if (parent / PROJECT_DIR_NAME).is_dir():
                return parent
        return None


    def init(self) -> Path:
        """ Explicit project creation: agentsh init.
            If the project already exists, it's an error. (we don't touch the existing one)."""
        target = self.cwd / PROJECT_DIR_NAME
        if target.exists():
            text_error = f"The project already exists: {target}"
            log.error(text_error)
            raise FileExistsError(text_error)
        self._create_skeleton(self.cwd)
        if self.lang_override:
            self._update_config({"lang": self.lang_override})
        self.root = self.cwd
        return self.cwd


    def ensure_project(self) -> Path:
        """ Soft check: find a project or create one in the current folder.
            It is called during normal agent startup."""
        root = self.find_project_root()
        if root is None:
            root = self.cwd
            self._create_skeleton(root)
        self.root = root
        return root


    def _update_config(self, updates: dict) -> None:
        """ Update .agentshell/config.json (merge on top of the existing one). """
        cfg_path = self.cwd / PROJECT_DIR_NAME / "config.json"
        cfg = self._read_json(cfg_path) if cfg_path.exists() else {}
        cfg.update(updates)
        cfg_path.write_text(
            json.dumps(cfg, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    

    def load_config(self) -> dict:
        """ Loads the global config (~/.agentshell/config.json),
            then the project (.agentshell/config.json) on top.
            The result is saved in self.config and returned."""
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
        """ Priority: override > config > 'en'."""
        if self.lang_override:
            return self.lang_override
        cfg = self.load_config()
        if cfg.get("lang") in ("en", "ru"):
            return cfg["lang"]
        return "en"


    def _create_skeleton(self, root: Path) -> None:
        """ Creates an agentshell/ with a skeleton: CLAUDE.md , MEMORY.md , memory/, config.json."""
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
            text_error = f"I can't read it: {path}: {e}"
            log.error(text_error)
            raise RuntimeError(text_error)