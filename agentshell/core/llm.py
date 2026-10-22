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
    Knows NOTHING about the Terminal, Router, or how the text is displayed.
    It just takes a `str`, does the hard work, and returns a `str`.
"""



class LLM:
    def __init__(self, config: dict, root: Path, tools):
        self.config = config
        self.project_root = root
        self.model = config.get("model")
        self.tools_llm = tools
        self.messages = []
        self.past_messages = []
        
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


    def chat(self, user_input: str = None) -> dict:
        """ Обращение к модели LLM """
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



    def send_tools(self, tools_calls: list) -> None:
        """ Обработка вызовов функций """
        for tool_call in tools_calls:
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

                # В любом случае (успех или ошибка) добавляем ответ в историю
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
            else:
                # Если LLM вызвала неизвестный инструмент, тоже нужно ответить
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": f"Error: Unknown tool '{tool_call.function.name}'"
                })