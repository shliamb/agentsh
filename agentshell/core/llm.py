import json
import litellm
from pathlib import Path
from utils.logger import log

"""
Core Loop (L2) — the agent's brain.

Why it exists:
    This is where the actual "thinking" happens. It takes the user's text,
    sends it to the LLM, waits for a response, and (in the future) will 
    execute tools, observe the results, and repeat until the task is done.

Responsibilities:
    1. Build the prompt/context from the history and user input.
    2. Call the LLM (via LiteLLM).
    3. Parse the response. If it's a tool call, execute it (L3) and loop.
    4. If it's a final text answer, return it.

Boundaries:
    Knows NOTHING about the Terminal, the transport, or how the text is displayed.
    It just takes a `str`, does the hard work, and returns a `str`.
"""



class LLM:
    def __init__(self, config: dict, root: Path, tools, ask=None):
        self.config = config
        self.project_root = root
        self.model = config.get("model")
        self.tools_llm = tools
        self.messages = []
        self.past_messages = []

        # Human-in-the-loop channel (L1 injects it). L2 never imports a transport.
        self.ask = ask
        self.max_iterations = max(1, int(config.get("max_iterations") or 50))
        self.iterations = 0
        
        # Описание инструментов для LLM (формат OpenAI)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Execute a shell command in the terminal and return its output.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The shell command to execute."
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]
        
        self._load_system_prompt()


    @staticmethod
    def _error_net(text_err: str):
        """Заглушка для ошибок сети. Возвращает объект в формате ответа API, 
        чтобы основной код не сломался. Внутри будет текст ошибки вместо ответа модели."""
        from types import SimpleNamespace
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=text_err
                    )
                )
            ]
        )


    def _load_system_prompt(self):
        """Читает .agentshell/CLAUDE.md и добавляет в начало истории."""
        claude_md_path = self.project_root / ".agentshell" / "CLAUDE.md"
        system_content = "You are Agent Shell, a helpful terminal AI assistant. You can execute shell commands to solve tasks."
        
        if claude_md_path.exists():
            try:
                content = claude_md_path.read_text(encoding="utf-8").strip()
                if content:
                    system_content += f"\n\nProject rules:\n{content}"
            except Exception as e:
                log.error(f"Failed to read CLAUDE.md: {e}")

        # Первое сообщение всегда системное
        self.messages.append({"role": "system", "content": system_content})


    def recover_messages(self) -> None:
        """ Восстановление прошлого диалога """
        self.messages = self.past_messages.copy()
        return


    def _budget_allows_next_call(self) -> bool:
        """Check the per-turn work budget, asking the human when it runs out.

        Returns False when the human says no. With no ask channel the answer is
        also False: an unattended loop is exactly what the budget exists to
        prevent."""
        if self.iterations < self.max_iterations:
            return True

        if not self.ask:
            log.warn(f"Iteration budget exhausted ({self.max_iterations}), no ask channel")
            return False

        answer = self.ask(
            f"{self.iterations} iterations used. Continue?",
            ("y", "n"),
        )
        if str(answer).strip().lower() in ("y", "yes"):
            self.iterations = 0
            return True
        return False


    def chat(self, user_input: str = None) -> dict | None:
        """ Обращение к модели LLM.

        Returns None when the human stops the turn at the budget question."""
        if user_input:
            self.iterations = 0  # a new turn gets a fresh budget
        if not self._budget_allows_next_call():
            return None
        self.iterations += 1

        self.past_messages = self.messages.copy() # Копия диалога
        if user_input: self.messages.append({"role": "user", "content": user_input})

        try:
            response = litellm.completion(
                model=self.model,
                messages=self.messages,
                tools=self.tools
            )
            message = response.choices[0].message
            if message: self.messages.append(message.model_dump())
            return response

        except Exception as e:
            self.recover_messages() # Восстановление прошлого диалога
            log.error(f"LLM Error: {e}")
            return self._error_net(e)



    def execute_tool(self, tool_call) -> str:
        """ Execute one tool call, append its result to the history, return the result.

        The caller (main) shows both the call and the result; this layer never prints."""
        if tool_call.function.name == "run_command":
            try:
                args = json.loads(tool_call.function.arguments)
                command = args.get("command", "")

                # Выполняем
                result = self.tools_llm.execute(command)

            except Exception as e:
                # Если упало, пишем ошибку в результат для LLM
                result = f"Error executing command: {e}"
                log.error(f"Tool execution error: {e}")

        else:
            # Если LLM вызвала неизвестный инструмент, тоже нужно ответить
            result = f"Error: Unknown tool '{tool_call.function.name}'"

        # В любом случае (успех или ошибка) добавляем ответ в историю
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })
        return result