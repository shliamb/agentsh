import sys
import re
import os
import getpass
import shutil
from settings import VERSION, MAIN_TEXTS

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


    def print_banner(self):
        
        CYAN = "\033[96m"
        DIM = "\033[2m"
        BOLD = "\033[1m"
        RESET = "\033[0m"
        
        version = self.version
        model = self.config.get('model', 'unknown')
        user = getpass.getuser().capitalize()
        
        welcome_txt = self.t(text=MAIN_TEXTS, lang=self.lang, key="banner.welcome", user=user)
        
        title = f" 💻 Agent Shell {DIM}v{version}{RESET} "
        title_clean = f" 💻 Agent Shell v{version} "
        
        # Строки контента (без ведущих пробелов, их добавит рамка)
        lines = [
            "",
            f"{BOLD}{welcome_txt}{RESET}",
            "",
            f"{DIM}Project:{RESET} {self.root_path}",
            f"{DIM}Model:  {RESET} {model}",
            ""
        ]
        
        clean_lines = [re.sub(r'\033\[[0-9;]*m', '', line) for line in lines]
        max_content_len = max(len(l) for l in clean_lines)
        
        # +1 к длине заголовка, так как эмодзи в терминале занимает 2 символа,
        # а len() в Python считает его за 1.
        title_len_visual = len(title_clean) + 1 
        
        width = max(max_content_len + 4, title_len_visual + 4, 40)
        
        title_fill = width - title_len_visual - 3
        print(f"{CYAN}╭─{title}{CYAN}{'─' * title_fill}╮{RESET}")
        
        for line, clean_line in zip(lines, clean_lines):
            pad = width - len(clean_line) - 3
            print(f"{CYAN}│{RESET} {line}{' ' * pad}{CYAN}│{RESET}")
            
        print(f"{CYAN}╰{'─' * (width - 2)}╯{RESET}")



    def cmd_exit(self) -> bool:
        print("До встречи.") if self.lang == "ru" else print("Bye.")
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
                text = input("\nagentshell > ")
                # Сброс флага, если начали вводить текст
                self.ctrl_c_pressed = False
                
            except EOFError:
                print("До встречи.") if self.lang == "ru" else print("Bye.")
                break
                
            except KeyboardInterrupt:
                if self.ctrl_c_pressed:
                    print("До встречи.") if self.lang == "ru" else print("Bye.")
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
