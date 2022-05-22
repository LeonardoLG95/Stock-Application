import asyncio

from puller import Puller


async def start_puller():
    puller = Puller()
    await puller.start()
    puller.pull_tasks()
    await asyncio.gather(*asyncio.all_tasks())


asyncio.run(start_puller())
