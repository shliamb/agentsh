from core.loop import run_agent

class Router:
    def process(self, text: str) -> str:
        """Принимает текст, отдает в ядро, возвращает ответ."""
        return run_agent(text)
