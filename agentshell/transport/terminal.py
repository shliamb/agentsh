import getpass


"""
Terminal — command-line interface (CLI) transport.

Why it exists:
    This is the first (and currently only) way for the user to talk to the agent.
    It handles terminal input, prints output, and intercepts local slash-commands.

Boundaries:
    This file knows NOTHING about LLMs or the Core. It doesn't care what the agent 
    does with the text. It just takes your input, hands it to the core, 
    and prints whatever comes back.

Flow:
    User -> input() -> [check local commands like /exit] -> Core -> print() -> User

Note: 
    Later, we will add `telegram.py` and `web.py` with the exact same interface.
    The Core will never know the difference.
"""


class TerminalTransport:
    def __init__(self):
        self.ctrl_c_pressed = False
        self.user = getpass.getuser().capitalize()
        self.ui = None
        
        self.commands = {
            "/exit": self.cmd_exit,
            "/quit": self.cmd_exit,
            "/help": self.cmd_help,
            "/clear": self.cmd_clear,
        }


    def get_obj_ui(self, obj):
        self.ui = obj
        return


    def cmd_exit(self) -> str:
        print(f"Bye {self.user}.")
        return "!STOP"


    def cmd_help(self) -> bool:
        print("Commands:")
        for cmd in self.commands:
            print(f"  {cmd}")
        return True


    def cmd_clear(self) -> bool:
        print("\033[H\033[J", end="")
        return True


    def wait_input_term(self) -> str | None:
        """ """
        try:
            text = input(self.ui.show_user())
            # Сброс флага, если начали вводить текст
            self.ctrl_c_pressed = False
            
        except EOFError:
            # Нужно вылавливать для прерывания
            return "!STOP"
  
        except KeyboardInterrupt:
            if self.ctrl_c_pressed:
                # Нужно вылавливать для прерывания
                return "!STOP"
            
            else:
                # будет специальная возможность отправлять на вывод отдельно
                print("\n(Press Ctrl+C again to exit, or type /exit)")
                self.ctrl_c_pressed = True
                return

        cmd = text.strip()
        if not cmd:
            print("Введите команду или вопрос") # переведи на английский
            return 

        if cmd.startswith("/"):
            handler: bool | str = self.commands.get(cmd)
            if handler:
                should_continue = handler()
                if not should_continue:
                    print("Нет такой команды попробуйте снова") # переведи на английский
                    return
                elif should_continue == "!STOP":
                    return "!STOP"
                return
            else:
                # будет специальная возможность отправлять на вывод отдельно
                print(f"Unknown command: {cmd}. Type /help for list.")
                return

        return text
