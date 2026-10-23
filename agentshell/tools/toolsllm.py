"""
L3 Tool: run_command.

Why it exists:
    This is the agent's "hand". It allows the LLM to execute shell commands.
    It takes a string, checks it against the security policy (L4), executes it 
    using subprocess, and returns a formatted string with the result.

Boundaries:
    Knows NOTHING about LLMs or the Core loop. It just executes what it's told.
"""
import subprocess
from pathlib import Path
from tools.subsystems.policy import Policy
from utils.logger import log



class ToolsLLM:
    """ ... """

    def __init__(self, root: Path | None = None):
        self.policy = Policy()
        self.root = root  # commands always run in the project root


    def execute(self, command: str) -> str:
        """
        Проверяет и выполняет команду.
        Возвращает строку с результатом (stdout + stderr + exit code).
        """

        # 1. Проверка безопасности (L4)
        result = self.policy.check(command)
        
        if result.decision.name == "DENY":
            log.warn(f"Blocked by policy: {command} | Reason: {result.reason}")
            return f"Error: Security policy denied execution. Reason: {result.reason}"

        # 2. Выполнение команды (L3)
        log.info(f"Executing command (cwd={self.root}): {command}")
        try:
            # shell=True позволяет использовать пайпы (|), редиректы (>) и т.д.
            # timeout=30 защищает от вечного зависания (например, если LLM вызовет `sleep 1000`)
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.root,
            )
            
            # 3. Форматируем вывод для LLM
            output = proc.stdout
            if proc.stderr:
                output += f"\n[stderr]\n{proc.stderr}"
                
            if not output.strip():
                output = "(no output)"

            #print(f"Exit code: {proc.returncode}\nOutput:\n{output}")
            return f"Exit code: {proc.returncode}\nOutput:\n{output}"
            
        except subprocess.TimeoutExpired:
            log.error(f"Command timed out: {command}")
            return "Error: Command timed out after 30 seconds."
        except Exception as e:
            log.error(f"Execution error: {e}")
            return f"Execution error: {e}"