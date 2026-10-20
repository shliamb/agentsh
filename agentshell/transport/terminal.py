"""
Terminal — command-line interface (CLI) transport.

Why it exists:
    This is the first (and currently only) way for the user to talk to the agent.
    It handles terminal input, prints output, and intercepts local slash-commands.

Boundaries:
    This file knows NOTHING about LLMs or the Core. It doesn't care what the agent 
    does with the text. It just takes your input, sends it to the Router, 
    and prints whatever the Router gives back.

Flow:
    User -> input() -> [check local commands like /exit] -> Router.process() -> print() -> User

Note: 
    Later, we will add `telegram.py` and `web.py` with the exact same interface.
    The Core will never know the difference.
"""

import getpass
from settings import VERSION

class TerminalTransport:
    def __init__(self, router, t_func, lang, config, root_path):
        self.version = VERSION
        self.router = router
        self.t = t_func
        self.lang = lang
        self.config = config
        self.root_path = root_path
        self.ctrl_c_pressed = False
        
        self.commands = {
            "/exit": self.cmd_exit,
            "/quit": self.cmd_exit,
            "/help": self.cmd_help,
            "/clear": self.cmd_clear,
        }

        self.green_bright = "\033[38;2;102;204;0m" # Яркий
        self.green_dark = "\033[38;2;50;100;0m"  # Темный
        self.reset = "\033[0m"


    def print_banner(self):
        """ LOGO AGENT """        
        version = self.version
        model = self.config.get('model', 'unknown')
        user = getpass.getuser().capitalize()
        logo = (
            f"{self.green_bright}    ▄▀█ █▀▀ █▀▀ █▄░█ ▀█▀ █▀ █░█ █▀▀ █░░ █░░ v{version}{self.reset}\n"
            f"{self.green_dark}  ░░█▀█ █▄█ ██▄ █░▀█ ░█░ ▄█ █▀█ ██▄ █▄▄ █▄▄░░ {self.reset}"
        )
        out_text = (
            f"\n{logo}\n"
            f"{self.green_dark}    ───────────────────────────────────────{self.reset}\n"
            f"    {self.green_bright}Welcome back, {user}!\n"
            f"    Project: {self.root_path}\n"
            f"    Model: {model}{self.reset}\n"
        )
        print(out_text)





    def cmd_exit(self) -> bool:
        print("Bye.")
        return False


    def cmd_help(self) -> bool:
        print("Commands:")
        for cmd in self.commands:
            print(f"  {cmd}")
        return True


    def cmd_clear(self) -> bool:
        print("\033[H\033[J", end="")
        return True


    def start(self):
        self.print_banner()
        
        while True:
            try:
                text = input(f"\n{self.green_dark}You > {self.reset}")
                # Сброс флага, если начали вводить текст
                self.ctrl_c_pressed = False
                
            except EOFError:
                print("Bye.")
                break
                
            except KeyboardInterrupt:
                if self.ctrl_c_pressed:
                    print("Bye.")
                    break
                else:
                    print("\n(Press Ctrl+C again to exit, or type /exit)")
                    self.ctrl_c_pressed = True
                    continue

            cmd = text.strip()
            if not cmd:
                continue

            if cmd.startswith("/"):
                handler = self.commands.get(cmd)
                if handler:
                    should_continue = handler()
                    if not should_continue:
                        break
                else:
                    print(f"Unknown command: {cmd}. Type /help for list.")
                continue

            response = self.router.process(cmd)
            print(f"\n{response}")
