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
import json
import litellm
from pathlib import Path
from utils.logger import log
from tools.run_command import execute as execute_command

class Agent:
    def __init__(self, config: dict, project_root: Path):
        self.config = config
        self.project_root = project_root
        self.model = config.get("model")
        
        # История диалога
        self.messages = []
        
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


    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        # Защита от бесконечного цикла (если LLM затупит)
        # 5 шагов — это более чем достаточно для одной задачи в MVP.
        max_iterations = 5
        
        for iteration in range(max_iterations):
            try:
                # Отправляем историю и список тулов в LLM
                response = litellm.completion(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tools
                )
                
                message = response.choices[0].message
                
                # Добавляем ответ LLM в историю (даже если это просто запрос на тул)
                self.messages.append(message.model_dump())

                # Если LLM НЕ просит вызвать тул — значит, это финальный ответ
                if not message.tool_calls:
                    return message.content

                # Если просит — выполняем ВСЕ запрошенные тулы (их может быть несколько)
                for tool_call in message.tool_calls:
                    if tool_call.function.name == "run_command":
                        args = json.loads(tool_call.function.arguments)
                        command = args.get("command", "")
                        
                        # Вызов L3 (внутри него сработает L4)
                        result = execute_command(command)
                        
                        # Отправляем результат выполнения обратно в LLM
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result
                        })
            
            except Exception as e:
                # Если произошла ошибка API, откатываем последнее сообщение пользователя
                self.messages.pop() 
                log.error(f"LLM Error: {e}")
                return f"[Error] LLM failure: {e}"
                
        return f"[Error] Agent reached maximum iterations ({max_iterations}) without finishing the task."