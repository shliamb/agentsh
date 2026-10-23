import getpass
from settings import VERSION
import os
os.system("")  # включает ANSI-цвета в cmd/PowerShell на Windows


"""
UI — Unified User Interface.

Why it exists:
    Centralizes all terminal output. Layers (Main, Core, Tools) should NOT 
    use print() directly. They call UI methods. Later, we can create a 
    TelegramUI or WebUI with the same methods, and the rest of the app 
    won't need to change.
"""



class UI:

    # ANSI Colors
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    def __init__(self, config, root):

        self.green_bright = "\033[38;2;102;204;0m" # Яркий
        self.green_bright_rgb = (102, 204, 0)
        self.green_dark = "\033[38;2;50;100;0m"  # Темный
        self.green_dark_rgb = (50, 100, 0)
        self.reset = "\033[0m"

        self.version = VERSION
        self.config = config
        self.root_path = root
        self.user = getpass.getuser().capitalize()

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


    def show_reasoning(self, text: str):
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

    def show_user(self):
        """Показывает ввод пользователя"""
        return(f"{self.BOLD}YOU:{self.RESET} ")

    def show_agent(self, text: str):
        """Выводит финальный ответ агента."""
        if text:
            print(f"\n{self.BOLD}AGENT:{self.RESET} {text}\n")

    def show_tool_start(self, tool_name: str, args: str):
        """Выводит начало выполнения команды."""
        print(f"{self.YELLOW}🛠️  Running [{tool_name}]: {args}{self.RESET}")

    def show_tool_result(self, result: str):
        """Выводит результат команды (можно обрезать, если очень длинно)."""
        # Пока выводим как есть, позже сделаем умную обрезку
        print(f"{self.GRAY}{result}{self.RESET}")

    def show_error(self, text: str):
        """Выводит сообщение об ошибке."""
        print(f"\n{self.RED}{text}{self.RESET}\n")

    def show_info(self, text: str):
        """Выводит системное сообщение."""
        print(f"{self.DIM}{text}{self.RESET}")





# show_user_input(text) — красиво выделяет твой ввод.

# show_agent_response(text) — выводит финальный ответ модели.

# show_reasoning(text) — выводит мысли (тот код с │, который мы сделали).

# show_tool_start(name, args) — выводит 🛠️ Executing: ls -la.

# show_tool_result(output) — выводит результат команды.

# show_error(text) — выводит красную ошибку.