#agentshell/main.py
import argparse
import sys
import time
import getpass
from pathlib import Path

from bootstrap.bootstrap import Bootstrap
from core.llm import LLM
from transport.terminal import TerminalTransport
from tools.toolsllm import ToolsLLM
from transport.ui import UI

from settings import VERSION, PROJECT_DIR_NAME
from dotenv import load_dotenv
from utils.logger import log, setup
from deps import is_in_venv, find_missing_deps
from keys import run_setup_keys




class AgentShellApp:
    """ """
    def __init__(self):
        self.user = getpass.getuser().capitalize()
        self.version = VERSION
        self.args = self._get_arg()

        self.start_time = time.time()
        self.tools_active_time = None
        self.ui = None
        self.config = None
        self.root = None

        # [LAYER 0: BOOTSTRAP]
        self.bootstrap = Bootstrap(
            cwd=self.args.project, 
            lang_override=self.args.lang
        )
        self.transport = None
        self.llm = None
        self.tools_llm = ToolsLLM()


    def run(self) -> int:
        return self._get_command()


    def _load_env(self) -> bool:
        """
        Load .env with fallback chain:
        1. <project_root>/.env
        2. ~/.agentshell/.env
        Returns True if any .env was loaded, False otherwise.
        """
        candidates = [
            self.root / ".env",
            Path.home() / ".agentshell" / ".env",
        ]
        for path in candidates:
            if path.exists():
                load_dotenv(path, override=True)
                log.info(f"Loaded env: {path}")
                return True
        return False


    def _get_arg(self):
        """ CLI argument parsing """
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
            version=f"agentshell {self.version}",
        )
        parser.add_argument(
            "--lang",
            choices=["en", "ru"],
            default=None,
            help="language: ru/en (overrides config)",
        )
        return parser.parse_args()


    def _get_command(self) -> int:
        """ Run bootstrap """
        if self.args.command == "init":
            return self.cmd_init()
        if self.args.command == "setup-keys":
            return self.cmd_setup_keys()
        if self.args.command == "help":
            print("Agent Shell — usage:")
            print("  agentshell init         Create a project skeleton in the current directory")
            print("  agentshell run          Start the agent (default)")
            print("  agentshell setup-keys   Configure API keys")
            print("  agentshell --help       Show standard CLI help")
            return 0
        return self.cmd_run()


    def cmd_init(self) -> int:
        """Create the .agentshell/ skeleton in the current folder.

        The logger is configured *after* the project check on purpose: setup()
        creates .agentshell/logs/, and that would make Bootstrap.init() think
        the project already exists."""
        existing = self.bootstrap.find_project_root()
        if existing:
            setup(project_root=existing)  # safe: .agentshell/ is already there
            errtext = f"Error: the project already exists: {existing / PROJECT_DIR_NAME}"
            print(errtext)
            log.error(errtext)
            return 1

        try:
            root = self.bootstrap.init()
        except FileExistsError as e:
            setup(project_root=self.bootstrap.cwd)
            errtext = f"Error: {e}"
            print(errtext)
            log.error(errtext)
            return 1

        setup(project_root=root)
        init_text = f"Project initialized: {root / PROJECT_DIR_NAME}"
        print(init_text)
        log.info(init_text)
        return 0


    @staticmethod
    def _fmt_time(seconds: float) -> str:
        """Human-friendly duration: '1m 23s' or '45.2s'."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        m, s = divmod(int(seconds), 60)
        return f"{m}m {s}s"


    @staticmethod
    def cmd_setup_keys() -> int:
        """Interactive API keys setup."""
        run_setup_keys()
        return 0
    

    def cmd_run(self) -> int:
        """Start the agent."""
        existing = self.bootstrap.find_project_root()
        if existing:
            self.bootstrap.root = existing

        #lang = self.bootstrap.resolve_lang()

        # 1. Check environment and dependencies
        if not is_in_venv():
            errtext = "Error: agentshell is not running inside its virtual environment.\nRun the installer: ./install.sh"
            print(errtext)
            log.error(errtext)
            return 1

        missing = find_missing_deps()
        if missing:
            errtext = f"Error: missing dependencies: {', '.join(missing)}.\nRun: ./install.sh"
            print(errtext)
            log.error(errtext)
            return 1

        self.root = self.bootstrap.ensure_project()
        setup(project_root=self.root)
        self.config = self.bootstrap.load_config()
        #lang = self.bootstrap.resolve_lang()

        # 2. Check API keys
        if not self._load_env():
            errtext = "Error: API keys not found. Please run: agentshell setup-keys"
            print(errtext)
            log.error(errtext)
            return 1

        # 3. Initialize Core and Transport
        self.llm = LLM(config=self.config, root=self.root, tools=self.tools_llm)
        self.transport = TerminalTransport()
        self.ui = UI(config=self.config, root=self.root)
        self.transport.get_obj_ui(self.ui)

        self.main_loop_agent()
        return 0


    def diagnostic_answer_llm(self, message, tools_calls, msg_obj):
        ######### ДИАГНОСТИКА ############
        # Если пришло что-то вообще без контента и без вызова тулзов, 
        # значит API вернул какую-то дичь или ошибку.
        if not message and not tools_calls:
            print("\n[WARNING] API вернул ответ без текста и без вызова инструментов.")
            print("Структура объекта message:")
            if hasattr(msg_obj, "__dict__"):
                print(vars(msg_obj))
            else:
                print(msg_obj)
            
            # Если это какая-то ошибка от LiteLLM, она может быть в скрытом поле
            if hasattr(msg_obj, "provider_specific_fields"):
                print("Provider specifics:", msg_obj.provider_specific_fields)


    def main_loop_agent(self):
        self.ui.logo_out_term()

        while True:
            """ Цикл ожидания ввода пользователя """


            """ [LAYER 1: TRANSPORT] Ожидание ввода User """
            user_question: str | None = self.transport.wait_input_term()
            if not user_question: continue
            if user_question == "!STOP": break

            request_start = time.time()

            while True:
                """ Рекурсия агента """

                """ [LAYER 2: CORE LLM] """
                answer_llm: dict = self.llm.chat(user_question)
                user_question = None

                try:
                    msg_obj = answer_llm.choices[0].message
                except (AttributeError, IndexError) as e:
                    print(f"\n[DEBUG API ERROR] Не могу достать message из ответа: {e}")
                    print(f"Сырой ответ: {answer_llm}")
                    break

                message = getattr(msg_obj, "content", None)
                reasoning_content = getattr(msg_obj, "reasoning_content", None)
                tools_calls = getattr(msg_obj, "tool_calls", None)

                ######### ДИАГНОСТИКА ВЫВОДА API LLM ############
                # self.diagnostic_answer_llm()
                ##################################

                if reasoning_content: self.ui.show_reasoning(reasoning_content)
                if message: self.ui.show_agent(message)
                if not tools_calls: break

                """ [LAYER 3: TOOLS LLM] """
                self.llm.send_tools(tools_calls)

            # --- Вывод времени запроса ---
            elapsed = time.time() - request_start
            self.ui.show_info(f"⏱️  Done in {self._fmt_time(elapsed)}")

        # --- Время всей сессии ---
        total = time.time() - self.start_time
        self.ui.show_info(f"\nSession total: {self._fmt_time(total)}")



def main() -> int:
    app = AgentShellApp()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())



