import asyncio
import websockets

async def send():
    async with websockets.connect('ws://localhost:19190') as ws:
        await ws.send('victory')
        await asyncio.sleep(5)

asyncio.run(send())