import asyncio
from core.loop import run_agent

class Router:
    def __init__(self):
        self.in_queue = asyncio.Queue()   # Очередь: клиенты -> ядро
        self.clients = []                 # Список очередей клиентов (терминал, телеграм)
        self.running = True

    def register_client(self, client_out_queue: asyncio.Queue):
        """Клиент (терминал) регистрирует свою очередь для получения ответов"""
        self.clients.append(client_out_queue)

    async def broadcast(self, text: str):
        """Разослать ответ всем подключенным клиентам"""
        for q in self.clients:
            await q.put(text)

    async def start(self):
        """Главный цикл обработки входящих сообщений"""
        print("[Router] Запущен и ждет сообщений...")
        while self.running:
            try:
                # Ждем сообщение, но с таймаутом, чтобы проверять флаг running
                text = await asyncio.wait_for(self.in_queue.get(), timeout=0.5)
                
                # Отдаем в ядро (L2)
                response = await run_agent(text)
                
                # Рассылаем ответ всем
                await self.broadcast(response)
                self.in_queue.task_done()
            except asyncio.TimeoutError:
                continue

    def stop(self):
        self.running = False