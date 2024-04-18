import asyncio

class Allocator:
    def __init__(self) -> None:
        sendtime = SendTime()
        sendtime.last_send_time=0

    async def run(self):
        while True:
            
            await asyncio.sleep(60)


class SendTime:
    def __init__(self) -> None:
        self.last_send_time = 0