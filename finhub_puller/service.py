import asyncio

from migration_handler import migration
from puller import Puller


async def start_puller():
    await migration()
    puller = Puller()
    await puller.start()
    puller.pull_tasks()
    await asyncio.gather(*asyncio.all_tasks())


asyncio.run(start_puller())
