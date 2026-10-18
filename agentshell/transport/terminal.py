import asyncio

class TerminalTransport:

    def __init__(self, router):
        self.router = router
        self.out_queue = asyncio.Queue()      # Очередь: ядро -> терминал
        self.router.register_client(self.out_queue) # Регистрируемся в роутере


    async def read_input(self):
        """Чтение из терминала (в отдельном потоке, чтобы не вешать event loop)"""
        while True:
            try:
                # to_thread спасает от блокировки
                text = await asyncio.to_thread(input, "\nagentsh > ")
            except EOFError:
                self.router.stop()
                break
            except asyncio.CancelledError:
                break # Отмена при выходе

            cmd = text.strip()
            if not cmd:
                continue

            # Клиентские команды (не идут в ядро)
            if cmd == "/exit":
                print("Bye.")
                self.router.stop()
                break
            if cmd == "/help":
                print("Commands: /exit, /help")
                continue

            # Отправляем в роутер
            await self.router.in_queue.put(cmd)


    async def write_output(self):
        """Чтение из очереди ответов и вывод в консоль"""
        try:
            while True:
                text = await self.out_queue.get()
                print(f"\n{text}")
                self.out_queue.task_done()
        except asyncio.CancelledError:
            pass


    async def start(self):
        """Запуск двух задач: чтение и вывод"""
        read_task = asyncio.create_task(self.read_input())
        write_task = asyncio.create_task(self.write_output())
        
        # Ждем завершения ЛЮБОЙ из задач (например, ввода /exit)
        done, pending = await asyncio.wait(
            [read_task, write_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Отменяем вторую задачу, чтобы она не висела
        for task in pending:
            task.cancel()