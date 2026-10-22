import getpass
from settings import VERSION
import os
os.system("")  # включает ANSI-цвета в cmd/PowerShell на Windows


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


class TerminalTransport:
    def __init__(self, config, root):
        self.version = VERSION
        self.config = config
        self.root_path = root
        self.ctrl_c_pressed = False
        self.user = getpass.getuser().capitalize()
        
        self.commands = {
            "/exit": self.cmd_exit,
            "/quit": self.cmd_exit,
            "/help": self.cmd_help,
            "/clear": self.cmd_clear,
        }

        self.green_bright = "\033[38;2;102;204;0m" # Яркий
        self.green_bright_rgb = (102, 204, 0)
        self.green_dark = "\033[38;2;50;100;0m"  # Темный
        self.green_dark_rgb = (50, 100, 0)
        self.reset = "\033[0m"

        # Череп 7x7, None = прозрачный пиксель
        self.skull = [
            [None,      "#CDC3BC", "#DCD4CD", "#D8D0C8", "#C8BEB7", "#AAA09A", None     ],
            ["#B9AFA8", "#D7CDC8", "#C8C0BA", "#AFA5A0", "#A59B96", "#7D736E", "#A59B96"],
            ["#B4AAA5", "#201614", "#1C1210", "#8C807A", "#281C1A", "#3E3430", "#9B918C"],
            ["#CDC3BE", "#322420", "#261C19", "#E0D6D0", "#241A18", "#2D201A", "#968C87"],
            ["#D8D0CA", "#DED6D0", "#BEB4AF", "#2A1E1C", "#BCB2AC", "#AAA09B", "#827873"],
            [None,      "#C8C0BA", "#D6CEC8", "#CDC5BE", "#827874", "#7D7370", None     ],
            [None,      "#F0EEEB", None,      "#E4DEDA", None,      "#A09C9B", None     ],
        ]

        # Узкий высокий шрифт: 3 пикселя в ширину (N - 4), 7 в высоту.
        self.font = {
            "A": [".#.", "#.#", "#.#", "###", "#.#", "#.#", "#.#"],
            "G": [".##", "#..", "#..", "#.#", "#.#", "#.#", ".##"],
            "E": ["###", "#..", "#..", "##.", "#..", "#..", "###"],
            "N": ["#..#", "##.#", "##.#", "#.##", "#.##", "#..#", "#..#"],
            "T": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", ".#."],
            "S": [".##", "#..", "#..", ".#.", "..#", "..#", "##."],
            "H": ["#.#", "#.#", "#.#", "###", "#.#", "#.#", "#.#"],
            "L": ["#..", "#..", "#..", "#..", "#..", "#..", "###"],
        }


    @staticmethod
    def _rgb(hex_color):
        return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))


    @staticmethod
    def _tint(rgb, tint):
        # перекрасить по яркости в оттенок tint
        lum = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        return tuple(int(c * lum) for c in tint)


    def _skull_canvas(self, tint):
        canvas = [[None] * 7]  # пустой ряд сверху -> 8 рядов = 4 строки терминала
        for row in self.skull:
            canvas.append([
                None if c is None
                else (self._tint(self._rgb(c), tint) if tint else self._rgb(c))
                for c in row
            ])
        return canvas


    def _text_canvas(self, word):
        rows = [[] for _ in range(8)]  # тот же холст 8 рядов, как у черепа
        for n, ch in enumerate(word):
            glyph = self.font[ch]
            for y in range(8):
                if n:
                    rows[y].append(None)  # промежуток между буквами
                if y == 0:
                    rows[y].extend([None] * len(glyph[0]))
                else:
                    # верхние 2 строки терминала - яркий, нижние 2 - тёмный
                    color = self.green_bright_rgb if y <= 3 else self.green_dark_rgb
                    rows[y].extend(color if c == "#" else None for c in glyph[y - 1])
        return rows


    def _render(self, canvas):
        # 2 пикселя по вертикали = 1 символ (▀ / ▄)
        lines = []
        for y in range(0, len(canvas), 2):
            line = ""
            for t, b in zip(canvas[y], canvas[y + 1]):
                if t and b:
                    line += (f"{self.reset}\033[38;2;{t[0]};{t[1]};{t[2]}m"
                             f"\033[48;2;{b[0]};{b[1]};{b[2]}m▀")
                elif t:
                    line += f"{self.reset}\033[38;2;{t[0]};{t[1]};{t[2]}m▀"
                elif b:
                    line += f"{self.reset}\033[38;2;{b[0]};{b[1]};{b[2]}m▄"
                else:
                    line += f"{self.reset} "
            lines.append("" + line + self.reset)
        return lines


    def build_logo(self, version, tint=None, gap=1):
        skull = self._render(self._skull_canvas(tint))        # 4 строки
        text = self._render(self._text_canvas("AGENTSHELL"))  # тоже 4 строки

        shade = f"{self.green_dark}░░{self.reset}"  # абстрактный штрих по краям
        lines = []
        for i, (s, t) in enumerate(zip(skull, text)):
            left = shade if i == 3 else "  "
            right = shade if i == 3 else ""
            if i == 0:
                right = f" {self.green_bright}v{version}{self.reset}"
            lines.append(" " + s + "" * gap + left + t + right)
        return "\n".join(lines)


    def logo_out_term(self):
        """ LOGO AGENT """        
        version = self.version
        model = self.config.get('model', 'unknown')
        logo = self.build_logo(version, tint=(102, 204, 0))  # череп в зелёной гамме
        out_text = (
            f"\n{logo}\n"
            f"{self.green_dark}  ────────────────────────────────────────────────{self.reset}\n"
            f"   {self.green_bright}Welcome back, {self.user}!\n"
            f"   Project: {self.root_path}\n"
            f"   Model: {model}{self.reset}\n"
        )
        print(out_text)


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
            text = input(f"\n{self.green_dark}You > {self.reset}")
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


    def render_reasoning(self, text: str):
        """Красиво выводит рассуждения модели, убирая пустые строки."""
        if not text:
            return
            
        GRAY = "\033[90m"
        RESET = "\033[0m"
        print(f"\n{GRAY}")
        
        # Разбиваем на строки, убираем лишние пробелы по краям
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Если строка пустая (была \n\n) — пропускаем её
            if not line:
                continue
                
            # Печатаем только непустые строки
            print(f"  │ {line}")
            
        print(f"{RESET}") # Отступ после блока мыслей